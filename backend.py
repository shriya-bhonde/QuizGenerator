import streamlit as st
import time
from PyPDF2 import PdfReader
import docx
from groq import Groq
from dotenv import load_dotenv
import requests
import os
import json
import re
import ast

load_dotenv()

# Access keys
GROQ_API_KEY = os.getenv("groq_api_key")

def parse_llm_output(output_str):
    """Parsing LLM output safely into Python objects (list/dict)."""

    print("output_str:", output_str)
    return json.loads(output_str)

def generate_flashcard_questions(text, num_questions=5):

    #Prompt for question generation
    prompt = f"""You are an expert academician. Generate {num_questions} true/flase quiz questions based on the following text. Each question should have 2 options (True/False), with one correct answer indicated. 
    Text: {text}    

    Return the response in the below format:
    
    [
        {{
            "question": "What is ...?",
            "answer": "True/False",
            "justification": "Explanation for the answer"
        }},
        {{
            "question": "What is ...?",
            "answer": "True/False",
            "justification": "Explanation for the answer"
        }}
    ]

    Return ONLY the JSON response. Do not include any explanations or additional text.
    
    """

    # Placeholder for LLM integration
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
      {
        "role": "user",
        "content": prompt
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None
    )
    
    llm_output = ""
    for chunk in completion:
        llm_output = llm_output + (chunk.choices[0].delta.content or "")

    output_str = parse_llm_output(llm_output)
    return output_str

def generate_mcq_questions(text, num_questions=5):

    #Prompt for question generation
    prompt = f"""You are an expert academician. Generate {num_questions} multiple-choice quiz questions based on the following text. Each question should have 4 options, with one correct answer indicated. 
    Text: {text}    

    Return the response in the below format:
    
    [
        {{
            "question": "What is ...?",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "answer": "A",
        }},
        {{
            "question": "What is ...?",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "answer": "B",
        }}
    ]

    Return ONLY the JSON response. Do not include any explanations or additional text.
    
    """

    # Placeholder for LLM integration
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
      {
        "role": "user",
        "content": prompt
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None
    )
    
    llm_output = ""
    for chunk in completion:
        llm_output = llm_output + (chunk.choices[0].delta.content or "")

    output_str = parse_llm_output(llm_output)
    return output_str