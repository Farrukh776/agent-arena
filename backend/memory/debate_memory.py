import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "debates.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS debates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            rounds INTEGER,
            winner TEXT,
            verdict TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS arguments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debate_id INTEGER,
            round_num INTEGER,
            agent_name TEXT,
            argument TEXT,
            logic_score INTEGER,
            evidence_score INTEGER,
            coherence_score INTEGER,
            total_score INTEGER,
            fallacy TEXT,
            FOREIGN KEY (debate_id) REFERENCES debates(id)
        )
    """)
    conn.commit()
    conn.close()


def save_debate(topic: str, rounds: int, winner: str, verdict: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO debates (topic, rounds, winner, verdict, created_at) VALUES (?, ?, ?, ?, ?)",
        (topic, rounds, winner, verdict, datetime.now().isoformat())
    )
    debate_id = c.lastrowid
    conn.commit()
    conn.close()
    return debate_id


def save_argument(debate_id: int, round_num: int, score: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO arguments 
        (debate_id, round_num, agent_name, argument, logic_score, evidence_score, coherence_score, total_score, fallacy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        debate_id,
        round_num,
        score["agent"],
        score["argument_preview"],
        score["logic"],
        score["evidence"],
        score["coherence"],
        score["total"],
        score["fallacy"]
    ))
    conn.commit()
    conn.close()


def get_past_debates(topic: str, limit: int = 3) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    keywords = topic.split()[:3]
    query = "SELECT topic, winner, verdict, created_at FROM debates WHERE " + \
            " OR ".join(["topic LIKE ?" for _ in keywords]) + \
            " ORDER BY created_at DESC LIMIT ?"
    params = [f"%{kw}%" for kw in keywords] + [limit]
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    if not rows:
        return ""

    formatted = ["[MEMORY: Past debates on similar topics]"]
    for row in rows:
        formatted.append(
            f"- Topic: '{row[0]}' | Winner: {row[1]} | Date: {row[3][:10]}\n"
            f"  Verdict summary: {row[2][:200] if row[2] else 'N/A'}..."
        )
    return "\n".join(formatted)


def get_agent_stats(agent_name: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT 
            COUNT(*) as total_args,
            AVG(logic_score) as avg_logic,
            AVG(evidence_score) as avg_evidence,
            AVG(coherence_score) as avg_coherence,
            AVG(total_score) as avg_total
        FROM arguments WHERE agent_name = ?
    """, (agent_name,))
    row = c.fetchone()
    c.execute("SELECT COUNT(*) FROM debates WHERE winner = ?", (agent_name,))
    wins = c.fetchone()[0]
    conn.close()

    if not row or row[0] == 0:
        return {"agent": agent_name, "no_data": True}

    return {
        "agent": agent_name,
        "total_arguments": row[0],
        "wins": wins,
        "avg_logic": round(row[1], 1),
        "avg_evidence": round(row[2], 1),
        "avg_coherence": round(row[3], 1),
        "avg_total": round(row[4], 1)
    }


def get_all_stats() -> list:
    agents = ["Optimist", "Skeptic", "Devil's Advocate"]
    return [get_agent_stats(a) for a in agents]