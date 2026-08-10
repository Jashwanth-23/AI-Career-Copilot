import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api, { parseApiError } from "../services/api";
import { useResume } from "../context/ResumeContext";
import { useToast } from "../context/ToastContext";
import { TimelineSkeleton } from "../components/common/SkeletonLoaders";
import {
  RoadmapIcon,
  UploadIcon,
  ChevronRightIcon,
  AlertIcon,
  SparklesIcon,
  TargetIcon,
  CheckIcon,
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

const LearningRoadmapPage = () => {
  const { activeResume, targetRole, setTargetRole } = useResume();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [roadmapData, setRoadmapData] = useState(null);

  const fetchRoadmap = useCallback(async () => {
    if (!activeResume?.id || loading) return;

    try {
      setLoading(true);
      setError(null);
      const response = await api.post(`/resume/learning-roadmap/${activeResume.id}`, {
        target_role: targetRole,
      });
      setRoadmapData(response.data);
    } catch (err) {
      console.error("Roadmap Error:", err);
      const message = parseApiError(err);
      setError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [activeResume?.id, targetRole, loading, showToast]);

  useEffect(() => {
    if (activeResume?.id) {
      fetchRoadmap();
    }
  }, [activeResume?.id, targetRole]);

  if (!activeResume) {
    return (
      <div className="glass-panel p-10 rounded-3xl text-center border border-slate-800 space-y-4 max-w-xl mx-auto my-12">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-400">
          <RoadmapIcon className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">No Active Resume Uploaded</h2>
        <p className="text-slate-400 text-sm">
          Please upload a resume first to generate your personalized AI learning roadmap.
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

  const roadmapInfo = roadmapData?.learning_roadmap || {};
  const weeks = roadmapInfo.roadmap || [];
  const recommendedProjects = roadmapInfo.recommended_projects || [];

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header & Target Role Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <RoadmapIcon className="w-3.5 h-3.5" />
            <span>AI Curriculum Engine</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">Personalized Learning Roadmap</h1>
          <p className="text-slate-400 text-sm mt-1">
            Tailored weekly roadmap for: <span className="text-indigo-400 font-semibold">{roadmapInfo.target_role || targetRole}</span>
          </p>
        </div>

        {/* Dropdown Selector */}
        <div className="flex items-center space-x-3 glass-panel p-2 rounded-2xl border border-slate-800">
          <span className="text-xs font-bold text-slate-400 pl-2">Target Role:</span>
          <select
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            disabled={loading}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-amber-500 disabled:opacity-50"
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
          <h3 className="text-lg font-bold text-white">Learning Roadmap Unavailable</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{error}</p>
          <button
            onClick={fetchRoadmap}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold hover:shadow-glow transition-all disabled:opacity-50"
          >
            Retry Learning Roadmap
          </button>
        </div>
      )}

      {loading ? (
        <TimelineSkeleton />
      ) : roadmapData ? (
        <div className="space-y-12">
          {/* Summary Banner */}
          <div className="glass-panel p-6 rounded-3xl border border-amber-500/30 bg-gradient-to-r from-amber-950/20 via-surface-900 to-indigo-950/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                Estimated Duration
              </span>
              <h2 className="text-2xl font-black text-white">
                {roadmapInfo.estimated_duration || "8 Weeks"}
              </h2>
            </div>

            <div className="space-y-1 sm:text-right">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Current Readiness Progress
              </span>
              <div className="text-xl font-bold text-indigo-400">
                {roadmapInfo.overall_progress || 35}% Complete
              </div>
            </div>
          </div>

          {/* Timeline UI */}
          <div className="relative pl-6 sm:pl-10 space-y-8 before:absolute before:left-3 sm:before:left-5 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-800">
            {weeks.map((weekItem, idx) => (
              <div key={idx} className="relative group">
                {/* Node Icon */}
                <div className="absolute -left-6 sm:-left-10 top-1.5 w-7 h-7 sm:w-9 sm:h-9 rounded-full bg-slate-900 border-2 border-amber-500 text-amber-400 font-extrabold text-xs flex items-center justify-center shadow-glow group-hover:scale-110 transition-transform">
                  W{weekItem.week}
                </div>

                {/* Module Card */}
                <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-4 glass-panel-hover">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                        Week {weekItem.week} Focus
                      </span>
                      <h3 className="text-xl font-extrabold text-white mt-0.5">
                        {weekItem.focus}
                      </h3>
                    </div>

                    <span className="self-start sm:self-auto px-3 py-1 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
                      Milestone: {weekItem.milestone}
                    </span>
                  </div>

                  {/* Topics List */}
                  {weekItem.topics && weekItem.topics.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        Key Topics Covered
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {weekItem.topics.map((t, ti) => (
                          <span
                            key={ti}
                            className="px-3 py-1 rounded-xl bg-slate-800/80 text-xs font-medium text-slate-200 border border-slate-700/60"
                          >
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Mini Project */}
                  {weekItem.mini_project && (
                    <div className="p-4 rounded-2xl bg-indigo-950/30 border border-indigo-500/20 space-y-1">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                        Practical Mini-Project Challenge
                      </h4>
                      <p className="text-xs text-slate-200 font-medium">{weekItem.mini_project}</p>
                    </div>
                  )}

                  {/* Free Resources */}
                  {weekItem.resources && weekItem.resources.length > 0 && (
                    <div className="space-y-1.5 pt-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        Free Learning Resources
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {weekItem.resources.map((res, ri) => (
                          <a
                            key={ri}
                            href={res.startsWith("http") ? res : `https://google.com/search?q=${encodeURIComponent(res)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-amber-300 transition-colors inline-flex items-center space-x-1"
                          >
                            <span>{res}</span>
                            <ChevronRightIcon className="w-3 h-3" />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* AI-GENERATED REAL-WORLD PROJECTS SECTION */}
          {recommendedProjects && recommendedProjects.length > 0 && (
            <div className="space-y-6 pt-10 border-t border-slate-800/80">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold uppercase tracking-wider mb-2">
                    <SparklesIcon className="w-3.5 h-3.5" />
                    <span>Hands-on Portfolio Showcase</span>
                  </div>
                  <h2 className="text-2xl font-extrabold text-white">✨ AI-GENERATED REAL-WORLD PROJECTS</h2>
                  <p className="text-slate-400 text-sm mt-1">
                    "Build these projects to become job-ready for your target role."
                  </p>
                </div>

                <div className="px-4 py-2 rounded-xl glass-panel border border-indigo-500/30 text-xs text-indigo-300 font-semibold flex items-center space-x-2 self-start sm:self-auto">
                  <span className="text-slate-400">Target Role:</span>
                  <span className="text-indigo-400 font-bold">{roadmapInfo.target_role || targetRole}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-6">
                {recommendedProjects.map((proj, pIdx) => {
                  const difficultyColor =
                    proj.difficulty === "Advanced"
                      ? "bg-rose-950/60 border-rose-500/30 text-rose-300"
                      : proj.difficulty === "Intermediate"
                      ? "bg-amber-950/60 border-amber-500/30 text-amber-300"
                      : "bg-emerald-950/60 border-emerald-500/30 text-emerald-300";

                  return (
                    <div
                      key={pIdx}
                      className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/30 space-y-6 glass-panel-hover bg-gradient-to-br from-surface-900 via-slate-900/90 to-indigo-950/20"
                    >
                      {/* Card Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-3">
                            <span className="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400 font-bold text-xs flex items-center justify-center border border-indigo-500/30">
                              P{pIdx + 1}
                            </span>
                            <h3 className="text-xl font-extrabold text-white">{proj.title}</h3>
                          </div>
                          <p className="text-xs text-slate-300 leading-relaxed pt-1">{proj.description}</p>
                        </div>

                        <div className="flex items-center space-x-2 self-start sm:self-auto flex-shrink-0">
                          <span className={`px-3 py-1 rounded-full border text-xs font-bold ${difficultyColor}`}>
                            {proj.difficulty}
                          </span>
                          <span className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono">
                            {proj.estimated_duration}
                          </span>
                        </div>
                      </div>

                      {/* Why This Project */}
                      {proj.why_this_project && (
                        <div className="p-4 rounded-2xl bg-indigo-950/40 border border-indigo-500/20 space-y-1">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                            Why This Project?
                          </h4>
                          <p className="text-xs text-slate-200 leading-relaxed">{proj.why_this_project}</p>
                        </div>
                      )}

                      {/* Technology Stack */}
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                            Technology Stack
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {proj.technologies.map((tech, tIdx) => (
                              <span
                                key={tIdx}
                                className="px-3 py-1 rounded-xl bg-purple-950/60 border border-purple-500/30 text-purple-300 text-xs font-semibold"
                              >
                                {tech}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Key Features & Skills Developed Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Key Features */}
                        {proj.key_features && proj.key_features.length > 0 && (
                          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400">
                              Key Features
                            </h4>
                            <ul className="space-y-1 text-xs text-slate-300">
                              {proj.key_features.map((feat, fIdx) => (
                                <li key={fIdx} className="flex items-start space-x-2">
                                  <span className="text-amber-400 mt-0.5">•</span>
                                  <span>{feat}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Skills Developed */}
                        {proj.skills_developed && proj.skills_developed.length > 0 && (
                          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                              Skills Developed
                            </h4>
                            <div className="flex flex-wrap gap-1.5">
                              {proj.skills_developed.map((sk, sIdx) => (
                                <span
                                  key={sIdx}
                                  className="px-2.5 py-0.5 rounded-lg bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-[11px] font-medium"
                                >
                                  {sk}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {/* Skill Gap Addressed */}
                      {proj.skill_gap_addressed && proj.skill_gap_addressed.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400">
                            Skill Gap Addressed
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {proj.skill_gap_addressed.map((gap, gIdx) => (
                              <span
                                key={gIdx}
                                className="px-3 py-1 rounded-xl bg-rose-950/60 border border-rose-500/30 text-rose-300 text-xs font-semibold"
                              >
                                {gap}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Portfolio Value & Expected Outcome Footer */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-800/60 text-xs">
                        {proj.portfolio_value && (
                          <div>
                            <span className="font-bold text-emerald-400 uppercase text-[10px] block mb-0.5">
                              Portfolio Value
                            </span>
                            <p className="text-slate-300 leading-relaxed">{proj.portfolio_value}</p>
                          </div>
                        )}

                        {proj.expected_outcome && (
                          <div>
                            <span className="font-bold text-indigo-400 uppercase text-[10px] block mb-0.5">
                              Expected Outcome
                            </span>
                            <p className="text-slate-300 leading-relaxed">{proj.expected_outcome}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
};

export default LearningRoadmapPage;
