import sys
from agents.debate_agents import create_optimist, create_skeptic, create_devils_advocate
from agents.judge_agent import JudgeAgent
from agents.fact_checker import FactChecker
from utils.scorer import score_argument
from memory.debate_memory import (
    init_db, save_debate, save_argument,
    get_past_debates, get_all_stats
)


def extract_winner(verdict: str) -> str:
    """Pull winner name from judge verdict text."""
    for line in verdict.split("\n"):
        if line.startswith("WINNER:"):
            return line.split(":", 1)[1].strip()
    return "Unknown"


def run_debate(topic: str, rounds: int = 2):

    # Initialize database on every run
    init_db()

    print("\n" + "="*60)
    print(f"  AgentArena — Topic: {topic}")
    print(f"  Rounds: {rounds}")
    print("="*60 + "\n")

    # Check memory for past debates on this topic
    memory_context = get_past_debates(topic)
    if memory_context:
        print("🧠 Memory loaded — agents aware of past debates\n")
        print(memory_context)
        print()

    # Initialize all agents
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
        print(f"\n{'─'*60}")
        print(f"  ROUND {round_num}")
        print(f"{'─'*60}\n")

        round_arguments = []

        for agent in agents:
            print(f"  [{agent.name.upper()}] arguing...\n")

            # Pass memory context only in round 1 opening arguments
            mem = memory_context if round_num == 1 else ""
            reply = agent.respond(debate_context, memory_context=mem)
            print(f"{reply}\n")

            # Score this argument
            score = score_argument(agent.name, reply)
            score["round"] = round_num
            all_scores.append(score)

            print(
                f"  📊 Scores — Logic: {score['logic']}/10 | "
                f"Evidence: {score['evidence']}/10 | "
                f"Coherence: {score['coherence']}/10 | "
                f"Total: {score['total']}/30"
            )
            if score['fallacy'] != "None":
                print(f"  ⚠️  Fallacy detected: {score['fallacy']}")

            # Fact-check if needed
            if fact_checker.contains_factual_claim(reply):
                print(f"\n  🔍 Fact-checking {agent.name}'s claim...")
                fact_result = fact_checker.check(agent.name, reply)
                print(fact_result)
                reply += fact_result

            print(f"\n{'·'*50}\n")

            round_arguments.append(f"{agent.name}: {reply}")
            full_debate_transcript += f"\n[Round {round_num}] {agent.name}:\n{reply}\n"

        round_summary = "\n\n".join(round_arguments)
        debate_context = (
            f"The debate topic is: '{topic}'\n\n"
            f"Arguments so far:\n\n{round_summary}\n\n"
            f"Respond directly to the strongest opposing point above."
        )

    # Final scores
    print(f"\n{'='*60}")
    print("  FINAL SCORES")
    print(f"{'='*60}")

    agent_totals = {}
    for s in all_scores:
        name = s['agent']
        agent_totals[name] = agent_totals.get(name, 0) + s['total']

    for agent_name, total in sorted(agent_totals.items(), key=lambda x: -x[1]):
        print(f"  {agent_name}: {total} points total")

    # Judge verdict
    print(f"\n{'='*60}")
    print("  JUDGE'S VERDICT")
    print(f"{'='*60}\n")

    verdict = judge.deliver_verdict(topic, full_debate_transcript, all_scores)
    print(verdict)

    # Save to memory
    winner = extract_winner(verdict)
    debate_id = save_debate(topic, rounds, winner, verdict)

    for score in all_scores:
        save_argument(debate_id, score.get("round", 1), score)

    print(f"\n💾 Debate saved to memory (ID: {debate_id})")

    # Show all-time agent stats
    print(f"\n{'='*60}")
    print("  ALL-TIME AGENT STATS")
    print(f"{'='*60}")
    for stat in get_all_stats():
        if stat.get("no_data"):
            print(f"  {stat['agent']}: No data yet")
        else:
            print(
                f"  {stat['agent']} — "
                f"Args: {stat['total_arguments']} | "
                f"Wins: {stat['wins']} | "
                f"Avg Total: {stat['avg_total']}/30"
            )

    print(f"\n{'='*60}")
    print("  DEBATE COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Artificial Intelligence will do more good than harm for humanity"

    run_debate(topic, rounds=2)