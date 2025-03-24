
from flask import Flask, jsonify,request
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import re
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
GITHUB_TOKEN =  "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"
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

@app.route("/github", methods=["POST"])
def fetch_github_repo():
    """
    Endpoint to fetch GitHub repo contents recursively.
    """
    data = request.get_json()
    owner = data.get("githubLink").split("/")[0]
    repo = data.get("githubLink").split("/")[1]
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
        # Get the directory of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the file in the same directory
        file_path = os.path.join(script_directory,"bdd.json")
        
        
        response_data = {
        "message": "Context received successfully",
        "BDD": response.text  # Assuming `response.text` contains the BDD content
    }
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(response_data, json_file, indent=4)
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/function", methods=["GET"])
def process_api_calls(scenario):
    base_url = "https://taskmanagement-hehd.onrender.com/"
    final_response = ""
    apis_called = ""
    
   

    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the file in the same directory
    file_path = os.path.join(script_directory,"log1.txt")

    # Load the JSON data from a file
    with open(file_path, "r") as file:
        functions_to_call = json.load(file)
    


    # Extract function calls
    
    # API Mapping
    api_mapping = ""
    with (open("log.txt", "r")) as file:
        function_code = file.read()
        response = model.generate_content(
            contents=f"""System prompt: {function_code}

                    User prompt:
                    Create A json which maps the apis to their respective functions. only give the json and nothing else.
                    Use the format
                    function name:
                        api: api to be called
                        request type: get/post/put/delete
                        header: headers if required
                            headername: header
                    """
        )
        api_mapping = json.loads(response.text)
        
    print(api_mapping)

    
    for functionCall in functions_to_call['candidates'][0]["content"]['parts']:
        
        function_name = functionCall['functionCall']['name']
        body = functionCall['functionCall']['args']

        token = ""

        if api_mapping.get(function_name):
            api_url = api_mapping[function_name]['api']
            request_type = api_mapping[function_name]['request_type']
            headers = {"Content-Type": "application/json"}

            # Simulating header modification logic (assuming you handle this separately)
            generate_header = model.generate_content(
                contents=f"""System prompt:
                apis:
                {str(api_mapping[function_name])}
                response from previous apis:
                {final_response}

                User prompt:
                current header is :
                {str(headers)}
                make any required changes (if any) in header based on the previous responses from apis and return only the header in json format.
                """
            )
            # print(generate_header.text.replace("```json\n", "").replace("\n```", ""))
            headers = json.loads(generate_header.text.replace("```json\n", "").replace("\n```", ""))
            api_response = {}

            if request_type == 'get':
                api_response = requests.get(f"{base_url}{api_url}", headers=headers, json=body)
            elif request_type == 'post':
                api_response = requests.post(f"{base_url}{api_url}", headers=headers, json=body)

            apis_called += f"\n{function_name} called with args {body} and headers {headers}"
            final_response += f"\n{function_name} response: {api_response.text}"
        else:
            final_response += f"\n{function_name} response: function not found"

    print(final_response)
    print("                                                                                    ")
    judge(final_response,scenario)
    return final_response


def judge(final_response,scenario):
    judge_tasks = model.generate_content(
          
          contents=f"""System prompt:
          Our Test Scenerio was:
                {scenario}

          Our response after calling the apis:
                {final_response}

          User prompt:
          judge if this testcase failed or not.
          and also give the reason in json.

          format:
            passes: write 1 if it passed else write 0
            reason : explain why it failed. Keep it empty if it passed.

          Do not return anything other that the json
       """
    )
    print(judge_tasks.text)

   
@app.route("/test", methods=["GET"])
def test():
     #get bdd from bdd.json file
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the file in the same directory
    file_path = os.path.join(script_directory,"bdd.json")

    # Step 1: Read the JSON file
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Load JSON data

    # Step 2: Extract the BDD content
    bdd_text = data.get("BDD")  # Get the BDD content

    # Step 3: Remove unwanted escape sequences and formatting
    bdd_text = bdd_text.replace("```gherkin", "").replace("```", "").strip()
    bdd_text = re.sub(r'Feature:.*?\n', '', bdd_text, flags=re.DOTALL)

    # Step 4: Split into individual scenarios
    # Split based on "Scenario:" while keeping scenario titles
    scenarios = re.split(r'\n\s*Scenario:', bdd_text)

    # Reformat scenarios to restore "Scenario:" in each
    scenarios = [f"Scenario:{s.strip()}" for s in scenarios if s.strip()]
   
    # Step 6: Print the structured scenarios
    for scenario in scenarios:
        process_scenario(scenario)
    return jsonify({"scenarios": scenarios})

def process_scenario(scenario):
    
    data = {
            "system_instruction": {
                "parts": [{"text": "You are a testing bot who tests system when you are given a particular test case scenario."}]
            },
            "tools": [],
            "tool_config": {
                "function_calling_config": {"mode": "auto"}
            },
            "contents": {
                "role": "user",
                "parts": [{"text": """
                Given a user is not logged in
                And there are tasks with different statuses in the system
                When the user requests to list tasks with status "completed"
                Then the system should display only the tasks with status "completed"
                """}]
            }
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers,json=data)     
    script_directory = os.path.dirname(os.path.abspath(__file__))  
    file_path = os.path.join(script_directory,"log1.txt")
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(response.json(), json_file, indent=4)
    return response.json()
        
        
        
        
        
#     # # Get the directory of the current script   
#     # 
#     # # Construct the path to the file in the same directory
#     # 
#     # response_data = {
#     #     "message": "Context received successfully",
#     #     "candidates": response.json()  # Assuming `response.text` contains the BDD content
#     # }
#     # with open(file_path, "w", encoding="utf-8") as json_file:
#     #     json.dump(response_data, json_file, indent=4)

#     # return jsonify(response_data), 200
#     return scenario

    
    
    

   
    
       


        
        

    


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
   