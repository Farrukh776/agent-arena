import { useDebateSocket, AGENT_CONFIG } from "./hooks/useDebateSocket";
import TopicForm    from "./components/TopicForm";
import AgentCard    from "./components/AgentCard";
import ScorePanel   from "./components/ScorePanel";
import VerdictPanel from "./components/VerdictPanel";
import StatusBar    from "./components/StatusBar";

const AGENT_NAMES = ["Optimist", "Skeptic", "Devil's Advocate"];

export default function App() {
  const {
    status, statusMsg, rounds, activeAgent,
    currentRound, totalRounds, verdict, winner,
    allStats, scores, memory, startDebate, stopDebate
  } = useDebateSocket();

  const isActive  = status === "running" || status === "connecting";
  const roundNums = Object.keys(rounds).map(Number).sort((a, b) => a - b);
  const hasContent = roundNums.length > 0;

  return (
    <div className="min-h-screen bg-[#080B12]">

      {/* ── Header ── */}
      <header className="glass border-b border-white/5 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30
                            flex items-center justify-center text-base">🎭</div>
            <div>
              <h1 className="text-lg font-black text-gradient leading-none">AgentArena</h1>
              <p className="text-[10px] text-gray-600 mt-0.5">Multi-Agent AI Debate System</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-gray-600">
            <span className={`w-1.5 h-1.5 rounded-full transition-colors
              ${isActive ? "bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]" : "bg-gray-700"}`} />
            {isActive ? <span className="text-emerald-500">Live</span> : "Idle"}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">

        {/* Topic form */}
        <TopicForm onStart={startDebate} onStop={stopDebate} status={status} />

        {/* Memory banner — only appears when backend confirms past debate exists */}
        {memory && (
          <div className="max-w-3xl mx-auto rounded-xl border border-indigo-500/20
                          bg-indigo-950/20 px-4 py-3">
            <div className="flex items-center gap-2 text-sm text-indigo-300 font-medium">
              <span>🧠</span>
              <span>Memory loaded — agents are aware of past debates on this topic</span>
            </div>
            <details className="mt-2">
              <summary className="text-xs text-indigo-500 cursor-pointer hover:text-indigo-400 transition-colors">
                View context
              </summary>
              <pre className="mt-2 text-xs text-gray-500 whitespace-pre-wrap leading-relaxed">
                {memory}
              </pre>
            </details>
          </div>
        )}

        {/* Status bar */}
        {(isActive || status === "done" || status === "error") && (
          <div className="max-w-3xl mx-auto">
            <StatusBar
              status={status}
              message={statusMsg}
              round={currentRound}
              totalRounds={totalRounds}
            />
          </div>
        )}

        {/* ── Debate content ── */}
        {hasContent && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">

            {/* Left 2/3 — rounds */}
            <div className="lg:col-span-2 space-y-10">
              {roundNums.map(roundNum => {
                const roundData = rounds[roundNum] || {};

                return (
                  <div key={roundNum} className="space-y-4">

                    {/* Round divider heading */}
                    <div className="flex items-center gap-4">
                      <div className="h-px flex-1 bg-gradient-to-r from-transparent to-[#1E2A3A]" />
                      <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full border text-xs font-bold
                        transition-all duration-300
                        ${currentRound === roundNum && isActive
                          ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-400"
                          : "border-[#1E2A3A] bg-[#0E1421] text-gray-500"
                        }`}>
                        {currentRound === roundNum && isActive && (
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                        )}
                        Round {roundNum}
                      </div>
                      <div className="h-px flex-1 bg-gradient-to-l from-transparent to-[#1E2A3A]" />
                    </div>

                    {/* Agent cards — only render when agent has data */}
                    {AGENT_NAMES.map(name => {
                      const agentData = roundData[name];
                      // Only show card if agent has started (has an entry in this round)
                      if (!agentData) return null;
                      return (
                        <AgentCard
                          key={name}
                          name={name}
                          data={agentData}
                          isActive={activeAgent === name && currentRound === roundNum}
                        />
                      );
                    })}
                  </div>
                );
              })}

              {/* Verdict */}
              {verdict && (
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="h-px flex-1 bg-gradient-to-r from-transparent to-[#1E2A3A]" />
                    <div className="px-4 py-1.5 rounded-full border border-amber-500/30
                                    bg-amber-500/5 text-amber-400 text-xs font-bold">
                      Final Verdict
                    </div>
                    <div className="h-px flex-1 bg-gradient-to-l from-transparent to-[#1E2A3A]" />
                  </div>
                  <VerdictPanel verdict={verdict} winner={winner} />
                </div>
              )}
            </div>

            {/* Right 1/3 — sticky score panel */}
            <div>
              <ScorePanel scores={scores} allStats={allStats} />
            </div>
          </div>
        )}

        {/* Empty state */}
        {!hasContent && status === "idle" && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-20 h-20 rounded-2xl bg-[#0E1421] border border-[#1E2A3A]
                            flex items-center justify-center text-4xl mb-6">🎭</div>
            <h2 className="text-xl font-bold text-gray-300 mb-2">Ready to debate</h2>
            <p className="text-sm text-gray-600 max-w-sm">
              Enter any topic above. Three AI agents — Optimist, Skeptic, and Devil's Advocate —
              will argue across multiple rounds with real-time web search and scoring.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
