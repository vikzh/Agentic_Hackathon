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

st.markdown("""
**AI-Powered Crypto Project Audit**

This AI-driven audit tool provides a comprehensive analysis of crypto projects, helping investors make informed decisions. It scans key aspects of the project and delivers a clear, easy-to-understand report. 

### **What it Solves:**
- **Helps Investors Assess Project Viability:** Get a clear overview of the project's fundamentals and risks.
- **Identifies Risks and Red Flags:** Detects potential vulnerabilities and warning signs early.
- **Ensures Compliance:** Checks for regulatory alignment and adherence to legal standards.
- **Evaluates Token Distribution:** Assesses fairness and sustainability of the tokenomics.
- **Provides Competitive Insights:** Helps understand the project’s positioning in the market.

### **How it Works:**
1. **Whitepaper & Smart Contract Data Extraction:** The tool analyzes data from the whitepaper and smart contract addresses.
2. **Tokenomics/Distribution Analysis:** Evaluates the project's token distribution for fairness and sustainability.
3. **Smart Contract Breakdown:** Explains the functionality of the smart contract in simple terms.
4. **Project Summary:** Provides a concise summary of the project's purpose and goals.
5. **Vulnerability Scan:** Scans the code for potential security weaknesses.
6. **Red Flags Detection:** Flags any unusual or risky aspects of the project.
7. **Pool Analysis:** Analyzes liquidity pools and token allocation.
8. **Regulatory Compliance Check:** Assesses whether the project complies with relevant regulations.
9. **Competitive Landscape:** Analyzes the project’s competitors and market positioning.
10. **Economic Impact & Use Cases:** Evaluates real-world applications and economic potential.
11. **Risk Scoring:** Provides a risk score to help determine the project’s overall safety and viability.

---
""")

settings = get_settings()

openai_api_key = settings.openai_api_key
etherscan_api_key = settings.etherscan_api_key
subgraph_url = "https://gateway-arbitrum.network.thegraph.com/api/subgraphs/id/HUZDsRpEVP2AvzDCyzDHtdc64dyDxx8FQjzsmqSg4H3B"


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
3. **Next Data From Exchange
    symbol
    name
    decimals
    # token total supply
    totalSupply
    # volume in token units
    volume
    # volume in derived USD
    volumeUSD
    # volume in USD even on pools with less reliable USD values
    untrackedVolumeUSD
    # fees in USD
    feesUSD
    # transactions across all pools that include this token
    txCount
    # number of pools containing this token
    poolCount
    # liquidity across all pools in token units
    totalValueLocked
    # liquidity across all pools in derived USD
    totalValueLockedUSD
    # TVL derived in USD untracked
    totalValueLockedUSDUntracked
    # Note: for chains where ETH is not the native token, this will be the derived
    # price of that chain's native token, effectively, this should be renamed
    # derivedNative
    derivedETH
    # pools token is in that are white listed for USD pricing** : {}

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

### 6. **Pool Analysis**
- **Objective**: Analyze pool data to assess liquidity, volume trends, and market stability.
- **Tasks**:
  - Evaluate liquidity sufficiency to support token stability and minimize volatility.
  - Analyze volume trends to assess trading activity and market interest.
  - Assess transaction count and fees to infer user engagement and potential profitability.
  - Evaluate pool diversity and whitelisting to understand market reach and security.
  - Investigate any correlations between derived ETH values and potential market manipulation risks.

### 7. **Regulatory Compliance Check**:
- **Objective**: Evaluate potential regulatory risks associated with the project.
- **Tasks**:
  - Identify any aspects of the smart contract or whitepaper that may raise regulatory concerns.
  - Assess whether the project appears to be in compliance with relevant laws and guidelines (e.g., KYC, AML).
  - Highlight jurisdictions that may pose specific regulatory risks.

### 8. **Competitive Landscape Analysis**:
- **Objective**: Contextualize the token within its competitive space.
- **Tasks**:
  - Identify direct competitors and analyze their market presence.
  - Compare key metrics (e.g., market cap, trading volume) to provide insights into the token's relative market position.
  - Highlight any unique features or advantages that differentiate the token from its competitors.

### 9. **Economic Impact and Real-World Use Cases**:
- **Objective**: Explore the broader impact and use cases of the token.
- **Tasks**:
  - Identify sectors or industries where the token is actively utilized or has potential for adoption.
  - Evaluate any partnerships or collaborations that enhance the token's use and credibility.
  - Analyze the token’s potential to address real-world problems or create economic value.

### 10. **Risk Scoring**
- **Objective**: Generate a risk score for the smart contract and project as a whole based on the analysis.
- **Tasks**:
  - Based on identified vulnerabilities, tokenomics concerns, red flags, and pool analysis, provide a risk score ranging from 1 (low risk) to 10 (high risk), indicating overall project security and fairness.

---

**Output:**

Please provide the following in a well-structured and easy-to-read format:

1. **Tokenomics / Distribution Analysis**
2. **Smart Contract Functionality Breakdown**
3. **Project Summary**
4. **Vulnerability Scan Report**
5. **Red Flags Detected**
6. **Pool Analysis**
7. **Regulatory Compliance Check**
8. **Competitive Landscape Analysis**
9. **Economic Impact and Real-World Use Cases**
10. **Risk Scoring**

---
"""

smart_contract_code = ""
pdf_text_short = ""


def get_contract_code(etherscan_api_key, contract_address):
    url = "https://api.etherscan.io/api"
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
        "apikey": etherscan_api_key,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "1":
            contract_info = data["result"][0]
            contract_code = contract_info.get("SourceCode", "No source code available.")
            st.success('Smart Contract code loaded successfully!')
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

    st.success('WhitePaper loaded successfully!')
    return text


if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    pdf_text_short = pdf_text[:4000]

def send_graphql_query_to_subgraph(api_key, query, variables = None):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # Prepare the request payload
    payload = {'query': query}
    if variables:
        payload['variables'] = variables

    # Send the GraphQL request to the Subgraph
    response = post(subgraph_url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        st.success('Subgraph loaded successfully!')
        return response.json()
    else:
        print("Error:", response.text)
        return None


def get_subgraph_data():
    settings = get_settings()
    query = f'''
{{
  token(id:"{address}") {{
    symbol
    name
    decimals
    # token total supply
    totalSupply
    # volume in token units
    volume
    # volume in derived USD
    volumeUSD
    # volume in USD even on pools with less reliable USD values
    untrackedVolumeUSD
    # fees in USD
    feesUSD
    # transactions across all pools that include this token
    txCount
    # number of pools containing this token
    poolCount
    # liquidity across all pools in token units
    totalValueLocked
    # liquidity across all pools in derived USD
    totalValueLockedUSD
    # TVL derived in USD untracked
    totalValueLockedUSDUntracked
    # Note: for chains where ETH is not the native token, this will be the derived
    # price of that chain's native token, effectively, this should be renamed
    # derivedNative
    derivedETH
    # pools token is in that are white listed for USD pricing
  }}
}}
    '''

    return send_graphql_query_to_subgraph(settings.the_graph_api_key, query)

subgraph_data=''

if address:
    subgraph_data = get_subgraph_data()

if st.button("Audit", use_container_width=True):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    ready_prompt = my_prompt.format(
        smart_contract_code,
        pdf_text_short,
        subgraph_data
    )

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