# Setup Guide

## Prerequisites
- Python 3.8+
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variable:**
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

   Or create a `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Running the Application

1. **Start the backend server:**
   ```bash
   python backend.py
   ```
   Backend will run on `http://localhost:5000`

2. **Open the frontend:**
   ```bash
   open index.html
   ```
   Or simply double-click `index.html` in Finder

## How It Works

### Workflow:
1. User enters a Git repository URL
2. Frontend calls backend `/generate-diagram` endpoint
3. Backend sends explanation to Gemini API
4. Gemini converts explanation to Mermaid diagram syntax
5. Frontend receives Mermaid code and renders it

### API Endpoints:

**POST /generate-diagram**
- Input: `{"explanation": "text description"}`
- Output: `{"success": true, "mermaid": "graph TB..."}`

**POST /analyze**
- Input: `{"repo_url": "...", "explanation": "..."}`
- Output: `{"success": true, "explanation": "...", "mermaid": "..."}`

**GET /health**
- Health check endpoint

## Testing

Test the backend directly:
```bash
curl -X POST http://localhost:5000/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{"explanation": "A simple API with routes and database models"}'
```

## Next Steps

To integrate with your Trainium fine-tuned model:
1. Replace `exampleExplanation` with actual SageMaker endpoint call
2. Update `/analyze` endpoint to call your deployed model
3. Add repo cloning and code extraction logic
