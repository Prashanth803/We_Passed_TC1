from flask import Flask, jsonify
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key="AIzaSyDjpailUEWHLsNchA85AdDo2Wbub6q1DG8")
 
# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

load_dotenv()

app = Flask(__name__)

GITHUB_API_BASE = "https://api.github.com/repos"
GITHUB_TOKEN = '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'
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def get_file_content(owner, repo, file_path):
    """
    Fetch the content of a specific file from a GitHub repository.
    """
    url = f"{GITHUB_API_BASE}/{owner}/{repo}/contents/{file_path}"
    print(f"[DEBUG] Fetching file: {url}")
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": f"{response.status_code}: {response.json().get('message')}"}

    file_data = response.json()
    if file_data["type"] == "file":
        download_url = file_data["download_url"]
        content_response = requests.get(download_url)
        if content_response.status_code == 200:
            return {"content": content_response.text}
        else:
            return {"error": f"{content_response.status_code}: Could not download file content"}
    else:
        return {"error": "Not a file"}

def get_repo_contents(owner, repo, path=""):
    """
    Recursively fetch the contents of a GitHub repository.
    """
    url = f"{GITHUB_API_BASE}/{owner}/{repo}/contents/{path}"
    print(f"[DEBUG] Fetching: {url}")
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return {"error": f"{response.status_code}: {response.json().get('message')}"}

    contents = response.json()
    repo_data = {}

    for item in contents:
        item_name = item["name"]
        item_path = item["path"]
        item_type = item["type"]

        if item_type == "file" and item_name.endswith(".py"):
            repo_data[item_name] = {
                "type": "file",
                "download_url": item["download_url"]
            }
            # Fetch and log file content
            file_content_data = get_file_content(owner, repo, item_path)
                # print(response.text)
            log_file("sivam",file_content_data["content"])

        elif item_type == "dir":
            # Recursively fetch folder contents
            sub_dir = get_repo_contents(owner, repo, item["path"])
            repo_data[item_name] = {
                "type": "directory",
                "contents": sub_dir
            }

    return repo_data

def log_file(filename, content):
    """
    Write the file content to a log file.
    """
    try:
        with open("log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(content)
            log_file.write("\n\n")

        print(f"[LOG] Content of {filename} logged.")
    except Exception as e:
        print(f"[ERROR] Failed to log content of {filename}: {e}")

def remove_empty_fields(obj):
    if isinstance(obj, dict):
        return {
            k: remove_empty_fields(v)
            for k, v in obj.items()
            if v not in [None, "", [], {}] and remove_empty_fields(v) != {}
        }
    elif isinstance(obj, list):
        return [remove_empty_fields(v) for v in obj if v not in [None, "", [], {}]]
    else:
        return obj

def ensure_array_items(obj):
    """
    For any 'type': 'array' field in parameters, add 'items': {'type': 'string'} if missing.
    Default to 'string' unless you want to infer more types.
    """
    if isinstance(obj, dict):
        if obj.get("type") == "array" and "items" not in obj:
            obj["items"] = {"type": "string"}  # Or "number"/"integer" as needed
        for k, v in obj.items():
            obj[k] = ensure_array_items(v)
    elif isinstance(obj, list):
        obj = [ensure_array_items(v) for v in obj]
    return obj


def log_response(content):
    cleaned_content=content.replace("```json","").replace("\n```","").strip()
    content_json=json.loads(cleaned_content)
    cleaned_json=remove_empty_fields(content_json)
    print("+=====================================================================+")
    print(cleaned_json)
    # fixed_json = ensure_array_items(cleaned_json)
    with open('log2.json','w')as log_file:
        log_file.write(json.dumps(cleaned_json, indent=2))
        log_file.write("\n\n")
    data = {
            "system_instruction": {
                "parts": [{"text": "You are a testing bot who tests system when you are given a particular test case scenario. If you need to autheticate the user use username:testuser@test.com password:test123"}]
            },
            "tools":[{
                "function_declarations":cleaned_json
                }
            ],
            "tool_config": {
                "function_calling_config": {"mode": "auto"}
            },
            "contents": {
                "role": "user",
                "parts": [{"text": """
                Given a user is authenticated with a valid token
                """}]
            }
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=AIzaSyDjpailUEWHLsNchA85AdDo2Wbub6q1DG8"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, json=data)

    with open("log1.txt", "a") as log_file:
        log_file.write(response.text)
        log_file.write("\n\n")

@app.route("/github/<owner>/<repo>", methods=["GET"])
def fetch_github_repo(owner, repo):
    """
    Endpoint to fetch GitHub repo contents recursively.
    """
    try:
        repo_contents = get_repo_contents(owner, repo)
        with open("log.txt", "r") as log_file:
            content = log_file.read()
            if content:
                response = model.generate_content(f"""System prompt: {content}

      User prompt: 
      Define the function using JSON, specifically with a select subset of the OpenAPI schema format. A single function declaration can include the following parameters:

      name (string): The unique identifier for the function within the API call.
      description (string): A comprehensive explanation of the function's purpose and capabilities.
      parameters (object): Defines the input data required by the function.
        type (string): Specifies the overall data type, such as object.
        properties (object): Lists individual parameters, each with:
            type (string): The data type of the parameter, such as string, integer, boolean.
            description (string): A clear explanation of the parameter's purpose and expected format.
        required (array): An array of strings listing the parameter names that are mandatory for the function to operate.

      if any parameter is empty do not include it in the JSON. All parameters are required. There should not be any element in the json with empty value.
      If the is a empty value do not include it in the json.
      
      """)
                log_response(response.text)

        if "error" in repo_contents:
            return jsonify(repo_contents), 404
        return jsonify({
            "owner": owner,
            "repo": repo,
            "contents": repo_contents
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/github/<owner>/<repo>/file/<path:file_path>", methods=["GET"])
def fetch_github_file(owner, repo, file_path):
    """
    Endpoint to fetch the content of a specific file.
    """
    try:
        file_content = get_file_content(owner, repo, file_path)
        if "content" in file_content:
            log_file(file_path, file_content["content"])
            return jsonify(file_content)
        else :
            return jsonify(file_content),404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)