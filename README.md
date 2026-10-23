# 🚀 Startup Validator AI

An AI-powered Python backend that evaluates startup ideas using **5 specialized agents** and produces a unified, evidence-driven verdict.

## 🤖 The 5 Agents

- **Market Agent** — Demand, audience, and market potential.
- **Risk Agent** — Technical, financial, and operational risks.
- **Competitor Agent** — Existing solutions and competitive advantages.
- **Monetization Agent** — Revenue models, pricing, and profitability.
- **Synthesis Agent** — Combines all findings into a final verdict and score.

## ⚙️ Tech Stack

Python · FastAPI · Pydantic · Groq API · Pytest

## ✨ Features

- Parallel agent execution for faster validation.
- Structured JSON outputs and evidence-backed findings.
- Animated, real-time validation progress in the frontend.
- Final verdict: **Build, Pivot, or Reject**.
- Market, risk, competition, and monetization scores.

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/startup-validator.git
cd startup-validator

python -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=your_api_key
GROQ_MODEL=your_supported_model
```

Run the API:

```bash
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

## 🔌 Example Request

`POST /api/v1/validate`

```json
{
  "idea": "An AI platform that automates invoice processing for SMEs",
  "target_market": "Small and medium-sized businesses",
  "region": "Global"
}
```

## 🧠 Validation Pipeline

```text
Startup Idea
     ↓
Market · Risk · Competitor · Monetization
     ↓
   Synthesis Agent
     ↓
Verdict + Scores + Recommendations
```

## 🗺️ Roadmap

- [ ] Parallel agent orchestration
- [ ] Source citations and market research
- [ ] Animated live progress updates
- [ ] Persistent validation history
- [ ] Exportable validation reports

**Disclaimer:** AI-generated assessments are decision-support tools, not guarantees of startup success.

Contributions are welcome. Add your license before publishing.