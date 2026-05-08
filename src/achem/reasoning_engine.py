"""Research Reasoning Engine — AI-powered synthesis of findings (Stage 4)."""

import json
import logging
import re
from typing import List, Dict, Optional

from .config_manager import ConfigManager


REASONING_SYSTEM_PROMPT = """You are a senior intelligence analyst producing a structured research brief.

Given a research topic and numbered source material, produce a concise synthesis.

Output ONLY valid JSON with this exact structure:
{
  "summary": "2-3 paragraph synthesis of the key findings",
  "key_findings": ["finding 1 [1]", "finding 2 [2][3]", "finding 3 [4]"],
  "themes": ["theme 1", "theme 2"],
  "contradictions": ["notable disagreement or conflict between sources, or 'None identified'"],
  "confidence_level": "high/medium/low based on source quality and consistency"
}

RULES:
- Base everything on the provided sources only
- CRITICAL: After each key finding, cite the source reference number(s) in brackets like [1] or [2][3]
- Every key finding MUST cite at least one source number
- If sources conflict, note it in contradictions
- Use the SAME LANGUAGE as the user's topic
- Output ONLY valid JSON — no explanations, no markdown"""


async def synthesize_findings(
    articles: List[Dict],
    scraped: List[Dict],
    references: List[Dict],
    topic: str,
    language: str = "en",
    model: Optional[str] = None,
) -> Dict:
    """Synthesize collected sources into a structured research brief with citations.

    Args:
        articles: Merged deduplicated articles from Stage 3 (with ref_id)
        scraped: Raw scraped content
        references: List of {ref_id, title, url} for the source table
        topic: Original research topic
        language: Output language
        model: OpenRouter model override

    Returns:
        Dict with keys: summary, key_findings, themes, contradictions,
                        confidence_level, references (with cited flags)
    """
    config = ConfigManager()
    api_key = config.get_openrouter_api_key()
    has_api = api_key and len(api_key) >= 10

    if not articles:
        return {
            "summary": "No sources available for synthesis.",
            "key_findings": [],
            "themes": [],
            "contradictions": [],
            "confidence_level": "low",
            "references": references or [],
        }

    if has_api:
        try:
            result = await _ai_synthesis(articles, scraped, references, topic, language, model)
            if result:
                return result
        except Exception as e:
            logging.warning(f"AI synthesis failed, falling back to local: {e}")

    return _local_synthesis(articles, references, topic)


async def _ai_synthesis(
    articles: List[Dict],
    scraped: List[Dict],
    references: List[Dict],
    topic: str,
    language: str = "en",
    model: Optional[str] = None,
) -> Optional[Dict]:
    """Call OpenRouter for structured AI synthesis with citation tracking."""
    import aiohttp

    config = ConfigManager()
    api_key = config.get_openrouter_api_key()
    model_name = model or config.get_openrouter_model() or "google/gemma-4-31b-it:free"

    source_blocks = []
    for a in articles[:20]:
        ref_id = a.get("ref_id", 0)
        title = a.get("title", "Untitled")
        body = (a.get("body", "") or a.get("summary", "") or "")[:1200]
        if body:
            source_blocks.append(f"[{ref_id}] {title}\n{body}")

    scraped_blocks = []
    for s in scraped[:10]:
        url = s.get("url", "")
        content = (s.get("content", "") or "")[:1500]
        if content:
            scraped_blocks.append(f"[{url}]\n{content}")

    combined = "\n\n".join(source_blocks + scraped_blocks)
    if len(combined) > 25000:
        combined = combined[:25000]

    lang_instruction = {
        "ar": "Respond in Arabic.",
        "fr": "Respond in French.",
        "en": "Respond in English.",
    }.get(language[:2], "Respond in English.")

    user_prompt = f"""Research Topic: {topic}

{lang_instruction}

Numbered Sources (cite by [N]):
{combined}

Produce a structured synthesis. CRITICAL: Each key finding MUST end with its source number(s) like [1] or [2][3]."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://achem.github.io",
        "X-Title": "ACHEM Reasoning Engine",
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": REASONING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 2048,
        "temperature": 0.3,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60),
        ) as response:
            if response.status != 200:
                text = await response.text()
                logging.error(f"Reasoning API error {response.status}: {text[:200]}")
                return None

            data = await response.json()

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

    if not content:
        return None

    return _parse_synthesis(content, references)


def _extract_cited_refs(text: str) -> List[int]:
    """Extract cited reference numbers like [1], [2][3] from text."""
    ids = set()
    for match in re.finditer(r"\[(\d+)\]", text):
        ids.add(int(match.group(1)))
    return sorted(ids)


def _build_reference_list(
    references: List[Dict],
    cited_ids: List[int],
) -> List[Dict]:
    """Build reference list with cited flags."""
    cited_set = set(cited_ids)
    result = []
    for ref in (references or []):
        rid = ref.get("ref_id", 0)
        result.append({
            "ref_id": rid,
            "title": ref.get("title", "Unknown"),
            "url": ref.get("url", ""),
            "cited": rid in cited_set,
        })
    return result


def _parse_synthesis(raw: str, references: List[Dict]) -> Optional[Dict]:
    """Parse JSON from AI synthesis response and extract citations."""
    json_candidates = []

    cleaned = raw.strip()
    if cleaned.startswith("{"):
        json_candidates.append(cleaned)

    code_blocks = re.findall(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    json_candidates.extend(code_blocks)

    braces_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if braces_match:
        json_candidates.append(braces_match.group(0))

    required_keys = {"summary", "key_findings", "themes"}

    for candidate in json_candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict) and required_keys.issubset(parsed.keys()):
                parsed.setdefault("contradictions", ["None identified"])
                parsed.setdefault("confidence_level", "medium")
                parsed["sources_analyzed"] = len(references)

                all_text = json.dumps(parsed)
                cited_ids = _extract_cited_refs(all_text)
                parsed["references"] = _build_reference_list(references, cited_ids)

                return parsed
        except (json.JSONDecodeError, TypeError):
            continue

    return None


def _local_synthesis(articles: List[Dict], references: List[Dict], topic: str) -> Dict:
    """Local fallback: extractive synthesis using TF-IDF-like scoring."""
    from .text_analyzer import TextAnalyzer

    analyzer = TextAnalyzer()

    texts = []
    for a in articles:
        body = a.get("body", "") or a.get("summary", "")
        if body and len(body) > 30:
            texts.append(body)

    combined = " ".join(texts) if texts else ""
    keywords = analyzer.find_recurring_keywords(articles, top_n=10)
    keyword_list = [kw for kw, _ in keywords]

    if not combined:
        return {
            "summary": f"Collected {len(articles)} sources about '{topic}'.",
            "key_findings": [f"Found {len(articles)} relevant sources"],
            "themes": keyword_list[:5] if keyword_list else ["general"],
            "contradictions": ["Local analysis cannot detect contradictions"],
            "confidence_level": "low",
            "sources_analyzed": len(articles),
            "references": _build_reference_list(references, [r.get("ref_id", 0) for r in (references or [])]),
        }

    sentences = re.split(r"[.!?\n]+", combined)
    scored = []
    seen = set()

    keyword_set = {kw.lower() for kw in keyword_list}

    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 40 or len(sent) > 600:
            continue
        sig = "".join(c for c in sent.lower() if c.isalnum())[:50]
        if sig in seen:
            continue
        seen.add(sig)

        score = sum(5 for kw in keyword_set if kw in sent.lower())
        score += len(sent) / 100
        if score > 0:
            scored.append((sent, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    top = [s for s, _ in scored[:10]]

    source_lines = []
    for a in articles[:5]:
        ref_id = a.get("ref_id", 0)
        t = a.get("title", "Untitled")
        body = (a.get("body", "") or a.get("summary", ""))
        excerpt = body[:200].strip() if body else ""
        if excerpt:
            source_lines.append(f"[{ref_id}] From '{t}': {excerpt}...")

    summary_parts = [
        f"Local analysis of {len(articles)} sources on '{topic}'.",
        "",
    ]
    if top:
        para = " ".join(top[:5])
        summary_parts.append(para + ".")
    if source_lines:
        summary_parts.append("")
        summary_parts.append("\n".join(source_lines[:3]))

    findings = []
    for i, s in enumerate(top[:5]):
        ref_id = articles[i % len(articles)].get("ref_id", 0) if articles else 0
        findings.append(f"{s} [{ref_id}]")

    return {
        "summary": "\n".join(summary_parts),
        "key_findings": findings if findings else [f"Collected {len(articles)} sources"],
        "themes": keyword_list[:5] if keyword_list else ["general"],
        "contradictions": ["Local analysis cannot detect contradictions"],
        "confidence_level": "low",
        "sources_analyzed": len(articles),
        "references": _build_reference_list(references, [r.get("ref_id", 0) for r in (references or [])]),
    }
