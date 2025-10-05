from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import boto3
import json
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in environment variables!")
    print("Please set it with: export GEMINI_API_KEY='your_key_here'")
    exit(1)
else:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use a fast, free model
    model = genai.GenerativeModel('gemini-2.5-flash')
    print(f"✓ Gemini API configured with model: gemini-2.5-flash")

# Configure AWS SageMaker for Trainium
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION]):
    print("ERROR: Missing AWS credentials in environment variables!")
    print("Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION")
    exit(1)

sagemaker_client = boto3.client(
    'sagemaker-runtime',
    region_name=AWS_DEFAULT_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)
TRAINIUM_ENDPOINT = os.environ.get('TRAINIUM_ENDPOINT')

if not TRAINIUM_ENDPOINT:
    print("ERROR: TRAINIUM_ENDPOINT not found in environment variables!")
    print("Please set it with: export TRAINIUM_ENDPOINT='your_endpoint_name'")
    exit(1)
print(f"✓ SageMaker configured for endpoint: {TRAINIUM_ENDPOINT}")

def document_github_repo_raw(url, branch="main", include_exts=None, token=None, max_file_size=200000):
    """
    Use git tree API to list files (one API request), then fetch content from
    raw.githubusercontent.com for each file (avoids per-file GitHub API requests).
    """
    url_components = url.split("/")
    owner = url_components[-2]
    repo = url_components[-1].split(".")[0]
    if include_exts is None:
        include_exts = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".html", ".css", ".go", ".rb", ".php"}
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    r = requests.get(tree_url, headers=headers)
    if r.status_code != 200:
        return f"[Error] Could not fetch repo tree: {r.status_code} {r.text}"
    tree = r.json().get("tree", [])
    output_lines = []
    current_folder = None
    for item in tree:
        if item.get("type") != "blob":
            continue
        path = item.get("path")
        _, ext = os.path.splitext(path)
        if ext.lower() not in include_exts:
            continue
        folder = os.path.dirname(path)
        filename = os.path.basename(path)
        if folder != current_folder:
            output_lines.append(f"Folder: {folder or 'Root Folder'}:")
            current_folder = folder
        output_lines.append(f"---> {filename}")
        # Build raw URL
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        try:
            resp = requests.get(raw_url, stream=True, timeout=10)
            resp.raise_for_status()
            size = int(resp.headers.get("content-length") or 0)
            if size and size > max_file_size:
                output_lines.append(f"     [Skipped {filename}: size {size} bytes > {max_file_size}]")
            else:
                text = resp.text
                indented = "\n".join("     " + line for line in text.splitlines())
                indented = indented[:50]
                output_lines.append(indented)
        except Exception as e:
            output_lines.append(f"     [Error fetching raw {filename}: {e}]")
        output_lines.append("")
    return "\n".join(output_lines)

@app.route('/generate-diagram', methods=['POST'])
def generate_diagram():
    """
    Takes a codebase explanation and converts it to Mermaid diagram syntax using Gemini.
    """
    try:
        if not GEMINI_API_KEY:
            return jsonify({'error': 'GEMINI_API_KEY not configured'}), 500
        
        data = request.json
        explanation = data.get('explanation', '')
        
        if not explanation:
            return jsonify({'error': 'No explanation provided'}), 400
        
        # Prompt for Gemini to convert explanation to Mermaid
        prompt = f"""You are an expert at creating valid Mermaid diagrams for software architecture.

Given the following codebase explanation, create a SIMPLE and VALID Mermaid flowchart.

CRITICAL RULES:
1. Start with: graph TB
2. Use SIMPLE node IDs (no spaces, no special chars): A, B, C, App, DB, API
3. Use square brackets for labels: A[Label Text]
4. For databases use: DB[(Database Name)]
5. Simple arrows only: A --> B
6. Keep labels SHORT (max 20 chars per line)
7. NO line breaks in labels
8. NO special characters in node IDs
9. Maximum 10-15 nodes
10. Test each line is valid Mermaid syntax

Codebase Explanation:
{explanation}

Generate ONLY valid Mermaid code. Start with 'graph TB' and keep it SIMPLE."""

        # Call Gemini API
        response = model.generate_content(prompt)
        mermaid_code = response.text.strip()
        
        # Clean up response (remove markdown code blocks if present)
        if mermaid_code.startswith('```mermaid'):
            mermaid_code = mermaid_code.replace('```mermaid', '').replace('```', '').strip()
        elif mermaid_code.startswith('```'):
            mermaid_code = mermaid_code.replace('```', '').strip()
        
        return jsonify({
            'success': True,
            'mermaid': mermaid_code
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    """
    TEMPORARY: Simulates the complete workflow using Gemini for both explanation generation (simulating Trainium)
    and Mermaid diagram generation.
    """
    try:
        if not GEMINI_API_KEY:
            return jsonify({'error': 'GEMINI_API_KEY not configured'}), 500
        
        data = request.json
        repo_url = data.get('repo_url', '')
        
        if not repo_url:
            return jsonify({'error': 'No repository URL provided'}), 400
        
        print(f"Analyzing repository: {repo_url}")
        
        # STEP 1: Scrape the GitHub repository
        print("Step 1: Fetching code from GitHub...")
        try:
            codebase_content = document_github_repo_raw(repo_url, branch="main", max_file_size=100000)
            
            if codebase_content.startswith("[Error]"):
                # Try 'master' branch if 'main' fails
                print("  Trying 'master' branch...")
                codebase_content = document_github_repo_raw(repo_url, branch="master", max_file_size=100000)
            
            print(f"  Fetched {len(codebase_content)} characters of code")
            
            # TinyLlama has VERY limited context (512 tokens total for input + output)
            # For code: 1 token ≈ 2-3 characters (not 4!)
            # Need: 250 input tokens + 150 output tokens = 400 total (safe buffer)
            max_context = 500  # ~250 tokens input, leaving room for 150 output tokens
            if len(codebase_content) > max_context:
                codebase_content = codebase_content[:max_context]
                print(f"  Truncated to {max_context} characters due to TinyLlama 512-token limit")
        except Exception as e:
            print(f"Error fetching GitHub repo: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to fetch repository: {str(e)}'
            }), 500
        
        # STEP 2: Call Trainium model with the actual code
        print("Step 2: Analyzing code with Trainium model...")
        try:
            # Prepare VERY SHORT prompt for Trainium (limited to 512 tokens total)
            trainium_prompt = f"""Code analysis:

{codebase_content}

Explain: what does this code do?"""

            # Prepare payload for Trainium with very conservative limits
            payload = {
                "inputs": trainium_prompt,
                "parameters": {
                    "max_new_tokens": 150,  # Further reduced to fit 512-token limit
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            # Invoke Trainium endpoint
            response = sagemaker_client.invoke_endpoint(
                EndpointName=TRAINIUM_ENDPOINT,
                Body=json.dumps(payload),
                ContentType="application/json"
            )
            
            # Parse Trainium response
            result = json.loads(response["Body"].read().decode())
            print(f"  Trainium response: {result}")
            
            # Extract explanation from Trainium response
            if isinstance(result, list) and len(result) > 0:
                trainium_explanation = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                trainium_explanation = result.get('generated_text', result.get('outputs', ''))
            else:
                trainium_explanation = str(result)
            
            print(f"  Generated explanation: {len(trainium_explanation)} characters")
            
        except Exception as e:
            print(f"Error calling Trainium: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to call Trainium model: {str(e)}'
            }), 500
        
        # STEP 3: Use Gemini to convert Trainium explanation to Mermaid diagram
        print("Step 3: Generating Mermaid diagram with Gemini...")
        mermaid_prompt = f"""You are an expert at creating valid Mermaid diagrams for software architecture.

Given the following codebase explanation, create a SIMPLE and VALID Mermaid flowchart.

CRITICAL RULES:
1. Start with: graph TB
2. Use SIMPLE node IDs (no spaces, no special chars): A, B, C, App, DB, API
3. Use square brackets for labels: A[Label Text]
4. For databases use: DB[(Database Name)]
5. Simple arrows only: A --> B
6. Keep labels SHORT (max 20 chars per line)
7. NO line breaks in labels
8. NO special characters in node IDs
9. Maximum 10-15 nodes
10. Test each line is valid Mermaid syntax

Codebase Explanation:
{trainium_explanation}

Generate ONLY valid Mermaid code. Start with 'graph TB' and keep it SIMPLE."""

        try:
            mermaid_response = model.generate_content(mermaid_prompt)
            mermaid_code = mermaid_response.text.strip()
            
            # Clean up response
            if mermaid_code.startswith('```mermaid'):
                mermaid_code = mermaid_code.replace('```mermaid', '').replace('```', '').strip()
            elif mermaid_code.startswith('```'):
                mermaid_code = mermaid_code.replace('```', '').strip()
            
            print(f"✓ Analysis complete for {repo_url}")
        except Exception as e:
            print(f"Error in Step 2: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to generate diagram: {str(e)}'
            }), 500
        
        return jsonify({
            'success': True,
            'repo_url': repo_url,
            'explanation': trainium_explanation,
            'mermaid': mermaid_code
        })
    
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_codebase():
    """
    Complete workflow: Takes explanation from Trainium model and returns both explanation and diagram.
    """
    try:
        if not GEMINI_API_KEY:
            return jsonify({'error': 'GEMINI_API_KEY not configured'}), 500
        
        data = request.json
        repo_url = data.get('repo_url', '')
        
        # In production, this would:
        # 1. Clone the repo
        # 2. Extract code structure
        # 3. Call Trainium/SageMaker endpoint for explanation
        # For now, we'll use the example explanation or user-provided one
        
        trainium_explanation = data.get('explanation', '')
        
        if not trainium_explanation:
            return jsonify({'error': 'No explanation provided'}), 400
        
        # Generate Mermaid diagram from explanation
        prompt = f"""You are an expert at creating valid Mermaid diagrams for software architecture.

Given the following codebase explanation, create a SIMPLE and VALID Mermaid flowchart.

CRITICAL RULES:
1. Start with: graph TB
2. Use SIMPLE node IDs (no spaces, no special chars): A, B, C, App, DB, API
3. Use square brackets for labels: A[Label Text]
4. For databases use: DB[(Database Name)]
5. Simple arrows only: A --> B
6. Keep labels SHORT (max 20 chars per line)
7. NO line breaks in labels
8. NO special characters in node IDs
9. Maximum 10-15 nodes
10. Test each line is valid Mermaid syntax

Codebase Explanation:
{trainium_explanation}

Generate ONLY valid Mermaid code. Start with 'graph TB' and keep it SIMPLE."""

        # Call Gemini API
        response = model.generate_content(prompt)
        mermaid_code = response.text.strip()
        
        # Clean up response
        if mermaid_code.startswith('```mermaid'):
            mermaid_code = mermaid_code.replace('```mermaid', '').replace('```', '').strip()
        elif mermaid_code.startswith('```'):
            mermaid_code = mermaid_code.replace('```', '').strip()
        
        return jsonify({
            'success': True,
            'repo_url': repo_url,
            'explanation': trainium_explanation,
            'mermaid': mermaid_code
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
