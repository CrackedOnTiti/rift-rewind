import sys
import os
import time
import json

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def run_chat(session_token):
    """Start AI coaching chat with given session token."""
    print(f"Starting chat with session token: {session_token}")
    # TODO: Implement chat functionality
