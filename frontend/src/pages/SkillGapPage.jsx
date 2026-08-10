import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api, { parseApiError } from "../services/api";
import { useResume } from "../context/ResumeContext";
import { useToast } from "../context/ToastContext";
import { CardSkeleton } from "../components/common/SkeletonLoaders";
import {
  TargetIcon,
  SparklesIcon,
  CheckIcon,
  AlertIcon,
  UploadIcon,
} from "../components/common/Icons";

const AVAILABLE_ROLES = [
  "Full Stack Developer",
  "Backend Developer",
  "Frontend Developer",
  "AI Engineer",
  "Data Analyst",
  "Cloud Engineer",
  "Software Engineer",
];

const SkillGapPage = () => {
  const { activeResume, targetRole, setTargetRole } = useResume();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [skillGapData, setSkillGapData] = useState(null);

  const fetchSkillGap = useCallback(async () => {
    if (!activeResume?.id || loading) return;

    try {
      setLoading(true);
      setError(null);
      const response = await api.post(`/resume/skill-gap/${activeResume.id}`, {
        target_role: targetRole,
      });
      setSkillGapData(response.data);
    } catch (err) {
      console.error("Skill Gap Error:", err);
      const message = parseApiError(err);
      setError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [activeResume?.id, targetRole, loading, showToast]);

  useEffect(() => {
    if (activeResume?.id) {
      fetchSkillGap();
    }
  }, [activeResume?.id, targetRole]);

  if (!activeResume) {
    return (
      <div className="glass-panel p-10 rounded-3xl text-center border border-slate-800 space-y-4 max-w-xl mx-auto my-12">
        <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
          <TargetIcon className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">No Active Resume Found</h2>
        <p className="text-slate-400 text-sm">
          Upload a resume to analyze candidate skill gaps against target tech roles.
        </p>
        <Link
          to="/upload"
          className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-sm hover:shadow-glow transition-all"
        >
          <UploadIcon className="w-4 h-4" />
          <span>Upload Resume Now</span>
        </Link>
      </div>
    );
  }

  const gapInfo = skillGapData?.skill_gap || {};
  const matchPct = gapInfo.match_percentage || 0;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header & Target Role Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <TargetIcon className="w-3.5 h-3.5" />
            <span>Target Role Benchmark</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">Skill Gap Analysis</h1>
          <p className="text-slate-400 text-sm mt-1">
            Analyzing document: <span className="text-indigo-400 font-semibold">{activeResume.original_filename}</span>
          </p>
        </div>

        {/* Dropdown Selector */}
        <div className="flex items-center space-x-3 glass-panel p-2 rounded-2xl border border-slate-800">
          <span className="text-xs font-bold text-slate-400 pl-2">Target Role:</span>
          <select
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            disabled={loading}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-cyan-500 disabled:opacity-50"
          >
            {AVAILABLE_ROLES.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && !loading && (
        <div className="glass-panel p-6 rounded-3xl border border-rose-500/30 bg-rose-950/10 text-center space-y-4 max-w-xl mx-auto my-6">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
            <AlertIcon className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Skill Gap Analysis Unavailable</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{error}</p>
          <button
            onClick={fetchSkillGap}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold hover:shadow-glow transition-all disabled:opacity-50"
          >
            Retry Skill Gap Analysis
          </button>
        </div>
      )}

      {loading ? (
        <CardSkeleton />
      ) : skillGapData ? (
        <div className="space-y-8">
          {/* Match Score Banner */}
          <div className="glass-panel p-8 rounded-3xl border border-cyan-500/30 bg-gradient-to-r from-cyan-950/20 via-surface-900 to-indigo-950/30 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                  Skill Match Ratio
                </span>
                <h2 className="text-2xl font-extrabold text-white mt-1">
                  {gapInfo.target_role} Benchmark
                </h2>
              </div>
              <div className="text-right">
                <span className="text-4xl font-black text-cyan-300">{matchPct}%</span>
                <span className="text-xs text-slate-400 block font-medium">Role Compatibility</span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-400 via-indigo-500 to-purple-500 transition-all duration-1000"
                style={{ width: `${matchPct}%` }}
              ></div>
            </div>
          </div>

          {/* Matched vs Missing Skills Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Matched Skills */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-emerald-500/30 bg-emerald-950/10 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-emerald-400 flex items-center space-x-2">
                  <CheckIcon className="w-5 h-5" />
                  <span>Matched Skills ({gapInfo.matched_skills?.length || 0})</span>
                </h3>
              </div>

              {gapInfo.matched_skills && gapInfo.matched_skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {gapInfo.matched_skills.map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1.5 rounded-xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center space-x-1"
                    >
                      <CheckIcon className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{skill}</span>
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No overlapping skills found for this role.</p>
              )}
            </div>

            {/* Missing Skills */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-rose-500/30 bg-rose-950/10 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-rose-400 flex items-center space-x-2">
                  <AlertIcon className="w-5 h-5" />
                  <span>Missing Core Skills ({gapInfo.missing_skills?.length || 0})</span>
                </h3>
              </div>

              {gapInfo.missing_skills && gapInfo.missing_skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {gapInfo.missing_skills.map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1.5 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs font-semibold"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No missing skills! You meet all core requirements.</p>
              )}
            </div>
          </div>

          {/* Priority Learning Order & Recommended Secondary Skills */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Priority Order */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/30 space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <SparklesIcon className="w-5 h-5 text-indigo-400" />
                <span>Priority Learning Order</span>
              </h3>
              {gapInfo.priority_learning_order && gapInfo.priority_learning_order.length > 0 ? (
                <ol className="space-y-2 text-xs text-slate-300">
                  {gapInfo.priority_learning_order.map((item, idx) => (
                    <li key={idx} className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                      <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 font-bold text-xs flex items-center justify-center flex-shrink-0">
                        {idx + 1}
                      </span>
                      <span className="font-medium text-white">{item}</span>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="text-xs text-slate-400">No priority order available.</p>
              )}
            </div>

            {/* Recommended Skills */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-purple-500/30 space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <TargetIcon className="w-5 h-5 text-purple-400" />
                <span>Recommended Secondary Skills</span>
              </h3>
              {gapInfo.recommended_skills && gapInfo.recommended_skills.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {gapInfo.recommended_skills.map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1.5 rounded-xl bg-purple-950/60 border border-purple-500/30 text-purple-300 text-xs font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No extra secondary skills recommended.</p>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default SkillGapPage;
