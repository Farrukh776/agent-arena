from agents.base_agent import Agent
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class JudgeAgent:
    """
    The Judge doesn't debate — it watches the whole debate
    then delivers a structured final verdict.
    It scores each agent and picks a winner with reasoning.
    """

    def __init__(self):
        self.client = Groq()
        self.name = "Judge"

    def deliver_verdict(self, topic: str, full_debate: str, scores: list) -> str:
        """
        Takes the full debate transcript + scores and delivers a verdict.
        """

        # Build score summary for the judge to reference
        score_summary = ""
        for s in scores:
            score_summary += (
                f"\n{s['agent']}: Logic={s['logic']}/10, "
                f"Evidence={s['evidence']}/10, "
                f"Coherence={s['coherence']}/10, "
                f"Total={s['total']}/30"
                f" | Fallacy detected: {s['fallacy']}"
            )

        prompt = f"""You are the Chief Judge of a formal debate. 
        
Topic: {topic}

FULL DEBATE TRANSCRIPT:
{full_debate}

ARGUMENT SCORES:
{score_summary}

Deliver your final verdict. Structure it EXACTLY like this:

WINNER: <agent name>

WINNING_REASON: <2 sentences on why they won>

STRONGEST_ARGUMENT: <quote the single best argument made in the entire debate>

WEAKEST_ARGUMENT: <name the agent and describe their weakest point>

KEY_INSIGHT: <one surprising or important insight that emerged from this debate>

FINAL_VERDICT: <3-4 sentences summarizing what the debate revealed about this topic>"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": "You are an impartial, rigorous debate judge. Be decisive and specific."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content