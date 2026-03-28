# 🏥 MS-DRG Grouper — Direct from CMS Live

A web-based MS-DRG (Medicare Severity Diagnosis Related Group) grouper built with Streamlit, powered by the official CMS FY2026 v43.0 logic.

## What It Does

Enter patient clinical data and instantly get the MS-DRG assignment — the same grouping logic used by CMS for Medicare inpatient reimbursement.

| Input | Output |
|---|---|
| Principal Diagnosis (ICD-10-CM) | MS-DRG Code |
| Secondary Diagnoses | DRG Description |
| Procedures (ICD-10-PCS) | MDC (Major Diagnostic Category) |
| Date of Birth, Sex | Relative Weight |
| Admission / Discharge Dates | CC / MCC / No CC Status |
| Discharge Status | Length of Stay |

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/DrFarooqAi/drg-direct-app.git
cd drg-direct-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python -m streamlit run app.py --server.port 8990
```

Open your browser at **http://localhost:8990**

## Requirements

- Python 3.9+
- No Java required — pure Python CMS grouper

## ICD Code Format

- **No dots** — enter `I635` not `I63.5`
- **Uppercase** — `A419` not `a419`
- Multiple codes: comma or newline separated

## Tech Stack

- [Streamlit](https://streamlit.io) — Web UI
- [drg](https://pypi.org/project/drg/) — CMS MS-DRG FY2026 v43.0 grouper (pure Python)

## Data Source

CMS MS-DRG Classifications — FY2026 Final Rule v43.0
https://www.cms.gov/medicare/payment/prospective-payment-systems/acute-inpatient-pps/ms-drg-classifications-and-software

## License

MIT
