import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useResume } from "../context/ResumeContext";
import {
  UserIcon,
  DocumentIcon,
  UploadIcon,
  ChartIcon,
  TargetIcon,
  RoadmapIcon,
  BriefcaseIcon,
  SparklesIcon,
  CheckIcon,
  ChevronRightIcon,
} from "../components/common/Icons";

const DashboardPage = () => {
  const { user } = useAuth();
  const { activeResume } = useResume();

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/20 relative overflow-hidden bg-gradient-to-r from-indigo-950/40 via-surface-900 to-purple-950/30">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-60 h-60 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-3">
              <SparklesIcon className="w-3.5 h-3.5" />
              <span>AI Copilot Active</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-white">
              Welcome back, {user?.name || "Developer"}! 👋
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-xl">
              Track your resume status, ATS optimization score, skill match %, and job recommendations in real-time.
            </p>
          </div>

          <Link
            to="/upload"
            className="self-start md:self-auto px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-sm hover:shadow-glow transition-all flex items-center space-x-2"
          >
            <UploadIcon className="w-4 h-4" />
            <span>Upload New Resume</span>
          </Link>
        </div>
      </div>

      {/* Grid Row 1: Profile & Resume Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Profile Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center space-x-4 pb-4 border-b border-slate-800">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 p-0.5 shadow-glow flex items-center justify-center">
              <div className="w-full h-full bg-surface-900 rounded-[14px] flex items-center justify-center text-white font-black text-xl">
                {user?.name ? user.name.charAt(0).toUpperCase() : <UserIcon className="w-6 h-6 text-indigo-400" />}
              </div>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">{user?.name || "Account Profile"}</h3>
              <p className="text-xs text-slate-400">{user?.email}</p>
              <span className="inline-block mt-1 px-2.5 py-0.5 rounded-md bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-[10px] font-bold uppercase tracking-wide">
                Active Member
              </span>
            </div>
          </div>

          <div className="space-y-2.5 text-xs text-slate-400">
            <div className="flex justify-between py-1 border-b border-slate-800/50">
              <span>Account ID</span>
              <span className="text-slate-200 font-mono">#{user?.id || 1}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/50">
              <span>Status</span>
              <span className="text-emerald-400 font-medium">Authenticated</span>
            </div>
            <div className="flex justify-between py-1">
              <span>Member Since</span>
              <span className="text-slate-300">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Active"}
              </span>
            </div>
          </div>
        </div>

        {/* Uploaded Resume Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 lg:col-span-2 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <DocumentIcon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Active Resume</h3>
                  <p className="text-xs text-slate-400">Currently selected document for AI analysis</p>
                </div>
              </div>

              {activeResume && (
                <span className="px-3 py-1 rounded-full bg-indigo-950 border border-indigo-500/40 text-indigo-300 text-xs font-semibold">
                  ID: #{activeResume.id}
                </span>
              )}
            </div>

            {activeResume ? (
              <div className="glass-panel p-4 rounded-xl border border-indigo-500/20 bg-indigo-950/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                    <span>{activeResume.original_filename}</span>
                  </h4>
                  <p className="text-xs text-slate-400">
                    Uploaded: {new Date(activeResume.uploaded_at).toLocaleString()} • {(activeResume.file_size / 1024).toFixed(1)} KB
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <Link
                    to="/analysis"
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors"
                  >
                    View Analysis
                  </Link>
                  <Link
                    to="/ats"
                    className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold transition-colors"
                  >
                    ATS Score
                  </Link>
                </div>
              </div>
            ) : (
              <div className="glass-panel p-6 rounded-xl border border-dashed border-slate-700 text-center space-y-3">
                <p className="text-sm text-slate-400">No active resume uploaded yet.</p>
                <Link
                  to="/upload"
                  className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all"
                >
                  <UploadIcon className="w-4 h-4" />
                  <span>Upload Resume File</span>
                </Link>
              </div>
            )}
          </div>

          {/* Resume Pipeline Status Steps */}
          <div className="pt-4 border-t border-slate-800">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-3">
              Resume Processing Pipeline
            </span>
            <div className="grid grid-cols-3 gap-3 text-center text-xs">
              <div className={`p-2.5 rounded-xl border ${activeResume ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                <div className="font-bold flex items-center justify-center space-x-1">
                  {activeResume && <CheckIcon className="w-3.5 h-3.5 text-emerald-400" />}
                  <span>1. Uploaded</span>
                </div>
              </div>
              <div className={`p-2.5 rounded-xl border ${activeResume ? 'bg-indigo-950/40 border-indigo-500/40 text-indigo-300' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                <div className="font-bold">2. Parsed</div>
              </div>
              <div className={`p-2.5 rounded-xl border ${activeResume ? 'bg-purple-950/40 border-purple-500/40 text-purple-300' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                <div className="font-bold">3. Analyzed</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Grid Row 2: Quick Action Modules */}
      <div>
        <h2 className="text-xl font-bold text-white mb-4">Copilot AI Modules</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            to="/upload"
            className="glass-panel p-6 rounded-2xl glass-panel-hover border border-slate-800 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <UploadIcon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Upload Resume</h3>
              <p className="text-xs text-slate-400">PDF/DOCX upload, file validation, drag & drop support.</p>
            </div>
            <div className="mt-4 flex items-center text-xs font-bold text-indigo-400">
              <span>Go to Upload</span>
              <ChevronRightIcon className="w-4 h-4 ml-1" />
            </div>
          </Link>

          <Link
            to="/analysis"
            className="glass-panel p-6 rounded-2xl glass-panel-hover border border-slate-800 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <DocumentIcon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Resume Analysis</h3>
              <p className="text-xs text-slate-400">Structured JSON breakdown of skills, experience, & projects.</p>
            </div>
            <div className="mt-4 flex items-center text-xs font-bold text-purple-400">
              <span>Explore Analysis</span>
              <ChevronRightIcon className="w-4 h-4 ml-1" />
            </div>
          </Link>

          <Link
            to="/ats"
            className="glass-panel p-6 rounded-2xl glass-panel-hover border border-slate-800 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <ChartIcon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">ATS Score Meter</h3>
              <p className="text-xs text-slate-400">Circular score meter, strengths, weaknesses & suggestions.</p>
            </div>
            <div className="mt-4 flex items-center text-xs font-bold text-emerald-400">
              <span>View ATS Score</span>
              <ChevronRightIcon className="w-4 h-4 ml-1" />
            </div>
          </Link>

          <Link
            to="/skill-gap"
            className="glass-panel p-6 rounded-2xl glass-panel-hover border border-slate-800 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <TargetIcon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Skill Gap Analysis</h3>
              <p className="text-xs text-slate-400">Identify missing skills against your target job role.</p>
            </div>
            <div className="mt-4 flex items-center text-xs font-bold text-cyan-400">
              <span>Check Skill Gap</span>
              <ChevronRightIcon className="w-4 h-4 ml-1" />
            </div>
          </Link>

          <Link
            to="/roadmap"
            className="glass-panel p-6 rounded-2xl glass-panel-hover border border-slate-800 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <RoadmapIcon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Learning Roadmap</h3>
              <p className="text-xs text-slate-400">Personalized weekly timeline UI with learning resources.</p>
            </div>
            <div className="mt-4 flex items-center text-xs font-bold text-amber-400">
              <span>View Roadmap</span>
              <ChevronRightIcon className="w-4 h-4 ml-1" />
            </div>
          </Link>

          <Link
            to="/jobs"
            className="glass-panel p-6 rounded-2xl glass-panel-hover border border-slate-800 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-pink-500/10 border border-pink-500/30 flex items-center justify-center text-pink-400">
                <BriefcaseIcon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-white">Job Recommendations</h3>
              <p className="text-xs text-slate-400">AI job role matches, match percentages, & salary estimates.</p>
            </div>
            <div className="mt-4 flex items-center text-xs font-bold text-pink-400">
              <span>Explore Jobs</span>
              <ChevronRightIcon className="w-4 h-4 ml-1" />
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
