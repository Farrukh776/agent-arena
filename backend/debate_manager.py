import json
from agents.debate_agents import create_optimist, create_skeptic, create_devils_advocate
from agents.judge_agent import JudgeAgent
from agents.fact_checker import FactChecker
from utils.scorer import score_argument
from memory.debate_memory import (
    init_db, save_debate, save_argument,
    get_past_debates, get_all_stats
)


def extract_winner(verdict: str) -> str:
    for line in verdict.split("\n"):
        if line.startswith("WINNER:"):
            return line.split(":", 1)[1].strip()
    return "Unknown"


async def run_debate_websocket(topic: str, rounds: int, websocket):
    """
    Full debate orchestrator for WebSocket connections.
    
    Instead of print(), we use websocket.send_text() to push
    structured JSON messages to the React frontend in real time.
    
    Message types we send:
    - "status"      : system messages (round started, etc.)
    - "agent_start" : agent is about to speak
    - "token"       : single streaming text chunk
    - "agent_end"   : agent finished, includes scores
    - "fact_check"  : fact checker result
    - "scores"      : round score summary
    - "verdict"     : judge's final verdict
    - "stats"       : all-time agent stats
    - "done"        : debate is complete
    - "error"       : something went wrong
    """

    async def send(msg_type: str, **kwargs):
        """Helper to send structured JSON over WebSocket."""
        await websocket.send_text(json.dumps({"type": msg_type, **kwargs}))

    try:
        init_db()

        # Load memory
        memory_context = get_past_debates(topic)
        if memory_context:
            await send("status", message="🧠 Memory loaded — agents aware of past debates", memory=memory_context)

        await send("status", message=f"Starting debate: {topic}", topic=topic, rounds=rounds)

        # Create agents
        optimist = create_optimist()
        skeptic = create_skeptic()
        devils_advocate = create_devils_advocate()
        judge = JudgeAgent()
        fact_checker = FactChecker()
        agents = [optimist, skeptic, devils_advocate]

        debate_context = f"The debate topic is: '{topic}'\n\nMake your opening argument."
        full_debate_transcript = f"TOPIC: {topic}\n\n"
        all_scores = []

        for round_num in range(1, rounds + 1):
            await send("status", message=f"Round {round_num} of {rounds}", round=round_num)

            round_arguments = []

            for agent in agents:
                # Signal agent is starting
                await send("agent_start", agent=agent.name, round=round_num)

                mem = memory_context if round_num == 1 else ""

                # Stream the response token by token
                full_reply = ""
                for chunk in agent.respond_streaming(debate_context, memory_context=mem):
                    await send("token", agent=agent.name, token=chunk)
                    full_reply += chunk

                # Score the completed argument
                score = score_argument(agent.name, full_reply)
                score["round"] = round_num
                all_scores.append(score)

                # Fact check if needed
                fact_result = None
                if fact_checker.contains_factual_claim(full_reply):
                    await send("status", message=f"🔍 Fact-checking {agent.name}'s claim...")
                    fact_result = fact_checker.check(agent.name, full_reply)
                    await send("fact_check", agent=agent.name, result=fact_result)
                    full_reply += fact_result

                # Send agent done + scores
                await send("agent_end",
                    agent=agent.name,
                    round=round_num,
                    scores={
                        "logic": score["logic"],
                        "evidence": score["evidence"],
                        "coherence": score["coherence"],
                        "total": score["total"],
                        "fallacy": score["fallacy"],
                        "logic_reason": score["logic_reason"],
                        "evidence_reason": score["evidence_reason"],
                        "coherence_reason": score["coherence_reason"]
                    }
                )

                round_arguments.append(f"{agent.name}: {full_reply}")
                full_debate_transcript += f"\n[Round {round_num}] {agent.name}:\n{full_reply}\n"

            # Update context for next round
            round_summary = "\n\n".join(round_arguments)
            debate_context = (
                f"The debate topic is: '{topic}'\n\n"
                f"Arguments so far:\n\n{round_summary}\n\n"
                f"Respond directly to the strongest opposing point above."
            )

            # Send round score summary
            round_scores = [s for s in all_scores if s.get("round") == round_num]
            await send("scores", round=round_num, scores=round_scores)

        # Judge verdict
        await send("status", message="⚖️ Judge is deliberating...")
        verdict = judge.deliver_verdict(topic, full_debate_transcript, all_scores)
        winner = extract_winner(verdict)

        await send("verdict", verdict=verdict, winner=winner)

        # Save to memory
        debate_id = save_debate(topic, rounds, winner, verdict)
        for score in all_scores:
            save_argument(debate_id, score.get("round", 1), score)

        # Send all-time stats
        stats = get_all_stats()
        await send("stats", stats=stats)

        await send("done", message="Debate complete", debate_id=debate_id)

    except Exception as e:
        await send("error", message=str(e))
        raise e