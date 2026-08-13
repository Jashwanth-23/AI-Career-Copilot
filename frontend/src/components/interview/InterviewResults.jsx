import React from "react";
import { Link } from "react-router-dom";

const InterviewResults = ({
  session,
  reportData,
  onPracticeAgain,
  onViewHistory,
}) => {
  const report = reportData?.report || session?.final_report || {};
  const overallScore = session?.overall_score ?? report.overall_score ?? 80;
  const rating = session?.performance_rating || report.performance_rating || "Strong";

  const getRatingBadge = (rat) => {
    if (rat === "Excellent") return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
    if (rat === "Strong") return "bg-indigo-500/20 text-indigo-300 border-indigo-500/40";
    if (rat === "Satisfactory") return "bg-amber-500/20 text-amber-300 border-amber-500/40";
    return "bg-rose-500/20 text-rose-300 border-rose-500/40";
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4 animate-fade-in">
      {/* Header Banner */}
      <div className="glass-panel p-8 rounded-2xl bg-gradient-to-r from-indigo-950/60 via-surface-900 to-purple-950/40 border border-indigo-500/30 shadow-glow relative overflow-hidden space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-bold uppercase tracking-wider">
              <span>🎉 Interview Completed</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              AI Mock Interview Report
            </h1>
            <p className="text-slate-300 text-sm">
              Target Role: <strong className="text-white">{session?.target_role || "Position"}</strong> • {session?.interview_type || "Technical"} ({session?.difficulty || "Medium"})
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-center p-4 rounded-2xl bg-surface-950/80 border border-indigo-500/30 min-w-[120px]">
              <span className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Overall Score
              </span>
              <span className="text-4xl font-extrabold text-white">
                {overallScore}
              </span>
              <span className="text-xs text-slate-400 font-semibold">/100</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3 pt-2">
          <span className="text-xs text-slate-400 font-semibold uppercase">Performance Rating:</span>
          <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getRatingBadge(rating)}`}>
            {rating}
          </span>
        </div>
      </div>

      {/* Category Score Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl bg-surface-900/90 border border-slate-800 text-center space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Technical Score
          </span>
          <div className="text-2xl font-extrabold text-white">
            {report.technical_score ?? overallScore}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl bg-surface-900/90 border border-slate-800 text-center space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Problem Solving
          </span>
          <div className="text-2xl font-extrabold text-white">
            {report.problem_solving_score ?? overallScore}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl bg-surface-900/90 border border-slate-800 text-center space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Communication
          </span>
          <div className="text-2xl font-extrabold text-white">
            {report.communication_score ?? overallScore}
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl bg-surface-900/90 border border-slate-800 text-center space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Role Readiness
          </span>
          <div className="text-2xl font-extrabold text-white">
            {report.role_readiness_score ?? overallScore}
          </div>
        </div>
      </div>

      {/* Strengths & Growth Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths */}
        <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
          <h3 className="text-lg font-bold text-emerald-400 flex items-center space-x-2">
            <span>✓ Candidate Strengths</span>
          </h3>
          <ul className="space-y-3 text-sm text-slate-300">
            {report.strengths && report.strengths.length > 0 ? (
              report.strengths.map((st, idx) => (
                <li key={idx} className="flex items-start space-x-2.5">
                  <span className="text-emerald-400 font-bold text-base">•</span>
                  <span>{st}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-400 text-xs">Solid overall candidate baseline demonstrated.</li>
            )}
          </ul>
        </div>

        {/* Growth Areas */}
        <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
          <h3 className="text-lg font-bold text-amber-400 flex items-center space-x-2">
            <span>• Areas to Improve</span>
          </h3>
          <ul className="space-y-3 text-sm text-slate-300">
            {report.weaknesses && report.weaknesses.length > 0 ? (
              report.weaknesses.map((wk, idx) => (
                <li key={idx} className="flex items-start space-x-2.5">
                  <span className="text-amber-400 font-bold text-base">•</span>
                  <span>{wk}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-400 text-xs">Review targeted technical concepts to reach maximum precision.</li>
            )}
          </ul>
        </div>
      </div>

      {/* Recommendations & Action Plan */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recommended Topics */}
        <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
          <h3 className="text-lg font-bold text-indigo-400 flex items-center space-x-2">
            <span>📚 Recommended Topics to Study</span>
          </h3>
          <div className="flex flex-wrap gap-2 pt-1">
            {report.recommended_topics && report.recommended_topics.length > 0 ? (
              report.recommended_topics.map((tpc, idx) => (
                <span
                  key={idx}
                  className="px-3.5 py-1.5 rounded-xl bg-indigo-950/40 border border-indigo-500/30 text-indigo-200 text-xs font-semibold"
                >
                  {tpc}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-400">Target role core architecture</span>
            )}
          </div>
        </div>

        {/* Action Plan */}
        <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
          <h3 className="text-lg font-bold text-purple-400 flex items-center space-x-2">
            <span>🎯 Actionable Improvement Plan</span>
          </h3>
          <ol className="space-y-2.5 text-xs text-slate-300 list-decimal list-inside">
            {report.action_plan && report.action_plan.length > 0 ? (
              report.action_plan.map((act, idx) => (
                <li key={idx} className="leading-relaxed">
                  <span className="font-semibold text-white">{act}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-400">Practice questions under timed constraints.</li>
            )}
          </ol>
        </div>
      </div>

      {/* Summary Feedback */}
      {report.final_feedback && (
        <div className="glass-panel p-6 rounded-2xl bg-indigo-950/20 border border-indigo-500/20 space-y-2">
          <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
            AI Interviewer Final Executive Summary
          </h4>
          <p className="text-sm text-slate-300 leading-relaxed">
            "{report.final_feedback}"
          </p>
        </div>
      )}

      {/* Action Navigation Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800/80">
        <button
          type="button"
          onClick={onPracticeAgain}
          className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-sm shadow-glow hover:opacity-95 transition-all flex items-center justify-center space-x-2"
        >
          <span>Practice Again</span>
          <span>🔄</span>
        </button>

        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <button
            type="button"
            onClick={onViewHistory}
            className="w-full sm:w-auto px-5 py-3.5 rounded-xl bg-surface-900 border border-slate-800 text-slate-300 font-semibold text-xs hover:text-white hover:bg-slate-800 transition-all"
          >
            View History
          </button>

          <Link
            to="/dashboard"
            className="w-full sm:w-auto px-5 py-3.5 rounded-xl bg-surface-900 border border-slate-800 text-slate-300 font-semibold text-xs hover:text-white hover:bg-slate-800 transition-all text-center"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default InterviewResults;
