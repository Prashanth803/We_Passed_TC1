
from flask import Flask, jsonify,request
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from file_handler import get_file_content
from json_cleaning import remove_empty_fields, ensure_array_items
from get_repo import get_repo_contents
from log_generator import log_file, log_response
import logging

# Configure Gemini API key
genai.configure(api_key="AIzaSyDjpailUEWHLsNchA85AdDo2Wbub6q1DG8")
 
# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

load_dotenv()

app = Flask(__name__)

GITHUB_API_BASE = "https://api.github.com/repos"
GITHUB_TOKEN =  os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

CORS(app)

# Configure logging to see the requests
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["POST"])
def process_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        logging.info(f"Received data: {data}") # Log the received data

        action = data.get("action")
        context = data.get("context")
        api = data.get("api")
        github_link = data.get("githubLink")
        testing_criteria = data.get("testingCriteria")

        # Process the data (replace with your actual logic)
        result = f"Processed: Action={action}, Context={context}, API={api}, GitHub Link={github_link}, Testing Criteria={testing_criteria}"

        logging.info(f"Response: {result}") # log the response
        return jsonify({"result": result})

    except Exception as e:
        logging.error(f"Error: {str(e)}") # log the error
        return jsonify({"error": str(e)}), 500

@app.route("/github/<owner>/<repo>", methods=["POST"])
def fetch_github_repo(owner, repo):
    """
    Endpoint to fetch GitHub repo contents recursively.
    """
    
    try:
        repo_contents = get_repo_contents(owner, repo)
        print('ok')
        try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/catfe/context', methods=['POST'])
def receive_context():
    try:
        data = request.get_json()

        if not data or 'context' not in data:
            return jsonify({"error": "Missing 'context' in request body"}), 400

        context = data['context']

        print(f"Received context: {context}")
        response = model.generate_content(f"""System prompt:
        You are a skilled QA engineer specialized in Behavior-Driven Development (BDD). You generate comprehensive test cases based on user-provided scenarios or feature descriptions.

        User prompt:
        Given the following context, generate all possible BDD test cases using the 'Given-When-Then' format. Cover both positive and negative test cases, edge cases, and potential user behaviors if applicable.

        Context:
        {context}
        """)
        print(response.text)

        return jsonify({
            "message": "Context received successfully",
            "received": context
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)