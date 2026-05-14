import { AGENT_CONFIG } from "../hooks/useDebateSocket";

export default function VerdictPanel({ verdict, winner }) {
  if (!verdict) return null;

  const config = AGENT_CONFIG[winner] || {};

  const sections = {};
  verdict.split("\n").forEach(line => {
    const idx = line.indexOf(":");
    if (idx > -1) {
      const key = line.slice(0, idx).trim();
      const val = line.slice(idx + 1).trim();
      if (val) sections[key] = val;
    }
  });

  const items = [
    { key: "STRONGEST_ARGUMENT", icon: "💪", label: "Strongest Argument", color: "text-green-400" },
    { key: "WEAKEST_ARGUMENT",   icon: "📉", label: "Weakest Point",       color: "text-red-400"   },
    { key: "KEY_INSIGHT",        icon: "💡", label: "Key Insight",         color: "text-purple-400" },
  ];

  return (
    <div className={`rounded-2xl border bg-[#0E1421] p-5 animate-fade-slide active-ring-amber`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30
                        flex items-center justify-center text-xl">⚖️</div>
        <div>
          <h3 className="font-bold text-lg text-amber-400">Judge's Verdict</h3>
          <p className="text-xs text-gray-500">Final evaluation</p>
        </div>
      </div>

      {/* Winner banner */}
      {winner && (
        <div className={`${config.bg || "bg-amber-500/10"} rounded-xl p-4 mb-5
                         border ${config.border || "border-amber-500/30"} text-center`}>
          <p className="text-xs text-gray-500 mb-1 font-medium uppercase tracking-widest">Winner</p>
          <p className={`text-2xl font-black ${config.text || "text-amber-400"}`}>
            {config.emoji} {winner}
          </p>
          {sections["WINNING_REASON"] && (
            <p className="text-gray-400 text-sm mt-2 leading-relaxed">{sections["WINNING_REASON"]}</p>
          )}
        </div>
      )}

      {/* Detail rows */}
      <div className="space-y-3">
        {items.map(({ key, icon, label, color }) =>
          sections[key] ? (
            <div key={key} className="p-3 rounded-xl bg-[#080B12] border border-[#1E2A3A]">
              <p className={`text-xs font-semibold mb-1 ${color}`}>{icon} {label}</p>
              <p className="text-sm text-gray-300 leading-relaxed">{sections[key]}</p>
            </div>
          ) : null
        )}

        {sections["FINAL_VERDICT"] && (
          <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 mt-2">
            <p className="text-xs font-semibold text-amber-400 mb-1.5">📜 Final Verdict</p>
            <p className="text-sm text-gray-300 leading-relaxed">{sections["FINAL_VERDICT"]}</p>
          </div>
        )}
      </div>
    </div>
  );
}
