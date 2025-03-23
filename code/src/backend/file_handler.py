from flask import Flask, jsonify
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()


GITHUB_API_BASE = "https://api.github.com/repos"
GITHUB_TOKEN =  os.getenv("GITHUB_TOKEN")


HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def get_file_content(owner, repo, file_path):
    """
    Fetch the content of a specific file from a GitHub repository.
    """

    url = f"{GITHUB_API_BASE}/{owner}/{repo}/contents/{file_path}"
    print(f"[DEBUG] Fetching file: {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        # print("ok")
        return {"error": f"{response.status_code}: {response.json()}"}
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