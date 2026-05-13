import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str, max_results: int = 3) -> str:
    try:
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results
        )

        results = response.get("results", [])
        if not results:
            return "No search results found."

        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[Source {i}] {r.get('title', 'No title')}\n"
                f"URL: {r.get('url', '')}\n"
                f"Summary: {r.get('content', '')[:300]}..."
            )

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Search failed: {str(e)}"