from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import post
from typing import Optional, Dict

class Settings(BaseSettings):
    api_key: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

class GraphqlReq(BaseModel):
    query: str
    operationName: Optional[str] = None
    variables: Optional[Dict[str, object]] = None

subgraph_url = "https://gateway-arbitrum.network.thegraph.com/api/subgraphs/id/HUZDsRpEVP2AvzDCyzDHtdc64dyDxx8FQjzsmqSg4H3B"

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
        return response.json()
    else:
        print("Error:", response.text)
        return None

if __name__ == "__main__":
    settings = get_settings()
    query = """
    {
  factories(first: 5) {
    id
    poolCount
    txCount
    totalVolumeUSD
  }
  bundles(first: 5) {
    id
    ethPriceUSD
  }
}
    """
    print(send_graphql_query_to_subgraph(settings.api_key, query))