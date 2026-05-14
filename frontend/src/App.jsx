import { useState } from "react";
import { useDebateSocket, AGENT_CONFIG } from "./hooks/useDebateSocket";
import TopicForm    from "./components/TopicForm";
import AgentCard    from "./components/AgentCard";
import ScorePanel   from "./components/ScorePanel";
import VerdictPanel from "./components/VerdictPanel";
import StatusBar    from "./components/StatusBar";

const AGENT_NAMES = ["Optimist", "Skeptic", "Devil's Advocate"];

const USE_CASES = [
  {
    icon: "🚀",
    label: "Startup Decisions",
    examples: [
      "We should pivot from B2C to B2B",
      "Raising a seed round now is the right move",
      "We should build in public from day one",
    ]
  },
  {
    icon: "📈",
    label: "Investment & Markets",
    examples: [
      "AI stocks are overvalued in 2025",
      "Real estate is still the safest long-term investment",
      "Crypto will replace traditional banking by 2030",
    ]
  },
  {
    icon: "🎓",
    label: "Academic & Policy",
    examples: [
      "Universal basic income would reduce poverty",
      "Social media should be regulated like tobacco",
      "Remote work is more productive than office work",
    ]
  },
  {
    icon: "⚙️",
    label: "Tech & Product",
    examples: [
      "We should rewrite our app in a new framework",
      "AI will replace software engineers by 2027",
      "Open source always beats proprietary software",
    ]
  },
];

export default function App() {
  const {
    status, statusMsg, rounds, activeAgent,
    currentRound, totalRounds, verdict, winner,
    allStats, scores, memory, startDebate, stopDebate
  } = useDebateSocket();

  const [prefillTopic, setPrefillTopic] = useState("");

  const isActive   = status === "running" || status === "connecting";
  const roundNums  = Object.keys(rounds).map(Number).sort((a, b) => a - b);
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
              <p className="text-[10px] text-gray-600 mt-0.5">AI-powered decision stress-testing</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-gray-600">
            <span className={`w-1.5 h-1.5 rounded-full transition-colors
              ${isActive
                ? "bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.6)]"
                : "bg-gray-700"}`} />
            {isActive ? <span className="text-emerald-500">Live</span> : "Idle"}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">

        {/* Topic form */}
        <TopicForm
          onStart={startDebate}
          onStop={stopDebate}
          status={status}
          prefillTopic={prefillTopic}
        />

        {/* Memory banner */}
        {memory && (
          <div className="max-w-3xl mx-auto rounded-xl border border-indigo-500/20 bg-indigo-950/20 px-4 py-3">
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

                    {/* Round heading */}
                    <div className="flex items-center gap-4">
                      <div className="h-px flex-1 bg-gradient-to-r from-transparent to-[#1E2A3A]" />
                      <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full border
                        text-xs font-bold transition-all duration-300
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

                    {/* Agent cards — only render when agent has started */}
                    {AGENT_NAMES.map(name => {
                      const agentData = roundData[name];
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

            {/* Right 1/3 — scores */}
            <div>
              <ScorePanel scores={scores} allStats={allStats} />
            </div>
          </div>
        )}

        {/* ── Empty state with use cases ── */}
        {!hasContent && status === "idle" && (
          <div className="max-w-3xl mx-auto py-8 space-y-8">
            <div className="text-center">
              <h2 className="text-xl font-bold text-gray-300 mb-2">
                Stress-test any idea before you commit to it
              </h2>
              <p className="text-sm text-gray-500 max-w-lg mx-auto">
                Three AI agents attack your topic from every angle — with real web search,
                scored arguments, and a judge's verdict. Click any example to get started.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {USE_CASES.map(({ icon, label, examples }) => (
                <div key={label} className="card card-hover space-y-1">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">{icon}</span>
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                      {label}
                    </span>
                  </div>
                  {examples.map(ex => (
                    <button
                      key={ex}
                      onClick={() => setPrefillTopic(ex)}
                      className="w-full text-left text-xs text-gray-500 hover:text-gray-200
                                 hover:bg-[#1A2535] px-3 py-2.5 rounded-lg transition-all duration-150
                                 border border-transparent hover:border-[#2A3A50]"
                    >
                      "{ex}"
                    </button>
                  ))}
                </div>
              ))}
            </div>

            {/* How it works */}
            <div className="pt-4 border-t border-[#1E2A3A]">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest text-center mb-4">
                How it works
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { step: "1", icon: "💬", text: "Enter any topic or decision" },
                  { step: "2", icon: "🤖", text: "3 AI agents debate with web search" },
                  { step: "3", icon: "📊", text: "Arguments scored on logic & evidence" },
                  { step: "4", icon: "⚖️", text: "Judge delivers structured verdict" },
                ].map(({ step, icon, text }) => (
                  <div key={step}
                    className="flex flex-col items-center text-center p-3 rounded-xl
                               bg-[#0E1421] border border-[#1E2A3A]">
                    <span className="text-2xl mb-2">{icon}</span>
                    <p className="text-xs text-gray-500 leading-relaxed">{text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
