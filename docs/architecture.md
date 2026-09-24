# Architecture — RA Operations Control Tower v0.1

## Pipeline

```text
.csv / .xlsx
     |
     v
loader.py
     |
     v
validation.py
     |
     v
analytics.py
     |
     +--> deterministic executive-summary template
     |
     v
excel_writer.py
     |
     v
5-sheet .xlsx report
```

## Module responsibilities

### `loader.py`

Loads tracker rows from CSV or XLSX.

CSV uses the standard-library `csv` module.

XLSX is parsed directly from the OOXML ZIP package. The loader resolves the first worksheet through `xl/workbook.xml` and `xl/_rels/workbook.xml.rels`, supports shared strings and inline strings, and normalizes Microsoft Excel numeric date serials into ISO dates.

### `validation.py`

Provides `ValidationError` and `validate_rows(rows)`.

Validation is fail-fast and intentionally separate from analytics. Once `analyze_rows` receives rows, it assumes the schema has already been validated.

### `analytics.py`

Pure deterministic calculations.

The caller supplies `as_of_date`; analytics never reads the system date.

It returns `kpis`, `rag`, `overdue`, and `raid_register`.

Internal missing KPI values are represented as `None`.

### `excel_writer.py`

Writes OOXML with standard-library primitives only.

The package contains `[Content_Types].xml`, root relationships, workbook relationships, and five worksheet XML parts.

The workbook relationships map `rId1` through `rId5` to the five sheet files.

Numeric cells use `t="n"`. Strings use `inlineStr`. Internal `None` becomes the text `N/A`.

### `cli.py`

Coordinates the pipeline: parse arguments, resolve date, load, validate, analyze, build the deterministic executive summary, and write the report.

`date.today()` is allowed only here as the default when `--as-of-date` is omitted.

## Determinism

Tests pass a fixed `as_of_date`.

The same validated rows and as-of date produce the same analytical result.

The report is generated without network access, LLM calls, or external services.

## Runtime dependency policy

`dependencies = []`.

The implementation uses standard-library modules only at runtime.

`setuptools` is declared only as the build backend and is not a runtime dependency.

## Excel compatibility

The writer was checked at two levels:

1. structural ZIP/XML verification in `test_phase2d.py`
2. application-level opening and value readback through installed Microsoft Excel

The Excel check confirmed five sheets and numeric/string cell types, including `N/A` for an unavailable on-time-delivery percentage.

## Known limitations

- First worksheet only for XLSX input.
- Formula cells are not evaluated; the loader reads stored values.
- No style-heavy dashboard formatting in v0.1.
- No Power BI integration.
- No web UI.
- No external APIs or notifications.
- RAG is ratio-only, so small-N projects can turn Red quickly.
