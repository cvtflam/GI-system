# GI Log Data System

A Python proof-of-concept for transforming geotechnical investigation (GI) log PDFs into structured, machine-readable engineering data using Google GenAI and Pydantic schemas.

This project explores how generative AI can support the civil and geotechnical engineering workflow by converting unstructured GI log documents into consistent soil-layer records that can be analysed, validated, and reused downstream.

The long-term vision is to build a practical AI-assisted geotechnical data platform that can ingest GI logs, lab reports, field test records, and other project documents from multiple formats such as PDF, AGS, Excel, and text, and convert them into structured data for engineering interpretation and decision making.

## Why this project matters

Geotechnical data is often locked inside PDF logs and descriptive reports. Extracting this information manually is time-consuming and prone to inconsistency. This project demonstrates a lightweight approach to automate the first stage of that process:

- identify key borehole metadata
- parse soil layer descriptions into structured fields
- standardize layer-level information using a schema
- produce output that can be fed into downstream analysis workflows

For geotechnical engineers, this type of workflow supports faster review of GI information, improved traceability, and stronger foundations for data-driven geotechnical assessments.

## Project focus

The current implementation focuses on GI log extraction from a borehole PDF.

The workflow uses a Python script to:

1. Load a GI log PDF file.
2. Encode the file as base64 data.
3. Send the PDF and a domain-specific prompt to a Gemini model.
4. Validate the model response using a Pydantic schema.
5. Print a summary of the extracted GI metadata and soil layer information.

The implementation currently lives in a single script:

- `src/GI log data extraction.py`

## What the script extracts

The current extraction target includes:

- GI name
- easting and northing coordinates
- GI date
- contract number
- ground level
- soil layer reduced levels (in mPD) and depths (in m)
- soil layer description text
- rock grade
- soil material origin
- soil grain size
- existence of cobble

This structure is defined by the Pydantic models `Soil` and `Gi_stick`.

## Workflow

The project follows a simple AI-assisted extraction pattern:

```text
PDF GI log
    -> Gemini model with domain prompt
    -> structured JSON response
    -> Pydantic schema validation
    -> readable terminal summary
```

This makes the project suitable as a starting point for a future engineering data pipeline rather than a standalone extraction tool.

## Repository structure

```text
GI system/
├── data/
│   ├── demo/
│   │   └── GI log/
│   └── local/
│       └── GI log/
│       └── reference/
├── src/
│   └── GI log data extraction.py
└── README.md
```

## Technical stack

The project uses:

- Python 3.12
- Google GenAI
- Python dotenv
- Pydantic

Install dependencies:

```bash
pip install google-genai python-dotenv pydantic
```

## Environment setup

Create a local `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

The script reads this key through `dotenv` and initializes the Gemini client.

## How to run

From the project root:

```bash
python src/GI\ log\ data\ extraction.py
```

The current sample workflow is configured around a demo PDF file path used in the repository.

## Current limitations

This is a demonstration project and a research prototype rather than a production-grade data extraction platform. Current limitations include:

- a single-PDF, single-borehole workflow
- limited support for report-wide document parsing
- no persistent database or file output pipeline
- no formal validation framework for the full GI data lifecycle

## Future development directions

The next phase of the project could include:

- structured output saved to CSV, JSON, or a SQL database
- Mark llm identified data on the pdf for easy reference
- extraction for multiple GI PDFs or whole GI reports
- support for lab test reports and field test reports
- enable ags file input for data processing
- data normalization and validation pipelines
- statistical or machine-learning interpretation for soil parameters
- GI summary standardization across projects
- a geotechnical RAG database or knowledge layer that links extracted facts to engineering context

## Innovation vision

This project is designed to demonstrate how vision LLM-assisted reasoning and extraction, and schema-driven structured engineering data output can be used to improve the reliability, speed, and reuse of geotechnical information. This is to save human effort for one of the most time-consuming and common error-prone manual handling tasks in civil and geotechnical engineering.

The long-term goal is not only to extract log text, but to help engineers turn scattered project records into a more connected, inspectable, and decision-ready geotechnical data platform, with the incorporation of RAG geo-data system.
