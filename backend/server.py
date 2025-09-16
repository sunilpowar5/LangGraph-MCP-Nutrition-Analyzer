import os
import requests
from mcp.server.fastmcp import FastMCP

from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun

from dotenv import load_dotenv
load_dotenv(override=True)

NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")

mcp = FastMCP(
    name="Nutrition Info",
    host="0.0.0.0",
    port=8000,
    stateless_http=True
)

@mcp.tool()
def nutrition_fetch(query:str)->dict:
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }
    resp = requests.post(
        "https://trackapi.nutritionix.com/v2/natural/nutrients",
        headers=headers,
        json={"query": query}
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": resp.text}

@mcp.tool(description="Fetch data via wikipedia api")
def wiki_search(query:str)->str:
    wiki_wrapper = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wiki_wrapper)
    return wiki_tool.run(query)

if __name__=="__main__":
    mcp.run(transport="streamable-http")