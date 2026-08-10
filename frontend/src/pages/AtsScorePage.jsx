import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api, { parseApiError } from "../services/api";
import { useResume } from "../context/ResumeContext";
import { useToast } from "../context/ToastContext";
import CircularMeter from "../components/common/CircularMeter";
import { MeterSkeleton } from "../components/common/SkeletonLoaders";
import {
  ChartIcon,
  SparklesIcon,
  CheckIcon,
  AlertIcon,
  UploadIcon,
} from "../components/common/Icons";

const AtsScorePage = () => {
  const { activeResume } = useResume();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [atsData, setAtsData] = useState(null);

  const fetchAtsScore = useCallback(async () => {
    if (!activeResume?.id || loading) return;

    try {
      setLoading(true);
      setError(null);
      const response = await api.post(`/resume/ats/${activeResume.id}`);
      setAtsData(response.data);
    } catch (err) {
      console.error("ATS Score Error:", err);
      const message = parseApiError(err);
      setError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [activeResume?.id, loading, showToast]);

  useEffect(() => {
    if (activeResume?.id) {
      fetchAtsScore();
    }
  }, [activeResume?.id]);

  if (!activeResume) {
    return (
      <div className="glass-panel p-10 rounded-3xl text-center border border-slate-800 space-y-4 max-w-xl mx-auto my-12">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
          <ChartIcon className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">No Active Resume Found</h2>
        <p className="text-slate-400 text-sm">
          Please upload a resume document to generate your ATS score breakdown.
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

  const scoreInfo = atsData?.ats_score || {};
  const overallScore = scoreInfo.overall_score || 0;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold uppercase tracking-wider mb-2">
          <ChartIcon className="w-3.5 h-3.5" />
          <span>Recruiter & ATS Optimization</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white">ATS Compatibility Score</h1>
        <p className="text-slate-400 text-sm mt-1">
          Evaluating document: <span className="text-indigo-400 font-semibold">{activeResume.original_filename}</span>
        </p>
      </div>

      {error && !loading && (
        <div className="glass-panel p-6 rounded-3xl border border-rose-500/30 bg-rose-950/10 text-center space-y-4 max-w-xl mx-auto my-6">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
            <AlertIcon className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">ATS Analysis Unavailable</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{error}</p>
          <button
            onClick={fetchAtsScore}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold hover:shadow-glow transition-all disabled:opacity-50"
          >
            Retry ATS Analysis
          </button>
        </div>
      )}

      {loading ? (
        <MeterSkeleton />
      ) : atsData ? (
        <div className="space-y-8">
          {/* Circular Score Gauge & Metric Cards Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Meter Card */}
            <div className="glass-panel p-8 rounded-3xl border border-slate-800 flex flex-col items-center justify-center space-y-6 shadow-xl">
              <CircularMeter score={overallScore} size={200} strokeWidth={16} label="Overall ATS" />
              <div className="text-center">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Rating Assessment
                </span>
                <p className="text-base font-bold text-white mt-1">
                  {overallScore >= 80 ? "Excellent ATS Readiness 🎉" : overallScore >= 60 ? "Good - Needs Minor Edits ⚡" : "Needs Optimization ⚠️"}
                </p>
              </div>
            </div>

            {/* Score Breakdown Progress Bars */}
            <div className="glass-panel p-8 rounded-3xl border border-slate-800 lg:col-span-2 space-y-5">
              <h3 className="text-lg font-bold text-white">Section Score Breakdown</h3>

              <div className="space-y-4 text-xs">
                {/* Skills Score */}
                <div className="space-y-1">
                  <div className="flex justify-between font-semibold">
                    <span className="text-slate-300">Technical Skills Coverage</span>
                    <span className="text-indigo-400">{scoreInfo.skills_score || 0}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${scoreInfo.skills_score || 0}%` }}></div>
                  </div>
                </div>

                {/* Experience Score */}
                <div className="space-y-1">
                  <div className="flex justify-between font-semibold">
                    <span className="text-slate-300">Experience Impact & Relevance</span>
                    <span className="text-purple-400">{scoreInfo.experience_score || 0}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500 rounded-full" style={{ width: `${scoreInfo.experience_score || 0}%` }}></div>
                  </div>
                </div>

                {/* Education Score */}
                <div className="space-y-1">
                  <div className="flex justify-between font-semibold">
                    <span className="text-slate-300">Education & Credentials</span>
                    <span className="text-cyan-400">{scoreInfo.education_score || 0}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${scoreInfo.education_score || 0}%` }}></div>
                  </div>
                </div>

                {/* Projects Score */}
                <div className="space-y-1">
                  <div className="flex justify-between font-semibold">
                    <span className="text-slate-300">Projects & Achievements</span>
                    <span className="text-emerald-400">{scoreInfo.projects_score || 0}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${scoreInfo.projects_score || 0}%` }}></div>
                  </div>
                </div>

                {/* Completeness Score */}
                <div className="space-y-1">
                  <div className="flex justify-between font-semibold">
                    <span className="text-slate-300">Profile Completeness & Formatting</span>
                    <span className="text-amber-400">{scoreInfo.completeness_score || 0}%</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 rounded-full" style={{ width: `${scoreInfo.completeness_score || 0}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Strengths & Weaknesses Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Strengths */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-emerald-500/30 bg-emerald-950/10 space-y-4">
              <h3 className="text-lg font-bold text-emerald-400 flex items-center space-x-2">
                <CheckIcon className="w-5 h-5" />
                <span>Identified Strengths</span>
              </h3>
              {scoreInfo.strengths && scoreInfo.strengths.length > 0 ? (
                <ul className="space-y-2.5 text-xs text-slate-300">
                  {scoreInfo.strengths.map((item, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-emerald-400 mt-0.5">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-400">No explicit strengths highlighted.</p>
              )}
            </div>

            {/* Weaknesses */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-rose-500/30 bg-rose-950/10 space-y-4">
              <h3 className="text-lg font-bold text-rose-400 flex items-center space-x-2">
                <AlertIcon className="w-5 h-5" />
                <span>Identified Weaknesses</span>
              </h3>
              {scoreInfo.weaknesses && scoreInfo.weaknesses.length > 0 ? (
                <ul className="space-y-2.5 text-xs text-slate-300">
                  {scoreInfo.weaknesses.map((item, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <span className="text-rose-400 mt-0.5">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-400">No major weaknesses detected!</p>
              )}
            </div>
          </div>

          {/* Actionable Improvement Suggestions */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/30 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <SparklesIcon className="w-5 h-5 text-indigo-400" />
              <span>Actionable Improvement Suggestions</span>
            </h3>
            {scoreInfo.improvement_suggestions && scoreInfo.improvement_suggestions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {scoreInfo.improvement_suggestions.map((suggestion, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-start space-x-3">
                    <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-bold flex items-center justify-center flex-shrink-0">
                      {idx + 1}
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed">{suggestion}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No suggestions needed.</p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default AtsScorePage;
