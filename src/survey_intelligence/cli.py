"""CLI entry point for the demonstration pipeline."""
import argparse
import json
import os
from pathlib import Path
from .extraction import extract_pdf, extract_txt
from .reporting import write_outputs
from .scoring import score_azure, score_local


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Survey Sentiment & Executive Intelligence demo")
    parser.add_argument("--input", type=Path, default=Path("samples/synthetic_feedback.txt"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--scorer", choices=["local", "azure"], default="local")
    parser.add_argument("--write-delta", action="store_true", help="Optional Spark Delta write")
    parser.add_argument("--delta-table", default="silver_survey_intelligence")
    args = parser.parse_args(argv)
    if not args.input.is_file():
        parser.error(f"Input does not exist: {args.input}")
    suffix = args.input.suffix.lower()
    if suffix == ".txt":
        extracted = extract_txt(args.input)
    elif suffix == ".pdf":
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        if not endpoint or not key:
            parser.error("PDF processing requires AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY")
        extracted = extract_pdf(args.input, endpoint, key)
    else:
        parser.error("Supported input formats: .txt (offline demo), .pdf (Azure)")
    if args.scorer == "azure":
        endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
        key = os.getenv("AZURE_LANGUAGE_KEY")
        if not endpoint or not key:
            parser.error("Azure scoring requires AZURE_LANGUAGE_ENDPOINT and AZURE_LANGUAGE_KEY")
        scored = score_azure([x["feedback"] for x in extracted], endpoint, key)
    else:
        scored = [score_local(x["feedback"]) for x in extracted]
    rows = [{**item, **prediction} for item, prediction in zip(extracted, scored)]
    summary = write_outputs(rows, args.output, args.scorer)
    if args.write_delta:
        from .delta_output import write_delta
        write_delta(rows, args.delta_table, args.scorer)
    print(json.dumps(summary, indent=2))
    print(f"Saved outputs in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
