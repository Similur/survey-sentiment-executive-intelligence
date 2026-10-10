"""Deterministic local demo scoring or managed Azure AI Language sentiment.

The local scorer is intentionally simple and NOT a production-ready NLP model.
"""
import re

POSITIVE = {"great", "helpful", "excellent", "fast", "friendly", "clear", "easy", "smooth", "good", "responsive", "satisfied", "improved"}
NEGATIVE = {"slow", "confusing", "broken", "late", "difficult", "frustrating", "poor", "bad", "delay", "delayed", "unhelpful", "unclear"}
THEMES = {
    "service": {"staff", "support", "service", "helpful", "friendly", "team"},
    "timeliness": {"wait", "waiting", "delay", "delayed", "slow", "fast", "late", "responsive"},
    "communication": {"communication", "update", "updates", "email", "clear", "unclear", "confusing"},
    "technology": {"portal", "site", "website", "app", "system", "broken", "login"},
    "process": {"process", "steps", "form", "forms", "easy", "difficult", "smooth"},
}


def keywords(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def identify_themes(text: str) -> list[str]:
    tokens = keywords(text)
    return [theme for theme, words in THEMES.items() if tokens & words] or ["other"]


def score_local(text: str) -> dict:
    tokens = keywords(text)
    pos, neg = len(tokens & POSITIVE), len(tokens & NEGATIVE)
    # Lexicon heuristic, bounded to [-1, 1]; mixed or unmatched terms are neutral.
    score = round((pos - neg) / max(pos + neg, 1), 3)
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {"sentiment": label, "score": score, "themes": identify_themes(text)}


def score_azure(texts: list[str], endpoint: str, key: str) -> list[dict]:
    """Azure AI Language Sentiment; the score is positive minus negative confidence."""
    try:
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential
    except ImportError as exc:
        raise RuntimeError("Install optional Azure packages: pip install -e '.[azure]'") from exc
    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    results = []
    for offset in range(0, len(texts), 10):
        batch = texts[offset:offset + 10]
        analyses = client.analyze_sentiment(batch)
        for original, analysis in zip(batch, analyses):
            if analysis.is_error:
                raise RuntimeError(f"Azure Language sentiment failed: {analysis.error.code}")
            confidence = analysis.confidence_scores
            score = round(confidence.positive - confidence.negative, 3)
            results.append({"sentiment": analysis.sentiment, "score": score,
                            "themes": identify_themes(original)})
    return results
