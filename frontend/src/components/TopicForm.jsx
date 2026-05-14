import { useState } from "react";

export default function TopicForm({ onStart, onStop, status }) {
  const [topic, setTopic]   = useState("");
  const [rounds, setRounds] = useState(2);
  const isRunning = status === "running" || status === "connecting";

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    onStart(topic.trim(), rounds);
  };

  return (
    <div className="card max-w-3xl mx-auto">
      <label className="block text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">
        Debate Topic
      </label>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <textarea
          className="w-full bg-[#080B12] border border-[#1E2A3A] rounded-xl px-4 py-3
                     text-gray-100 placeholder-gray-600 resize-none focus:outline-none
                     focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/20
                     transition-all text-sm leading-relaxed"
          rows={2}
          placeholder="e.g. Social media is doing more harm than good to democracy…"
          value={topic}
          onChange={e => setTopic(e.target.value)}
          disabled={isRunning}
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
              Rounds
            </span>
            <div className="flex gap-1.5">
              {[1, 2, 3, 4].map(r => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRounds(r)}
                  disabled={isRunning}
                  className={`w-9 h-9 rounded-lg text-sm font-bold transition-all duration-150
                    ${rounds === r
                      ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/25"
                      : "bg-[#080B12] border border-[#1E2A3A] text-gray-500 hover:text-gray-300 hover:border-[#2A3A50]"
                    } disabled:opacity-40`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {isRunning && (
              <button type="button" onClick={onStop} className="btn-danger">
                Stop Debate
              </button>
            )}
            <button
              type="submit"
              disabled={!topic.trim() || isRunning}
              className="btn-primary"
            >
              {status === "connecting" ? "Connecting…" : "Start Debate"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
