import React, { useState } from "react";

const InterviewQuestion = ({
  session,
  activeQuestion,
  onSubmitAnswer,
  loading,
  error,
}) => {
  const [answerInput, setAnswerInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!answerInput.trim() || loading) return;
    onSubmitAnswer(answerInput.trim());
  };

  const handleClear = () => {
    setAnswerInput("");
  };

  if (!activeQuestion) {
    return (
      <div className="glass-panel p-8 text-center rounded-2xl bg-surface-900/90 text-slate-300">
        No active question. Please wait or refresh the page.
      </div>
    );
  }

  const currentNum = session?.current_question_number || activeQuestion.question_number || 1;
  const totalNum = session?.total_questions || 3;
  const progressPercent = Math.round((currentNum / totalNum) * 100);

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4">
      {/* Session Progress Header */}
      <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-indigo-400">
              <span>{session?.target_role || "Target Role"}</span>
              <span>•</span>
              <span className="capitalize">{session?.interview_type || "Technical"}</span>
              <span>•</span>
              <span className="capitalize">{session?.difficulty || "Medium"}</span>
            </div>
            <h2 className="text-xl font-bold text-white mt-1">
              Question {currentNum} of {totalNum}
            </h2>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs font-bold text-slate-400">
              Progress {progressPercent}%
            </span>
            <div className="w-32 h-2.5 bg-surface-950 rounded-full overflow-hidden border border-slate-800">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-300 shadow-glow"
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Question Card */}
      <div className="glass-panel p-8 rounded-2xl bg-gradient-to-br from-surface-900 via-surface-900 to-indigo-950/20 border border-indigo-500/20 shadow-glow space-y-6">
        {/* Meta badges */}
        <div className="flex flex-wrap gap-2">
          {activeQuestion.topic && (
            <span className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium">
              Topic: {activeQuestion.topic}
            </span>
          )}
          {activeQuestion.resume_reference && (
            <span className="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-medium">
              Resume Ref: {activeQuestion.resume_reference}
            </span>
          )}
          <span className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium capitalize">
            {activeQuestion.difficulty || "medium"}
          </span>
        </div>

        {/* Question Text Prompt */}
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-wider font-bold text-slate-400">
            AI Interviewer asks:
          </p>
          <h3 className="text-xl sm:text-2xl font-bold text-white leading-relaxed">
            "{activeQuestion.question_text}"
          </h3>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-start space-x-3">
            <span>⚠️</span>
            <div className="flex-1">{error}</div>
          </div>
        )}

        {/* Answer Text Input Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Your Text Answer
            </label>
            <textarea
              rows={7}
              value={answerInput}
              onChange={(e) => setAnswerInput(e.target.value)}
              disabled={loading}
              placeholder="Type your response clearly and thoroughly... Explain your approach, key principles, and practical examples."
              className="w-full p-4 rounded-xl bg-surface-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-indigo-500 transition-all resize-y disabled:opacity-50"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={handleClear}
              disabled={loading || !answerInput}
              className="px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-semibold transition-all disabled:opacity-40"
            >
              Clear Answer
            </button>

            <button
              type="submit"
              disabled={loading || !answerInput.trim()}
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 text-white font-bold text-sm shadow-glow hover:opacity-95 disabled:opacity-50 transition-all flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>AI interviewer is evaluating your answer...</span>
                </>
              ) : (
                <>
                  <span>Submit Answer</span>
                  <span>→</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InterviewQuestion;
