# Architecture and design decisions

1. **Ingest:** local `.txt` synthetic records for zero-dependency testing or PDF input through Azure Document Intelligence layout model.
2. **Normalize:** create records with `source`, `page`, and `feedback`. PDF paragraphs are candidate segments, not verified responses.
3. **Enrich:** attach managed sentiment or deterministic local heuristic and multi-label keyword themes.
4. **Publish:** write a standardized CSV and aggregated JSON. Optionally push records to a Spark Delta table in a compatible host.
5. **Consume:** connect Power BI or another reporting layer to CSV, JSON, or Delta tables; not included as a production dashboard.

Production extension points: configuration-driven question mapping, survey-specific deduplication, batch retries, PII redaction, row-level access control, language detection, observability, and regression tests with manually labeled examples.
