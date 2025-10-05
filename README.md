# Codebase Analyzer with Mermaid Diagrams

A web application that analyzes codebases and generates visual architecture diagrams using a fine-tuned LLM and Mermaid.js.

## Architecture Overview

```
User Input (Git URL)
    ↓
Frontend (index.html)
    ↓
Backend API (Flask)
    ↓
┌─────────────────────┐
│ Trainium Model      │ → Text Explanation
│ (TinyLlama)         │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Gemini API          │ → Mermaid Syntax
│ (External LLM)      │
└─────────────────────┘
    ↓
Frontend Mermaid.js → Visual Diagram
```

## Components

### 1. Frontend (`index.html`)
- Clean, modern UI built with vanilla HTML/CSS/JS
- URL input form to submit repository URLs
- Displays codebase explanation text
- Renders Mermaid diagrams using Mermaid.js CDN
- Stores submitted URLs in localStorage

### 2. Backend (`backend.py`)
- Flask REST API with CORS enabled
- Integrates with Google Gemini API
- Converts plain text explanations to Mermaid diagram syntax
- Two main endpoints:
  - `/generate-diagram` - Converts explanation to Mermaid
  - `/analyze` - Full workflow (for future Trainium integration)

### 3. Integration Flow
1. User submits Git repository URL
2. Backend receives codebase explanation (from Trainium model)
3. Backend calls Gemini API to convert explanation → Mermaid syntax
4. Frontend receives Mermaid code and renders diagram

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation instructions.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set Gemini API key
export GEMINI_API_KEY="your_key_here"

# 3. Run backend
python backend.py

# 4. Open frontend
open index.html
```

## Testing

```bash
# Test the backend API
python test_backend.py

# Or test manually with curl
curl -X POST http://localhost:5000/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{"explanation": "Your codebase explanation here"}'
```

## Files

- `index.html` - Frontend application
- `backend.py` - Flask API server
- `requirements.txt` - Python dependencies
- `test_backend.py` - Backend test suite
- `SETUP.md` - Setup instructions

## Technology Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript, Mermaid.js
- **Backend**: Flask, Google Gemini API
- **Training**: AWS Trainium (TinyLlama-1.1B) - *in progress*
- **Inference**: AWS SageMaker + Inferentia - *planned*

## Next Steps

1. ✓ Create frontend with URL input
2. ✓ Integrate Gemini API for Mermaid generation
3. ⏳ Complete Trainium model training
4. ⏳ Deploy model to SageMaker inference endpoint
5. ⏳ Add repository cloning and code extraction
6. ⏳ Connect backend to SageMaker endpoint

## License

MIT