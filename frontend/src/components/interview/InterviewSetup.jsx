import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useResume } from "../../context/ResumeContext";

const INTERVIEW_TYPES = [
  {
    id: "technical",
    label: "Technical",
    icon: "💻",
    description: "Algorithms, APIs, databases, framework concepts, and coding logic.",
  },
  {
    id: "behavioral",
    label: "Behavioral",
    icon: "🤝",
    description: "STAR-style questions on teamwork, conflict resolution, and leadership.",
  },
  {
    id: "hr",
    label: "HR & Culture",
    icon: "🎯",
    description: "Introduction, career goals, strengths, weaknesses, and company fit.",
  },
  {
    id: "system_design",
    label: "System Design",
    icon: "🏗️",
    description: "Architecture, scalability, trade-offs, microservices, and database design.",
  },
  {
    id: "mixed",
    label: "Mixed",
    icon: "⚡",
    description: "A balanced blend of technical, behavioral, and scenario-based questions.",
  },
  {
    id: "resume_based",
    label: "Resume-Based",
    icon: "📄",
    description: "Questions generated strictly around your uploaded resume projects & skills.",
  },
];

const DIFFICULTY_LEVELS = [
  { id: "easy", label: "Easy", desc: "Fundamentals & core concepts" },
  { id: "medium", label: "Medium", desc: "Practical scenarios & application" },
  { id: "hard", label: "Hard", desc: "Deep technical reasoning & trade-offs" },
];

const QUESTION_COUNTS = [3, 5, 10, 15];

const InterviewSetup = ({ onStart, loading, error }) => {
  const { activeResume, resumeHistory, setActiveResume, targetRole } = useResume();

  const [selectedResumeId, setSelectedResumeId] = useState(
    activeResume ? activeResume.id : resumeHistory[0]?.id || ""
  );
  const [roleInput, setRoleInput] = useState(targetRole || "Backend Developer");
  const [interviewType, setInterviewType] = useState("technical");
  const [difficulty, setDifficulty] = useState("medium");
  const [questionCount, setQuestionCount] = useState(3);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedResumeId) return;

    onStart({
      resume_id: Number(selectedResumeId),
      target_role: roleInput.trim() || "Software Engineer",
      interview_type: interviewType,
      difficulty: difficulty,
      total_questions: Number(questionCount),
    });
  };

  const handleResumeChange = (e) => {
    const id = Number(e.target.value);
    setSelectedResumeId(id);
    const found = resumeHistory.find((r) => r.id === id);
    if (found) {
      setActiveResume(found);
    }
  };

  if (!resumeHistory || resumeHistory.length === 0) {
    return (
      <div className="glass-panel p-8 text-center max-w-2xl mx-auto my-12 space-y-6 bg-surface-900/80 border border-indigo-500/20 rounded-2xl">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto text-3xl">
          📄
        </div>
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-white">No Resume Available</h2>
          <p className="text-slate-400 max-w-md mx-auto text-sm">
            Please upload a resume first so Gemini AI can generate personalized interview questions based on your experience.
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold shadow-glow hover:opacity-95 transition-all"
        >
          <span>Upload Resume Now</span>
          <span>→</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      {/* Header Banner */}
      <div className="glass-panel p-8 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-surface-900 to-purple-950/30 border border-indigo-500/20 shadow-glow relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -z-10"></div>
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
            <span>✨ Gemini AI Powered</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            AI Mock Interview Setup
          </h1>
          <p className="text-slate-300 text-sm max-w-2xl">
            Configure your personalized mock interview session. Gemini will generate candidate-specific questions tailored to your active resume, skills, and target position.
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-start space-x-3">
          <span className="text-base">⚠️</span>
          <div className="flex-1">{error}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Step 1: Target Role & Resume Selection */}
        <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center space-x-2">
            <span className="text-indigo-400">01.</span>
            <span>Candidate Profile & Target Position</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Active Resume */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Select Resume
              </label>
              <select
                value={selectedResumeId}
                onChange={handleResumeChange}
                className="w-full px-4 py-3 rounded-xl bg-surface-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-indigo-500 transition-all"
              >
                {resumeHistory.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.original_filename} ({new Date(r.uploaded_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            </div>

            {/* Target Job Role */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Target Role / Job Position
              </label>
              <input
                type="text"
                value={roleInput}
                onChange={(e) => setRoleInput(e.target.value)}
                placeholder="e.g. Backend Developer, Data Scientist"
                required
                className="w-full px-4 py-3 rounded-xl bg-surface-950 border border-slate-800 text-white text-sm focus:outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>
        </div>

        {/* Step 2: Interview Category Selection */}
        <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center space-x-2">
            <span className="text-indigo-400">02.</span>
            <span>Select Interview Type</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {INTERVIEW_TYPES.map((type) => {
              const selected = interviewType === type.id;
              return (
                <div
                  key={type.id}
                  onClick={() => setInterviewType(type.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 space-y-2 ${
                    selected
                      ? "bg-indigo-950/40 border-indigo-500/80 shadow-glow"
                      : "bg-surface-950/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-800/40"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-2xl">{type.icon}</span>
                    {selected && (
                      <span className="w-2 h-2 rounded-full bg-indigo-400 shadow-glow"></span>
                    )}
                  </div>
                  <h4 className="font-bold text-white text-sm">{type.label}</h4>
                  <p className="text-slate-400 text-xs leading-relaxed">
                    {type.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Step 3: Difficulty & Question Count */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Difficulty Selection */}
          <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <span className="text-indigo-400">03.</span>
              <span>Difficulty Level</span>
            </h3>

            <div className="grid grid-cols-3 gap-3">
              {DIFFICULTY_LEVELS.map((level) => {
                const selected = difficulty === level.id;
                return (
                  <button
                    key={level.id}
                    type="button"
                    onClick={() => setDifficulty(level.id)}
                    className={`py-3 px-2 rounded-xl text-center border font-semibold text-xs transition-all ${
                      selected
                        ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-transparent shadow-glow"
                        : "bg-surface-950 border-slate-800 text-slate-300 hover:bg-slate-800"
                    }`}
                  >
                    <div>{level.label}</div>
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-slate-400 italic">
              {DIFFICULTY_LEVELS.find((d) => d.id === difficulty)?.desc}
            </p>
          </div>

          {/* Number of Questions */}
          <div className="glass-panel p-6 rounded-2xl bg-surface-900/90 border border-slate-800/80 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <span className="text-indigo-400">04.</span>
              <span>Number of Questions</span>
            </h3>

            <div className="grid grid-cols-4 gap-3">
              {QUESTION_COUNTS.map((cnt) => {
                const selected = questionCount === cnt;
                return (
                  <button
                    key={cnt}
                    type="button"
                    onClick={() => setQuestionCount(cnt)}
                    className={`py-3 rounded-xl border text-center font-bold text-sm transition-all ${
                      selected
                        ? "bg-indigo-600 text-white border-indigo-400 shadow-glow"
                        : "bg-surface-950 border-slate-800 text-slate-300 hover:bg-slate-800"
                    }`}
                  >
                    {cnt} Qs
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-slate-400">
              {questionCount === 3
                ? "Fast practice session (Recommended for quick testing)."
                : `Comprehensive ${questionCount}-question interview simulation.`}
            </p>
          </div>
        </div>

        {/* Submit Action */}
        <div className="flex justify-end pt-4">
          <button
            type="submit"
            disabled={loading || !selectedResumeId}
            className="w-full md:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 text-white font-bold text-base shadow-glow hover:opacity-95 disabled:opacity-50 transition-all flex items-center justify-center space-x-3"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Initializing AI Interviewer...</span>
              </>
            ) : (
              <>
                <span>Start AI Interview</span>
                <span>🚀</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default InterviewSetup;
