# CSRD AI Data Extraction Engine

## Project Overview
This repository contains an AI-powered data extraction pipeline built to automatically extract **20 CSRD sustainability indicators** (Environmental, Social, and Governance) from large PDF-based annual and sustainability reports of European banks.

The project was developed as part of the **AA Impact Inc. AI Agent Developer technical case study**. The primary goal is to demonstrate an end-to-end extraction system that prioritizes **accuracy, transparency, and avoidance of hallucination** under tight time constraints.

---

## Key Features
- Automated extraction of 20 CSRD indicators per report  
- Page-level source citations for auditability  
- Confidence scoring for each extracted value  
- Explicit handling of missing or non-disclosed data  
- SQLite-based storage with CSV export  
- Modular and extensible Python architecture  

---

## Repository Structure

```text
.
├── data/
│   ├── reports/                 # Input PDF reports (AIB, BBVA, BPCE)
│   ├── csrd_data.db             # SQLite database (auto-generated)
│   └── csrd_results_openai.csv  # Final extracted results
├── src/
│   ├── main.py                  # Pipeline orchestrator
│   ├── extractor.py             # LLM prompt and extraction logic
│   ├── pdf_parser.py            # PDF text extraction logic
│   └── database.py              # Database schema and operations
├── requirements.txt
├── README.md
└── .env                         # API keys (not committed)
````

---

## Setup & Installation

### Prerequisites

* Python 3.10+
* OpenAI API key

### Installation Steps

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## Input Data

Place the PDF reports inside the `data/reports/` directory.
The system is configured to process three reports:

* AIB (Ireland)
* BBVA (Spain)
* Groupe BPCE (France)

---

## Running the Pipeline

```bash
python src/main.py
```

### Execution Flow

1. PDF reports are parsed page by page
2. Indicator-specific prompts are applied
3. The LLM extracts values, units, and context
4. Results are stored in SQLite
5. A final CSV file is exported

---

## Output Format

The output CSV contains the following fields:

| Column         | Description                     |
| -------------- | ------------------------------- |
| company        | Bank name                       |
| year           | Reporting year                  |
| indicator_name | CSRD indicator                  |
| value          | Extracted value or None         |
| unit           | Unit as disclosed in report     |
| confidence     | Extraction confidence (0.0–1.0) |
| source_page    | Page number reference           |
| notes          | Context or explanation          |

---

## Confidence Scoring Logic

* **1.0** – Value explicitly stated in the report
* **0.5** – Value partially inferred or indirectly stated
* **0.0** – Indicator not disclosed

---

## Units & Data Representation

Values are stored using the **original units as disclosed** in the source documents.
Unit normalization was intentionally avoided to prevent introducing conversion assumptions under tight time constraints.

---

## Limitations

* Some CSRD indicators are not explicitly disclosed in reports; these are recorded as null values
* Section-level references are not consistently machine-detectable; page numbers are used instead
* Image-based tables may not be captured without OCR integration

---

## Scalability

The system can be extended to additional banks or indicators by modifying configuration and prompts.
The architecture supports batch processing of large PDF documents.