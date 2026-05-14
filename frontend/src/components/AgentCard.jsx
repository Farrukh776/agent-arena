import { AGENT_CONFIG } from "../hooks/useDebateSocket";

const BORDER_ACTIVE = {
  green:  "border-green-500/60",
  red:    "border-red-500/60",
  purple: "border-purple-500/60",
  amber:  "border-amber-500/60",
};
const BORDER_DONE = {
  green:  "border-green-500/20",
  red:    "border-red-500/20",
  purple: "border-purple-500/20",
  amber:  "border-amber-500/20",
};
const RING = {
  green:  "active-ring-green",
  red:    "active-ring-red",
  purple: "active-ring-purple",
  amber:  "active-ring-amber",
};

export default function AgentCard({ name, data, isActive }) {
  const config    = AGENT_CONFIG[name] || AGENT_CONFIG["Judge"];
  const text      = data?.text      || "";
  const scores    = data?.scores    || null;
  const factCheck = data?.factCheck || null;

  const borderClass = isActive ? BORDER_ACTIVE[config.color] : BORDER_DONE[config.color];
  const ringClass   = isActive ? RING[config.color] : "";

  return (
    <div className={`rounded-2xl border bg-[#0E1421] p-5 transition-all duration-300 animate-fade-slide
      ${borderClass} ${ringClass}`}>

      {/* Agent header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-lg ${config.bg} border ${borderClass}`}>
            {config.emoji}
          </div>
          <div>
            <h3 className={`font-bold text-base leading-none ${config.text}`}>{name}</h3>
            {isActive && (
              <span className="text-[11px] text-gray-500 mt-0.5 block">generating response…</span>
            )}
          </div>
        </div>
        {scores && (
          <div className={`text-xs font-semibold px-2.5 py-1 rounded-full ${config.bg} ${config.text} border ${borderClass}`}>
            {scores.total} / 30
          </div>
        )}
      </div>

      {/* Argument text — only rendered when there's content */}
      {text.length > 0 && (
        <div className={`text-[14px] text-gray-300 leading-relaxed whitespace-pre-wrap
          ${isActive ? `pl-3 border-l-2 ${borderClass}` : ""}`}>
          {text}
          {isActive && <span className={`cursor-blink ${config.text}`} />}
        </div>
      )}

      {/* Streaming cursor when no text yet */}
      {isActive && text.length === 0 && (
        <div className={`pl-3 border-l-2 ${borderClass}`}>
          <span className={`cursor-blink ${config.text}`} />
        </div>
      )}

      {/* Fact check */}
      {factCheck && (
        <div className="mt-4 p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs text-amber-300 leading-relaxed">
          <span className="font-semibold text-amber-400">🔍 Fact Check — </span>
          {factCheck}
        </div>
      )}

      {/* Score breakdown */}
      {scores && (
        <div className="mt-4 pt-4 border-t border-[#1E2A3A]">
          <div className="grid grid-cols-3 gap-2">
            {[
              { label: "Logic",     value: scores.logic,     reason: scores.logic_reason },
              { label: "Evidence",  value: scores.evidence,  reason: scores.evidence_reason },
              { label: "Coherence", value: scores.coherence, reason: scores.coherence_reason },
            ].map(({ label, value, reason }) => (
              <div key={label} title={reason}
                className={`${config.bg} rounded-xl p-3 border ${borderClass} cursor-help`}>
                <div className={`text-xl font-black ${config.text}`}>
                  {value}<span className="text-xs font-normal text-gray-600">/10</span>
                </div>
                <div className="text-[11px] text-gray-500 mt-0.5 font-medium">{label}</div>
              </div>
            ))}
          </div>
          {scores.fallacy && scores.fallacy !== "None" && (
            <div className="mt-3 flex items-center gap-2 text-xs text-orange-400">
              <span className="w-1.5 h-1.5 rounded-full bg-orange-400 flex-shrink-0" />
              Fallacy detected: <span className="font-semibold">{scores.fallacy}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
