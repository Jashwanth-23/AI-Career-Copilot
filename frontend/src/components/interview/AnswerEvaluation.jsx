import React from "react";

const AnswerEvaluation = ({
  evaluation,
  onContinue,
  isLastQuestion,
  loading,
}) => {
  if (!evaluation) return null;

  const score = evaluation.overall_score || 0;

  const getScoreColor = (val) => {
    if (val >= 85) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (val >= 70) return "text-indigo-400 border-indigo-500/30 bg-indigo-500/10";
    if (val >= 55) return "text-amber-400 border-amber-500/30 bg-amber-500/10";
    return "text-rose-400 border-rose-500/30 bg-rose-500/10";
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4 animate-fade-in">
      {/* Feedback Banner */}
      <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-300 text-xs font-bold uppercase tracking-wider mb-2">
              <span>✨ AI Answer Evaluation</span>
            </div>
            <h3 className="text-2xl font-extrabold text-white">
              Feedback & Performance Analysis
            </h3>
          </div>

          <div
            className={`px-6 py-3 rounded-2xl border flex items-center space-x-3 ${getScoreColor(
              score
            )}`}
          >
            <span className="text-xs uppercase font-bold tracking-wider">
              Score
            </span>
            <span className="text-3xl font-extrabold">{score}/100</span>
          </div>
        </div>

        {/* Sub-Scores Matrix */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl bg-surface-950/60 border border-slate-800 text-center space-y-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Accuracy
            </span>
            <div className="text-xl font-bold text-white">
              {evaluation.technical_accuracy ?? score}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl bg-surface-950/60 border border-slate-800 text-center space-y-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Relevance
            </span>
            <div className="text-xl font-bold text-white">
              {evaluation.relevance ?? score}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl bg-surface-950/60 border border-slate-800 text-center space-y-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Completeness
            </span>
            <div className="text-xl font-bold text-white">
              {evaluation.completeness ?? score}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl bg-surface-950/60 border border-slate-800 text-center space-y-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Communication
            </span>
            <div className="text-xl font-bold text-white">
              {evaluation.communication ?? score}
            </div>
          </div>
        </div>

        {/* Strengths & Missing Points */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strengths */}
          <div className="p-5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-3">
            <h4 className="text-sm font-bold text-emerald-300 flex items-center space-x-2">
              <span>✓ Strengths</span>
            </h4>
            <ul className="space-y-2 text-xs text-slate-300">
              {evaluation.strengths && evaluation.strengths.length > 0 ? (
                evaluation.strengths.map((str, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{str}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-400">Response was received cleanly.</li>
              )}
            </ul>
          </div>

          {/* Missing Points / Growth */}
          <div className="p-5 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-3">
            <h4 className="text-sm font-bold text-amber-300 flex items-center space-x-2">
              <span>• Missing Key Concepts</span>
            </h4>
            <ul className="space-y-2 text-xs text-slate-300">
              {evaluation.missing_points && evaluation.missing_points.length > 0 ? (
                evaluation.missing_points.map((pt, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <span className="text-amber-400 font-bold">•</span>
                    <span>{pt}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-400">Covered core expected points well.</li>
              )}
            </ul>
          </div>
        </div>

        {/* Improvement & Ideal Answer Guidance */}
        <div className="space-y-4">
          {evaluation.improvement && (
            <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 space-y-1">
              <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
                How to Improve:
              </span>
              <p className="text-sm text-slate-300">{evaluation.improvement}</p>
            </div>
          )}

          {evaluation.ideal_answer && (
            <div className="p-4 rounded-xl bg-surface-950 border border-slate-800 space-y-1">
              <span className="text-xs font-bold text-purple-300 uppercase tracking-wider">
                Ideal Answer Direction:
              </span>
              <p className="text-sm text-slate-300 italic">{evaluation.ideal_answer}</p>
            </div>
          )}
        </div>

        {/* Continue Action */}
        <div className="flex justify-end pt-4 border-t border-slate-800/80">
          <button
            type="button"
            onClick={onContinue}
            disabled={loading}
            className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-sm shadow-glow hover:opacity-95 disabled:opacity-50 transition-all flex items-center space-x-2"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Preparing next step...</span>
              </>
            ) : (
              <>
                <span>{isLastQuestion ? "View Final Report" : "Continue to Next Question"}</span>
                <span>→</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnswerEvaluation;
