from flask import Flask, jsonify
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from json_cleaning import remove_empty_fields
import re


def log_file(filename, content):
    """
    Write the file content to a log file.
    """
    try:
        with open("log.txt", "a", encoding="utf-8") as file:
            file.write(content)
            file.write("\n\n")

        print(f"[LOG] Content of {filename} logged.")
    except Exception as e:
        print(f"[ERROR] Failed to log content of {filename}: {e}")


def log_response(content):
    cleaned_content=content.replace("```json","").replace("\n```","").strip()
    content_json=json.loads(cleaned_content)
    cleaned_json=remove_empty_fields(content_json)
    print("+=====================================================================+")
    print(cleaned_json)
    # fixed_json = ensure_array_items(cleaned_json)
    with open('log2.json','w')as file:
        file.write(json.dumps(cleaned_json, indent=2))
        file.write("\n\n")

def generate_function_calls(function_desc,bdds):
    function_calls = []
    for bdd in bdds:
        data = {
                "system_instruction": {
                    "parts": [{"text": "You are a testing bot who tests system when you are given a particular test case scenario. If you need to autheticate the user use username:testuser@test.com password:test123"}]
                },
                "tools":[{
                    "function_declarations":function_desc
                    }
                ],
                "tool_config": {
                    "function_calling_config": {"mode": "auto"}
                },
                "contents": {
                    "role": "user",
                    "parts": [{"text": f"""
                    {bdd}
                    """}]
                }
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=AIzaSyDjpailUEWHLsNchA85AdDo2Wbub6q1DG8"
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers=headers, json=data)

        function_calls.append(response.json())
    
    return function_calls


def split_bdds(bdd_dict):
    bdd_text = ""

    # Combine all string values in the dictionary into one text block
    if isinstance(bdd_dict, dict):
        bdd_text = "\n".join(str(value) for value in bdd_dict.values())
    else:
        bdd_text = str(bdd_dict)

    # Clean and split
    bdd_text = bdd_text.replace("```gherkin", "")
    bdd_text = re.sub(r'```.*', '', bdd_text, flags=re.DOTALL).replace("```", "").strip()
    scenarios = re.split(r"\n\n\*\*Scenario \d+: ", bdd_text.strip())

    return scenarios