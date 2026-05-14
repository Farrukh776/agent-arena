import { useState, useRef, useCallback } from "react";

const WS_URL = "wss://agent-arena-g2wy.onrender.com/debate";

export const AGENT_CONFIG = {
  "Optimist":         { color: "green",  emoji: "🟢", border: "border-green-500",  text: "text-green-400",  bg: "bg-green-500/10"  },
  "Skeptic":          { color: "red",    emoji: "🔴", border: "border-red-500",    text: "text-red-400",    bg: "bg-red-500/10"    },
  "Devil's Advocate": { color: "purple", emoji: "🟣", border: "border-purple-500", text: "text-purple-400", bg: "bg-purple-500/10" },
  "Judge":            { color: "amber",  emoji: "⚖️", border: "border-amber-500",  text: "text-amber-400",  bg: "bg-amber-500/10"  },
};

export function useDebateSocket() {
  const [status, setStatus]             = useState("idle");
  const [statusMsg, setStatusMsg]       = useState("");
  const [rounds, setRounds]             = useState({});
  const [activeAgent, setActiveAgent]   = useState(null);
  const [currentRound, setCurrentRound] = useState(0);
  const [totalRounds, setTotalRounds]   = useState(2);
  const [verdict, setVerdict]           = useState(null);
  const [winner, setWinner]             = useState(null);
  const [allStats, setAllStats]         = useState([]);
  const [scores, setScores]             = useState([]);
  const [memory, setMemory]             = useState(null);

  const wsRef   = useRef(null);
  const stopped = useRef(false);

  const resetState = useCallback(() => {
    setRounds({});
    setActiveAgent(null);
    setCurrentRound(0);
    setVerdict(null);
    setWinner(null);
    setAllStats([]);
    setScores([]);
    setStatusMsg("");
    setMemory(null);
    stopped.current = false;
  }, []);

  const startDebate = useCallback((topic, numRounds) => {
    // Hard-stop any existing connection
    stopped.current = true;
    if (wsRef.current) {
      wsRef.current.onmessage = null;
      wsRef.current.onclose   = null;
      wsRef.current.onerror   = null;
      wsRef.current.close();
      wsRef.current = null;
    }

    // Small delay so close fires before we reset
    setTimeout(() => {
      stopped.current = false;
      resetState();
      setTotalRounds(numRounds);
      setStatus("connecting");

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        if (stopped.current) { ws.close(); return; }
        setStatus("running");
        ws.send(JSON.stringify({ topic, rounds: numRounds }));
      };

      ws.onmessage = (event) => {
        if (stopped.current) return;
        const data = JSON.parse(event.data);

        switch (data.type) {

          case "status":
            setStatusMsg(data.message);
            if (data.round) setCurrentRound(data.round);
            break;

          // Memory only loads when backend explicitly sends "memory" type
          case "memory":
            setMemory(data.memory);
            break;

          case "agent_start":
            setActiveAgent(data.agent);
            setCurrentRound(data.round);
            setStatusMsg(`Round ${data.round} — ${data.agent} is arguing…`);
            setRounds(prev => ({
              ...prev,
              [data.round]: {
                ...prev[data.round],
                [data.agent]: { text: "", scores: null, factCheck: null }
              }
            }));
            break;

          case "token":
            setRounds(prev => {
              const r = prev[data.round] || {};
              const a = r[data.agent]    || { text: "", scores: null, factCheck: null };
              return {
                ...prev,
                [data.round]: { ...r, [data.agent]: { ...a, text: a.text + data.token } }
              };
            });
            break;

          case "agent_end":
            setActiveAgent(null);
            setRounds(prev => {
              const r = prev[data.round] || {};
              const a = r[data.agent]    || {};
              return {
                ...prev,
                [data.round]: { ...r, [data.agent]: { ...a, scores: data.scores } }
              };
            });
            setScores(prev => [...prev, { agent: data.agent, round: data.round, ...data.scores }]);
            break;

          case "fact_check":
            setRounds(prev => {
              const roundNum = data.round || currentRound;
              const r = prev[roundNum] || {};
              const a = r[data.agent]  || {};
              return {
                ...prev,
                [roundNum]: { ...r, [data.agent]: { ...a, factCheck: data.result } }
              };
            });
            break;

          case "verdict":
            setVerdict(data.verdict);
            setWinner(data.winner);
            setStatusMsg("⚖️ Judge has delivered the verdict!");
            break;

          case "stats":
            setAllStats(data.stats);
            break;

          case "done":
            setStatus("done");
            setStatusMsg("Debate complete!");
            setActiveAgent(null);
            break;

          case "error":
            setStatus("error");
            setStatusMsg(`Error: ${data.message}`);
            break;
        }
      };

      ws.onerror = () => {
        if (stopped.current) return;
        setStatus("error");
        setStatusMsg("Connection failed — is the backend running on port 8000?");
      };

      ws.onclose = () => {
        if (stopped.current) return;
        setStatus(s => s === "running" ? "done" : s);
      };
    }, 50);
  }, [resetState]);

  const stopDebate = useCallback(() => {
    stopped.current = true;
    if (wsRef.current) {
      wsRef.current.onmessage = null;
      wsRef.current.onclose   = null;
      wsRef.current.onerror   = null;
      wsRef.current.close();
      wsRef.current = null;
    }
    resetState();
    setStatus("idle");
  }, [resetState]);

  return {
    status, statusMsg, rounds, activeAgent,
    currentRound, totalRounds, verdict, winner,
    allStats, scores, memory, startDebate, stopDebate
  };
}
