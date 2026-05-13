from groq import Groq
from utils.web_search import search_web
from dotenv import load_dotenv
import re

load_dotenv()

class FactChecker:
    """
    Spawns dynamically when a factual claim is detected in an argument.
    
    Concept — Dynamic Agent Spawning:
    Instead of always running, the FactChecker only activates when
    it detects checkable claims (statistics, named events, specific facts).
    This mimics real debate fact-checkers who intervene only when needed.
    """

    def __init__(self):
        self.client = Groq()
        self.name = "Fact-Checker"

    def contains_factual_claim(self, text: str) -> bool:
        """
        Quick heuristic check — does this argument contain
        a specific factual claim worth verifying?
        Looks for numbers, percentages, named studies, statistics.
        """
        patterns = [
            r'\d+%',                    # percentages
            r'\d+ million|\d+ billion', # large numbers
            r'studies show|research shows|according to',
            r'in \d{4}',               # year references
            r'statistics|data shows|survey',
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in patterns)

    def check(self, agent_name: str, argument: str) -> str:
        """
        1. Extract the main factual claim
        2. Search the web for it
        3. Return a fact-check verdict
        """

        # Step 1: Extract the claim worth checking
        extract_response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"Extract the single most specific factual claim from this argument that can be verified with a web search. Return ONLY the search query, nothing else:\n\n{argument}"
            }]
        )
        search_query = extract_response.choices[0].message.content.strip()

        # Step 2: Search the web
        search_results = search_web(search_query)

        # Step 3: Verdict
        verdict_response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""You are a fact-checker. Based on these search results, evaluate this claim.

Claim by {agent_name}: {argument[:300]}

Search results:
{search_results}

Respond in this format:
VERDICT: <SUPPORTED / DISPUTED / UNVERIFIED>
FACT_CHECK: <2 sentences explaining what the evidence shows>"""
            }]
        )

        return f"\n[FACT-CHECKER] {verdict_response.choices[0].message.content}"