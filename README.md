# Survey Sentiment & Executive Intelligence

A **public-safe reference implementation** of an Azure-based survey analytics workflow. It demonstrates extraction of unstructured text, sentiment scoring, theme tagging, structured output, and an executive-level aggregate summary.

> **Portfolio note:** This is a generic reconstruction of an architectural pattern, **not the original employer code**. All sample feedback is synthetic. No proprietary survey questions, respondent records, production secrets, or internal models are included.

## Architecture

```text
Synthetic TXT / Survey PDF
         |
         v
Extraction: local TXT or Azure Document Intelligence (prebuilt-layout)
         |
         v
Sentiment: local demo lexicon or Azure AI Language
         |
         v
Theme classification (transparent keyword rules)
         |
         +--> survey_intelligence.csv
         +--> executive_summary.json
         +--> optional Spark Delta table
```

## Quick start (no Azure account required)

Python 3.10+:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
survey-intelligence --input samples/synthetic_feedback.txt --output output
pytest -q
```

Read `output/survey_intelligence.csv` and `output/executive_summary.json`. The local sentiment model is a **simple heuristic used only for demos**; it is not a validated NLP model.

## Azure Document Intelligence PDF extraction

```bash
python -m pip install -e '.[azure]'
# Copy .env.example to your own config or set environment variables in your shell.
# The application reads environment variables; it does NOT automatically load .env.
export AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT='https://YOUR-RESOURCE.cognitiveservices.azure.com/'
export AZURE_DOCUMENT_INTELLIGENCE_KEY='your-secret'
survey-intelligence --input path/to/survey.pdf --output output
```

On Windows PowerShell use `$env:AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="..."` and similarly for the key. Azure API calls may incur charges.

### Managed sentiment scoring with Azure AI Language

```bash
export AZURE_LANGUAGE_ENDPOINT='https://YOUR-LANGUAGE-RESOURCE.cognitiveservices.azure.com/'
export AZURE_LANGUAGE_KEY='your-secret'
survey-intelligence --input samples/synthetic_feedback.txt --scorer azure
```

For PDF + Azure sentiment, provide all four credentials. **Don't commit keys or real survey responses.** The Document Intelligence SDK here uses the `azure.ai.formrecognizer.DocumentAnalysisClient` interface consistent with the architecture example.

## Delta output

The optional Delta adapter calls `SparkSession.getActiveSession()` and therefore is for a **Spark-hosted environment** (such as a Fabric notebook or a Delta-enabled Spark job), not a standalone local CLI without Spark session initialization. From that environment, call `write_delta(rows, "silver_survey_intelligence", "azure")` after constructing rows, or invoke the CLI while a compatible session is active. Dependencies: `pip install -e '.[spark]'`. Delta integration and credentials depend on the host platform. The included example uses append mode; production deployments should implement deduplication, stable IDs, and idempotent merges.

## Data contract

The CSV columns are `response_id`, `source`, `page`, `feedback`, `sentiment`, `score`, `themes`, `scoring_method`. A local score ranges from -1 to 1; an Azure score is *positive confidence minus negative confidence*. **These two scores are not calibrated or directly comparable.** Themes are rule-based and multi-label. The JSON file contains overall counts, average score, and theme frequencies.

## Important limitations

- Document Intelligence layout analysis does **not** reliably identify respondent boundaries by itself. Paragraphs are treated as candidate response segments, not one response per respondent.
- Real survey parsing needs a form-specific mapping, removal of headers, consent/PII controls, and quality review.
- The sample lexicon scorer does not handle negation, sarcasm, context, or language diversity. Use a validated model for substantive decisions.
- Aggregates describe extracted text segments, not a statistically representative population. Do not use them to infer respondent sentiment rates without verified mappings.
- For production, add retries/backoff for Azure rate limits, monitoring, cost control, redaction, access control, and per-document error routing.
- Avoid publishing any raw employee, student, customer, or personally identifiable feedback.

## Repository layout

```text
src/survey_intelligence/  extraction, scoring, reporting, Delta adapter, CLI
samples/                  invented feedback for reproducible offline run
tests/                    core unit and integration tests
docs/                     architecture and privacy notes
.github/workflows/        CI tests
.env.example              credential variable names only
```

## Why this project exists

Survey insights often arrive as files rather than structured records. This example shows how an extraction pipeline can standardize feedback, apply an NLP scoring step, attach themes, and produce management-ready summaries. It is designed to communicate technical approach while protecting sensitive business data.

## License

MIT, see `LICENSE`.
