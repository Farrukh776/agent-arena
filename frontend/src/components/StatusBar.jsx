export default function StatusBar({ status, message, round, totalRounds }) {
  const styles = {
    idle:       { bar: "bg-[#0E1421] border-[#1E2A3A] text-gray-500",     dot: "bg-gray-600" },
    connecting: { bar: "bg-blue-950/40 border-blue-500/20 text-blue-400",  dot: "bg-blue-400 animate-pulse" },
    running:    { bar: "bg-emerald-950/40 border-emerald-500/20 text-emerald-400", dot: "bg-emerald-400 animate-pulse" },
    done:       { bar: "bg-indigo-950/40 border-indigo-500/20 text-indigo-400", dot: "bg-indigo-400" },
    error:      { bar: "bg-red-950/40 border-red-500/20 text-red-400",     dot: "bg-red-400" },
  };
  const s = styles[status] || styles.idle;
  const isLive = status === "running" || status === "connecting";

  return (
    <div className={`rounded-xl border px-4 py-2.5 flex items-center gap-3 text-sm ${s.bar}`}>
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${s.dot}`} />
      <span className="flex-1 font-medium">{message || "Ready"}</span>
      {isLive && round > 0 && (
        <div className="flex items-center gap-2 text-xs font-semibold opacity-70">
          <span>Round {round} / {totalRounds}</span>
          <div className="flex gap-1">
            {Array.from({ length: totalRounds }).map((_, i) => (
              <div key={i} className={`h-1 w-6 rounded-full transition-all duration-500
                ${i < round ? "bg-current" : "bg-current opacity-20"}`} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
