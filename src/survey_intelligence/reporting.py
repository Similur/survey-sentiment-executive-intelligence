"""Create standardized datasets and an executive-friendly aggregate report."""
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def make_summary(rows: list[dict], mode: str) -> dict:
    labels = Counter(row["sentiment"] for row in rows)
    themes = Counter(theme for row in rows for theme in row["themes"])
    count = len(rows)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scoring_method": mode,
        "responses_processed": count,
        "sentiment_counts": {label: labels[label] for label in ("positive", "neutral", "negative", "mixed")},
        "average_sentiment_score": round(sum(row["score"] for row in rows) / count, 3) if count else None,
        "theme_counts": dict(sorted(themes.items(), key=lambda kv: (-kv[1], kv[0]))),
        "note": "Candidate text segments, not verified distinct survey respondents. Do not infer population-level rates.",
    }


def write_outputs(rows: list[dict], output: Path, mode: str) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    cols = ["response_id", "source", "page", "feedback", "sentiment", "score", "themes", "scoring_method"]
    with (output / "survey_intelligence.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for i, row in enumerate(rows, start=1):
            writer.writerow({"response_id": i, "source": row["source"], "page": row["page"],
                             "feedback": row["feedback"], "sentiment": row["sentiment"],
                             "score": row["score"], "themes": "|".join(row["themes"]),
                             "scoring_method": mode})
    summary = make_summary(rows, mode)
    (output / "executive_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
