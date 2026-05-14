import { AGENT_CONFIG } from "../hooks/useDebateSocket";

const BAR_COLOR = {
  green:  "bg-green-500",
  red:    "bg-red-500",
  purple: "bg-purple-500",
  amber:  "bg-amber-500",
};

export default function ScorePanel({ scores, allStats }) {
  if (!scores || scores.length === 0) return null;

  const totals = {};
  scores.forEach(s => {
    totals[s.agent] = (totals[s.agent] || 0) + s.total;
  });

  const sorted   = Object.entries(totals).sort((a, b) => b[1] - a[1]);
  const maxScore = sorted[0]?.[1] || 1;
  const hasStats = allStats?.some(s => !s.no_data);

  return (
    <div className="card space-y-5 sticky top-24">
      {/* Leaderboard */}
      <div>
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">
          Leaderboard
        </p>
        <div className="space-y-4">
          {sorted.map(([agent, total], i) => {
            const config = AGENT_CONFIG[agent];
            const pct    = Math.round((total / (maxScore * 1.05)) * 100);
            return (
              <div key={agent}>
                <div className="flex justify-between items-center mb-1.5">
                  <div className="flex items-center gap-2">
                    {i === 0 && <span className="text-sm">👑</span>}
                    <span className={`text-sm font-semibold ${config?.text}`}>{agent}</span>
                  </div>
                  <span className="text-xs font-bold text-gray-400 tabular-nums">{total} pts</span>
                </div>
                <div className="h-1.5 bg-[#080B12] rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${BAR_COLOR[config?.color] || "bg-indigo-500"}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* All-time stats */}
      {hasStats && (
        <div className="pt-4 border-t border-[#1E2A3A]">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">
            All-Time Record
          </p>
          <div className="space-y-2.5">
            {allStats.filter(s => !s.no_data).map(stat => {
              const config = AGENT_CONFIG[stat.agent];
              return (
                <div key={stat.agent}
                  className="flex items-center justify-between p-2.5 rounded-xl bg-[#080B12] border border-[#1E2A3A]">
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{config?.emoji}</span>
                    <span className={`text-xs font-semibold ${config?.text}`}>{stat.agent}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-gray-300">{stat.wins}W</div>
                    <div className="text-[10px] text-gray-600">avg {stat.avg_total}/30</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
