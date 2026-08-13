import React, { useState, useEffect } from "react";
import interviewService from "../../services/interviewService";

const InterviewHistory = ({ onViewSessionReport, onStartNew }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await interviewService.getHistory();
      setHistory(data || []);
    } catch (err) {
      setError(err.message || "Failed to load interview history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (sessionId) => {
    if (!window.confirm("Are you sure you want to delete this interview record?")) {
      return;
    }
    try {
      setDeletingId(sessionId);
      await interviewService.deleteInterview(sessionId);
      setHistory((prev) => prev.filter((item) => item.id !== sessionId));
    } catch (err) {
      alert(err.message || "Failed to delete interview record.");
    } finally {
      setDeletingId(null);
    }
  };

  const getStatusBadge = (status, score) => {
    if (status === "completed") {
      return (
        <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          Completed ({score ? `${score}/100` : "Passed"})
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
        Active
      </span>
    );
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            Interview History
          </h2>
          <p className="text-slate-400 text-xs mt-0.5">
            Review past practice sessions and track your progress over time.
          </p>
        </div>

        <button
          type="button"
          onClick={onStartNew}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-xs shadow-glow hover:opacity-95 transition-all"
        >
          + New Practice Session
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
          {error}
        </div>
      )}

      {loading ? (
        <div className="glass-panel p-12 text-center rounded-2xl bg-surface-900/80">
          <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-slate-400 text-xs font-medium">
            Loading interview history...
          </p>
        </div>
      ) : history.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl bg-surface-900/80 space-y-4">
          <div className="text-3xl">🎤</div>
          <h3 className="text-lg font-bold text-white">No Interviews Recorded Yet</h3>
          <p className="text-slate-400 text-xs max-w-sm mx-auto">
            Start your first AI mock interview session to evaluate your skills and receive tailored performance feedback.
          </p>
          <button
            type="button"
            onClick={onStartNew}
            className="px-6 py-3 rounded-xl bg-indigo-600 text-white text-xs font-bold shadow-glow hover:bg-indigo-500 transition-all"
          >
            Start Practice Interview
          </button>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl bg-surface-900/90 border border-slate-800/80 overflow-hidden">
          <div className="divide-y divide-slate-800/80">
            {history.map((session) => (
              <div
                key={session.id}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-800/30 transition-all"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-bold text-white text-sm">
                      {session.target_role}
                    </h4>
                    {getStatusBadge(session.status, session.overall_score)}
                  </div>

                  <div className="flex items-center space-x-3 text-xs text-slate-400">
                    <span className="capitalize">{session.interview_type}</span>
                    <span>•</span>
                    <span className="capitalize">{session.difficulty}</span>
                    <span>•</span>
                    <span>{session.total_questions} Questions</span>
                    <span>•</span>
                    <span>
                      {new Date(session.created_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    type="button"
                    onClick={() => onViewSessionReport(session.id)}
                    className="px-4 py-2 rounded-xl bg-indigo-950/50 border border-indigo-500/30 text-indigo-300 font-semibold text-xs hover:bg-indigo-900/50 transition-all"
                  >
                    View Report
                  </button>

                  <button
                    type="button"
                    disabled={deletingId === session.id}
                    onClick={() => handleDelete(session.id)}
                    className="px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 font-semibold text-xs transition-all disabled:opacity-40"
                  >
                    {deletingId === session.id ? "..." : "Delete"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewHistory;
