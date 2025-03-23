
from flask import Flask, jsonify
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from json_cleaning import remove_empty_fields, ensure_array_items
from log_generator import log_file
from file_handler import get_file_content

load_dotenv()

GITHUB_API_BASE = "https://api.github.com/repos"
GITHUB_TOKEN =  os.getenv("GITHUB_TOKEN")


HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

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

        if item_type == "file" and item_name.endswith(".js"):
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