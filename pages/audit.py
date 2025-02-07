import os
import streamlit as st
import requests
import fitz  # PyMuPDF

from openai import OpenAI
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import post
from typing import Optional, Dict

class Settings(BaseSettings):
    the_graph_api_key: str
    openai_api_key: str
    etherscan_api_key: str
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

st.title("💬 Audit Asset")

settings = get_settings()

openai_api_key = settings.openai_api_key
etherscan_api_key = settings.etherscan_api_key

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Fill in the smart contract address form and WhitePaper",
        }
    ]


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

uploaded_file = st.file_uploader("Upload WhitePaper", type=("pdf"))

address = st.text_input(
    "Smart Contract Address",
    placeholder="0x0000000000000000000000000000000000000000",
)


my_prompt = """
Certainly! Here's a prompt you can use for the ChatGPT API to accept Solidity smart contract code and a whitepaper, then analyze and provide insights based on your desired points:

---

**Prompt for Smart Contract and Whitepaper Analysis:**

---

**Input:**
You will receive the following two inputs:
1. **Solidity Smart Contract Code**: {}
2. **Whitepaper (Optional)**: {}

---

**Instructions for ChatGPT API:**

Using the provided smart contract code and any accompanying whitepaper or documentation, perform the following analyses:

### 1. **Tokenomics / Distribution Analysis**
- **Objective**: Analyze the tokenomics and distribution mechanisms described in the smart contract code and whitepaper (if provided).
- **Tasks**:
  - Assess the fairness of the token distribution.
  - Identify any mechanisms that could indicate potential for "rug pulls" or unfair token allocations.
  - Evaluate whether the contract has centralized control over the token minting or distribution process.
  - Highlight any risks related to the allocation of tokens that could allow project founders or insiders to control or manipulate the token supply.

### 2. **Smart Contract Functionality**
- **Objective**: Provide a breakdown of the smart contract code, explaining all the relevant functionality.
- **Tasks**:
  - Summarize the purpose of each function and its role in the overall contract.
  - Identify key components, such as minting, burning, transferring, and any access control functions.
  - Provide a clear explanation of any significant logic related to token transfers, user roles, and restrictions.

### 3. **Project Summary**
- **Objective**: Analyze the whitepaper and any other available project documentation.
- **Tasks**:
  - Provide a comprehensive and easy-to-digest project summary based on the available documents.
  - Explain the project's objectives, use cases, and overall goals.
  - Identify any key aspects of the project that align with best practices, as well as any potential concerns raised in the whitepaper.

### 4. **Vulnerabilities**
- **Objective**: Analyze the smart contract code for vulnerabilities and security risks.
- **Tasks**:
  - Scan the contract for known security vulnerabilities such as:
    - **Reentrancy attacks**
    - **Overflow/underflow errors**
    - **Improper access controls**
    - **Unchecked call exceptions**
  - Identify any other weaknesses that may compromise the security of the contract or users interacting with it.

### 5. **Red Flags**
- **Objective**: Detect suspicious patterns or behavior within the contract code that could be indicative of malicious intent or potential risks.
- **Tasks**:
  - Look for **overly complex or obfuscated code** that may hide malicious behavior.
  - Identify **backdoors** or secret functions that grant developers excessive control or allow for privileged actions.
  - Check for patterns that are often seen in **malicious projects**, such as too much control retained by developers, emergency pause functions, or administrative privileges that could be exploited.

### 6. **Risk Scoring**
- **Objective**: Generate a risk score for the smart contract and project as a whole based on the analysis.
- **Tasks**:
  - Based on the severity of identified vulnerabilities, tokenomics concerns, red flags, and overall smart contract design, provide a risk score for the project.
  - The score should range from **1 (low risk)** to **10 (high risk)**, indicating the overall level of security and fairness of the contract and project.

---

**Output:**

Please provide the following in a well-structured and easy-to-read format:

1. **Tokenomics / Distribution Analysis**
2. **Smart Contract Functionality Breakdown**
3. **Project Summary**
4. **Vulnerability Scan Report**
5. **Red Flags Detected**
6. **Risk Scoring**

---
"""

smart_contract_code = ""
pdf_text_short = ""


def get_contract_code(api_key, contract_address):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
        "apikey": api_key,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "1":
            contract_info = data["result"][0]
            contract_code = contract_info.get("SourceCode", "No source code available.")
            return contract_code
        else:
            return f"Error: {data['message']}"
    except Exception as e:
        return f"An error occurred: {e}"


if address:
    smart_contract_code = get_contract_code(etherscan_api_key, address)


def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text


if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    pdf_text_short = pdf_text[:4000]

ready_prompt = my_prompt.format(
    smart_contract_code,
    pdf_text_short
)

if st.button("Audit", use_container_width=True):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append(
        {
            "role": "user",
            "content": ready_prompt,
        }
    )

    # st.chat_message("user").write(ready_prompt)

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=st.session_state.messages
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)