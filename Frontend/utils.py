import streamlit as st
import requests
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

API_URL = "http://127.0.0.1:8000/api/"
DISTRICTS = ["Dhaka", "Chattogram", "Rajshahi", "Sylhet", "Barishal", "Khulna"]


def api_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, timeout: int = 7):

    ALL_ROUTES_ENDPOINT = f"{API_URL}{endpoint}"

    if method not in ('GET', 'POST', 'DELETE'):
        raise ValueError("Unsupported HTTP method")

    try:
        if method == 'GET':
            response = requests.get(ALL_ROUTES_ENDPOINT, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(ALL_ROUTES_ENDPOINT, json=data, timeout=timeout)
        else:
            response = requests.delete(ALL_ROUTES_ENDPOINT, timeout=timeout)

        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            return response.text

    except requests.exceptions.RequestException:
        raise