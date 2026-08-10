import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api, { parseApiError } from "../services/api";
import { useResume } from "../context/ResumeContext";
import { useToast } from "../context/ToastContext";
import { CardSkeleton } from "../components/common/SkeletonLoaders";
import {
  BriefcaseIcon,
  CheckIcon,
  AlertIcon,
  UploadIcon,
} from "../components/common/Icons";

const LOCATIONS = ["Remote", "On-site", "Hybrid"];
const EXPERIENCE_LEVELS = ["Fresher", "Junior", "Mid-Level", "Senior", "Lead"];

const JobRecommendationsPage = () => {
  const {
    activeResume,
    preferredLocation,
    setPreferredLocation,
    experienceLevel,
    setExperienceLevel,
  } = useResume();

  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jobsData, setJobsData] = useState(null);

  const fetchJobRecommendations = useCallback(async () => {
    if (!activeResume?.id || loading) return;

    try {
      setLoading(true);
      setError(null);
      const response = await api.post(`/resume/job-recommendations/${activeResume.id}`, {
        preferred_location: preferredLocation,
        experience_level: experienceLevel,
      });
      setJobsData(response.data);
    } catch (err) {
      console.error("Job Recommendations Error:", err);
      const message = parseApiError(err);
      setError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [activeResume?.id, preferredLocation, experienceLevel, loading, showToast]);

  useEffect(() => {
    if (activeResume?.id) {
      fetchJobRecommendations();
    }
  }, [activeResume?.id, preferredLocation, experienceLevel]);

  if (!activeResume) {
    return (
      <div className="glass-panel p-10 rounded-3xl text-center border border-slate-800 space-y-4 max-w-xl mx-auto my-12">
        <div className="w-16 h-16 rounded-2xl bg-pink-500/10 border border-pink-500/30 flex items-center justify-center mx-auto text-pink-400">
          <BriefcaseIcon className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">No Active Resume Uploaded</h2>
        <p className="text-slate-400 text-sm">
          Please upload a resume first to evaluate job role suitabilities & salary ranges.
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

  const recommendedJobs = jobsData?.recommended_jobs || [];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header & Preferences Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-pink-500/10 border border-pink-500/30 text-pink-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <BriefcaseIcon className="w-3.5 h-3.5" />
            <span>AI Job Matching</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">Job Recommendations</h1>
          <p className="text-slate-400 text-sm mt-1">
            Matching candidate profile: <span className="text-indigo-400 font-semibold">{activeResume.original_filename}</span>
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3 glass-panel p-2 rounded-2xl border border-slate-800">
          <div className="flex items-center space-x-2 pl-2">
            <span className="text-xs font-bold text-slate-400">Location:</span>
            <select
              value={preferredLocation}
              onChange={(e) => setPreferredLocation(e.target.value)}
              disabled={loading}
              className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-pink-500 disabled:opacity-50"
            >
              {LOCATIONS.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-slate-400">Tier:</span>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              disabled={loading}
              className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-pink-500 disabled:opacity-50"
            >
              {EXPERIENCE_LEVELS.map((tier) => (
                <option key={tier} value={tier}>
                  {tier}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {error && !loading && (
        <div className="glass-panel p-6 rounded-3xl border border-rose-500/30 bg-rose-950/10 text-center space-y-4 max-w-xl mx-auto my-6">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
            <AlertIcon className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Job Recommendations Unavailable</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{error}</p>
          <button
            onClick={fetchJobRecommendations}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold hover:shadow-glow transition-all disabled:opacity-50"
          >
            Retry Job Recommendations
          </button>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : jobsData ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {recommendedJobs.map((job, idx) => {
              const matchPct = job.match_percentage || 0;
              const isHighMatch = matchPct >= 75;

              return (
                <div
                  key={idx}
                  className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-5 glass-panel-hover flex flex-col justify-between"
                >
                  <div className="space-y-4">
                    {/* Header: Title, Badge, Salary */}
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                          Role Title
                        </span>
                        <h3 className="text-xl font-extrabold text-white mt-0.5">{job.role}</h3>
                        <span className="inline-block mt-1 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
                          Est. Salary: {job.salary_range}
                        </span>
                      </div>

                      {/* Match Badge */}
                      <div
                        className={`px-3 py-1.5 rounded-xl font-black text-sm flex flex-col items-center border ${
                          isHighMatch
                            ? "bg-emerald-950/80 border-emerald-500/40 text-emerald-300"
                            : "bg-amber-950/80 border-amber-500/40 text-amber-300"
                        }`}
                      >
                        <span>{matchPct}%</span>
                        <span className="text-[9px] uppercase tracking-wider font-normal">Match</span>
                      </div>
                    </div>

                    {/* Candidate Strengths */}
                    {job.strengths && job.strengths.length > 0 && (
                      <div className="space-y-1.5">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center space-x-1">
                          <CheckIcon className="w-3.5 h-3.5" />
                          <span>Aligned Candidate Strengths</span>
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {job.strengths.map((s, si) => (
                            <span key={si} className="px-2.5 py-0.5 rounded-lg bg-emerald-950/40 text-emerald-300 text-[11px]">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Skills */}
                    {job.missing_skills && job.missing_skills.length > 0 && (
                      <div className="space-y-1.5">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center space-x-1">
                          <AlertIcon className="w-3.5 h-3.5" />
                          <span>Missing Requirements</span>
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {job.missing_skills.map((m, mi) => (
                            <span key={mi} className="px-2.5 py-0.5 rounded-lg bg-rose-950/40 text-rose-300 text-[11px]">
                              {m}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Advice / Recommendations */}
                    {job.recommendations && job.recommendations.length > 0 && (
                      <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1 text-xs text-slate-300">
                        <span className="font-bold text-indigo-400 uppercase text-[10px]">Actionable Advice</span>
                        <ul className="list-disc list-inside space-y-0.5 text-slate-400 text-[11px]">
                          {job.recommendations.map((rec, ri) => (
                            <li key={ri}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default JobRecommendationsPage;
