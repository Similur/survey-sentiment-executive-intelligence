from pathlib import Path
from survey_intelligence.extraction import extract_txt
from survey_intelligence.scoring import score_local, identify_themes
from survey_intelligence.reporting import make_summary, write_outputs


def test_extraction(tmp_path):
    sample = tmp_path / "feedback.txt"
    sample.write_text("Good support\n\nBad delay\n", encoding="utf-8")
    result = extract_txt(sample)
    assert len(result) == 2
    assert result[0]["source"] == "feedback.txt"


def test_scoring():
    assert score_local("Great friendly service")["sentiment"] == "positive"
    assert score_local("Slow confusing app")["sentiment"] == "negative"
    assert score_local("Ordinary response")["sentiment"] == "neutral"
    assert "technology" in identify_themes("The portal login failed")


def test_output(tmp_path):
    row = {"source": "demo.txt", "page": None, "feedback": "Great service",
           **score_local("Great service")}
    summary = write_outputs([row], tmp_path / "out", "local")
    assert summary["responses_processed"] == 1
    assert summary["sentiment_counts"]["positive"] == 1
    assert (tmp_path / "out" / "survey_intelligence.csv").exists()
    assert (tmp_path / "out" / "executive_summary.json").exists()


def test_empty_summary():
    summary = make_summary([], "local")
    assert summary["average_sentiment_score"] is None
    assert summary["responses_processed"] == 0


def test_cli(tmp_path):
    from survey_intelligence.cli import main
    inp = tmp_path / "feedback.txt"
    inp.write_text("Helpful staff\nSlow website\n", encoding="utf-8")
    assert main(["--input", str(inp), "--output", str(tmp_path / "result")]) == 0
