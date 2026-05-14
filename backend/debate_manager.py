import json
import asyncio
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


async def run_debate_websocket(topic: str, rounds: int, websocket, cancelled: asyncio.Event):
    """
    cancelled: asyncio.Event set by main.py the moment the client disconnects.
    Checked before every major step — if set, exits immediately without saving.
    """

    async def send(msg_type: str, **kwargs):
        if cancelled.is_set():
            return
        try:
            await websocket.send_text(json.dumps({"type": msg_type, **kwargs}))
        except Exception:
            cancelled.set()

    def is_cancelled():
        return cancelled.is_set()

    try:
        init_db()

        if is_cancelled(): return

        memory_context = get_past_debates(topic)
        if memory_context:
            await send("memory", message="🧠 Memory loaded", memory=memory_context)

        await send("status", message=f"Starting debate: {topic}", topic=topic, rounds=rounds)

        optimist        = create_optimist()
        skeptic         = create_skeptic()
        devils_advocate = create_devils_advocate()
        judge           = JudgeAgent()
        fact_checker    = FactChecker()
        agents          = [optimist, skeptic, devils_advocate]

        debate_context         = f"The debate topic is: '{topic}'\n\nMake your opening argument."
        full_debate_transcript = f"TOPIC: {topic}\n\n"
        all_scores             = []

        for round_num in range(1, rounds + 1):
            if is_cancelled(): return

            await send("status", message=f"Round {round_num} of {rounds}", round=round_num)

            round_arguments = []

            for agent in agents:
                if is_cancelled(): return

                await send("agent_start", agent=agent.name, round=round_num)

                mem        = memory_context if round_num == 1 else ""
                full_reply = ""

                for chunk in agent.respond_streaming(debate_context, memory_context=mem):
                    if is_cancelled(): return
                    await send("token", agent=agent.name, token=chunk, round=round_num)
                    full_reply += chunk

                if is_cancelled(): return

                score          = score_argument(agent.name, full_reply)
                score["round"] = round_num
                all_scores.append(score)

                if fact_checker.contains_factual_claim(full_reply):
                    if is_cancelled(): return
                    await send("status", message=f"🔍 Fact-checking {agent.name}'s claim...")
                    fact_result = fact_checker.check(agent.name, full_reply)
                    await send("fact_check", agent=agent.name, result=fact_result, round=round_num)
                    full_reply += fact_result

                if is_cancelled(): return

                await send("agent_end",
                    agent=agent.name,
                    round=round_num,
                    scores={
                        "logic":            score["logic"],
                        "evidence":         score["evidence"],
                        "coherence":        score["coherence"],
                        "total":            score["total"],
                        "fallacy":          score["fallacy"],
                        "logic_reason":     score["logic_reason"],
                        "evidence_reason":  score["evidence_reason"],
                        "coherence_reason": score["coherence_reason"]
                    }
                )

                round_arguments.append(f"{agent.name}: {full_reply}")
                full_debate_transcript += f"\n[Round {round_num}] {agent.name}:\n{full_reply}\n"

            if is_cancelled(): return

            round_summary  = "\n\n".join(round_arguments)
            debate_context = (
                f"The debate topic is: '{topic}'\n\n"
                f"Arguments so far:\n\n{round_summary}\n\n"
                f"Respond directly to the strongest opposing point above."
            )

            round_scores = [s for s in all_scores if s.get("round") == round_num]
            await send("scores", round=round_num, scores=round_scores)

        if is_cancelled(): return

        await send("status", message="⚖️ Judge is deliberating...")
        verdict = judge.deliver_verdict(topic, full_debate_transcript, all_scores)
        winner  = extract_winner(verdict)

        if is_cancelled(): return

        await send("verdict", verdict=verdict, winner=winner)

        if is_cancelled(): return

        # Only saves if we reach this point — full completion, not stopped
        debate_id = save_debate(topic, rounds, winner, verdict)
        for score in all_scores:
            save_argument(debate_id, score.get("round", 1), score)

        stats = get_all_stats()
        await send("stats", stats=stats)
        await send("done", message="Debate complete", debate_id=debate_id)

    except asyncio.CancelledError:
        return  # stopped — do not save
    except Exception as e:
        if not is_cancelled():
            try:
                await send("error", message=str(e))
            except Exception:
                pass