import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq()

def score_argument(agent_name: str, argument: str) -> dict:
    """
    Uses Groq to score a single argument on 3 dimensions.
    Returns a dict with scores and reasoning.

    Concept: We're using the LLM itself as a scoring engine
    by giving it a strict JSON output format to fill in.
    """

    prompt = f"""You are an expert debate judge. Score this argument strictly and fairly.

Agent: {agent_name}
Argument: {argument}

Score each dimension from 1-10 and give one sentence of reasoning.
Respond ONLY in this exact format, nothing else:

LOGIC_SCORE: <number>
LOGIC_REASON: <one sentence>
EVIDENCE_SCORE: <number>
EVIDENCE_REASON: <one sentence>
COHERENCE_SCORE: <number>
COHERENCE_REASON: <one sentence>
FALLACY: <name a logical fallacy if present, or "None">"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    return parse_scores(agent_name, argument, raw)


def parse_scores(agent_name: str, argument: str, raw: str) -> dict:
    """Parse the structured score response into a dict."""
    lines = raw.strip().split("\n")
    scores = {
        "agent": agent_name,
        "argument_preview": argument[:100] + "...",
        "logic": 0,
        "logic_reason": "",
        "evidence": 0,
        "evidence_reason": "",
        "coherence": 0,
        "coherence_reason": "",
        "fallacy": "None",
        "total": 0
    }

    for line in lines:
        if line.startswith("LOGIC_SCORE:"):
            try:
                scores["logic"] = int(line.split(":")[1].strip())
            except:
                scores["logic"] = 5
        elif line.startswith("LOGIC_REASON:"):
            scores["logic_reason"] = line.split(":", 1)[1].strip()
        elif line.startswith("EVIDENCE_SCORE:"):
            try:
                scores["evidence"] = int(line.split(":")[1].strip())
            except:
                scores["evidence"] = 5
        elif line.startswith("EVIDENCE_REASON:"):
            scores["evidence_reason"] = line.split(":", 1)[1].strip()
        elif line.startswith("COHERENCE_SCORE:"):
            try:
                scores["coherence"] = int(line.split(":")[1].strip())
            except:
                scores["coherence"] = 5
        elif line.startswith("COHERENCE_REASON:"):
            scores["coherence_reason"] = line.split(":", 1)[1].strip()
        elif line.startswith("FALLACY:"):
            scores["fallacy"] = line.split(":", 1)[1].strip()

    scores["total"] = scores["logic"] + scores["evidence"] + scores["coherence"]
    return scores