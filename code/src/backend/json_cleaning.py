from flask import Flask, jsonify
import requests
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

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