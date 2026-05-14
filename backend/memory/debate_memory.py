import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "debates.db")

# Words too common to use as search keywords
STOPWORDS = {
    "is", "are", "was", "were", "will", "would", "could", "should",
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "that", "this", "it", "be",
    "do", "does", "did", "has", "have", "had", "not", "more", "than",
    "already", "just", "also", "very", "too", "so", "yet", "still",
    "about", "can", "may", "might", "its", "their", "our", "your"
}


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
    """
    Only returns memory if a past debate topic is a strong match.
    
    Strong match = at least 2 meaningful keywords overlap between
    the current topic and a past topic. This prevents common words
    like 'is', 'will', 'the' from triggering false memory loads.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Extract meaningful keywords — strip stopwords, min 4 chars
    def extract_keywords(text):
        words = text.lower().split()
        return {w.strip(".,?!") for w in words
                if w not in STOPWORDS and len(w) >= 4}

    current_keywords = extract_keywords(topic)

    # Need at least 2 meaningful keywords to even attempt matching
    if len(current_keywords) < 2:
        conn.close()
        return ""

    # Fetch recent debates
    c.execute("SELECT topic, winner, verdict, created_at FROM debates ORDER BY created_at DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()

    if not rows:
        return ""

    matched = []
    for row in rows:
        past_keywords = extract_keywords(row[0])
        overlap = current_keywords & past_keywords

        # Require at least 2 keyword matches to count as related
        if len(overlap) >= 2:
            matched.append(row)
            if len(matched) >= limit:
                break

    if not matched:
        return ""

    formatted = ["[MEMORY: Past debates on similar topics]"]
    for row in matched:
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