import os
import requests
from fastapi import FastAPI
from fastmcp import FastMCP
from langchain_community.utilities import WikipediaAPIWrapper

app = FastAPI()
mcp = FastMCP(name="Nutrition Info")
app.mount("/mcp", mcp)

@app.get("/")
def read_root():
    return {"status": "Nutrition Tool Server is running"}

NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")

@mcp.tool()
def nutrition_fetch(query: str) -> dict:
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
def wiki_search(query: str) -> str:
    wiki_wrapper = WikipediaAPIWrapper()
    return wiki_wrapper.run(query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
