import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useResume } from "../context/ResumeContext";
import { useToast } from "../context/ToastContext";
import {
  DocumentIcon,
  UploadIcon,
  CheckIcon,
  SparklesIcon,
  ChevronRightIcon,
  ChartIcon,
  TargetIcon,
  RoadmapIcon,
  BriefcaseIcon,
} from "../components/common/Icons";

const MyResumesPage = () => {
  const {
    resumeHistory,
    loadingResumes,
    activeResume,
    setActiveResume,
    deleteResume,
    downloadResume,
    fetchResumeHistory,
  } = useResume();

  const { showToast } = useToast();
  const navigate = useNavigate();
  const [deletingId, setDeletingId] = useState(null);

  const handleSetActive = (item) => {
    setActiveResume(item);
    showToast(`"${item.original_filename}" is now set as your active resume.`, "success");
  };

  const handleOpenAnalysis = (item) => {
    setActiveResume(item);
    navigate("/analysis");
  };

  const handleDownload = async (id, filename) => {
    try {
      await downloadResume(id, filename);
      showToast("Download started...", "info");
    } catch (err) {
      showToast(err.message || "Failed to download resume.", "error");
    }
  };

  const handleDelete = async (id, filename) => {
    if (
      !window.confirm(
        `Are you sure you want to delete "${filename}"? This action cannot be undone.`
      )
    ) {
      return;
    }

    try {
      setDeletingId(id);
      await deleteResume(id);
      showToast(`Resume "${filename}" deleted successfully.`, "info");
    } catch (err) {
      showToast(err.message || "Failed to delete resume.", "error");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <DocumentIcon className="w-3.5 h-3.5" />
            <span>Candidate Portfolio</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">My Resumes</h1>
          <p className="text-slate-400 text-sm mt-1">
            Maintain multiple candidate resumes and seamlessly switch active resume profiles.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchResumeHistory}
            disabled={loadingResumes}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 font-semibold text-xs transition-all disabled:opacity-50"
          >
            {loadingResumes ? "Refreshing..." : "Refresh List"}
          </button>

          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-xs hover:shadow-glow transition-all"
          >
            <UploadIcon className="w-4 h-4" />
            <span>+ Upload New Resume</span>
          </Link>
        </div>
      </div>

      {/* Currently Active Resume Highlight Banner */}
      {activeResume && (
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-emerald-500/40 bg-gradient-to-r from-emerald-950/30 via-surface-900 to-indigo-950/20 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
                <DocumentIcon className="w-6 h-6" />
              </div>
              <div>
                <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-bold uppercase tracking-wider border border-emerald-500/40 mb-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Active Resume</span>
                </span>
                <h2 className="text-xl font-extrabold text-white">{activeResume.original_filename}</h2>
                <div className="flex items-center space-x-3 text-xs text-slate-400 mt-0.5">
                  <span>ID: #{activeResume.id}</span>
                  <span>•</span>
                  <span>Uploaded: {new Date(activeResume.uploaded_at).toLocaleDateString()}</span>
                  <span>•</span>
                  <span>Size: {(activeResume.file_size / (1024 * 1024)).toFixed(2)} MB</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleOpenAnalysis(activeResume)}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-xs hover:shadow-glow transition-all flex items-center space-x-2 self-start sm:self-auto"
            >
              <SparklesIcon className="w-4 h-4" />
              <span>Open AI Analysis</span>
              <ChevronRightIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Active Resume Quick Navigation Shortcuts */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Link
              to="/ats"
              className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 transition-all text-xs font-semibold text-slate-300 flex items-center space-x-2 group"
            >
              <ChartIcon className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
              <span>ATS Score Meter</span>
            </Link>

            <Link
              to="/skill-gap"
              className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 transition-all text-xs font-semibold text-slate-300 flex items-center space-x-2 group"
            >
              <TargetIcon className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
              <span>Skill Gap Analysis</span>
            </Link>

            <Link
              to="/roadmap"
              className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 transition-all text-xs font-semibold text-slate-300 flex items-center space-x-2 group"
            >
              <RoadmapIcon className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
              <span>Learning Roadmap</span>
            </Link>

            <Link
              to="/jobs"
              className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 transition-all text-xs font-semibold text-slate-300 flex items-center space-x-2 group"
            >
              <BriefcaseIcon className="w-4 h-4 text-pink-400 group-hover:scale-110 transition-transform" />
              <span>Job Recommendations</span>
            </Link>
          </div>
        </div>
      )}

      {/* Resumes Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">All Saved Resumes ({resumeHistory.length})</h2>
          <span className="text-xs text-slate-400">Isolated to your account</span>
        </div>

        {loadingResumes ? (
          <div className="glass-panel p-12 rounded-3xl text-center space-y-3">
            <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-xs text-slate-400 font-medium">Fetching saved candidate resumes...</p>
          </div>
        ) : resumeHistory.length === 0 ? (
          <div className="glass-panel p-12 rounded-3xl text-center space-y-4 max-w-lg mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400">
              <DocumentIcon className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white">No Resumes Found</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              You haven't uploaded any resumes yet. Upload your first resume to generate personalized AI candidate profiles!
            </p>
            <Link
              to="/upload"
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-xs hover:shadow-glow transition-all"
            >
              <UploadIcon className="w-4 h-4" />
              <span>Upload Resume Now</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {resumeHistory.map((item) => {
              const isActive = activeResume?.id === item.id;
              const isDeleting = deletingId === item.id;

              return (
                <div
                  key={item.id}
                  className={`glass-panel p-6 rounded-3xl border transition-all duration-300 flex flex-col justify-between space-y-5 ${
                    isActive
                      ? "border-emerald-500/50 bg-emerald-950/10 shadow-glow"
                      : "border-slate-800 hover:border-slate-700 bg-surface-900/60"
                  }`}
                >
                  <div className="space-y-4">
                    {/* Badge & Title */}
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center space-x-3">
                        <div
                          className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-xs flex-shrink-0 ${
                            isActive
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                              : "bg-slate-800 text-indigo-400 border border-slate-700"
                          }`}
                        >
                          <DocumentIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="text-base font-bold text-white truncate max-w-[220px]">
                            {item.original_filename}
                          </h3>
                          <span className="text-[11px] text-slate-400 font-mono">ID: #{item.id}</span>
                        </div>
                      </div>

                      {isActive ? (
                        <span className="px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 font-bold text-[10px] uppercase tracking-wider flex items-center space-x-1">
                          <CheckIcon className="w-3 h-3" />
                          <span>Active</span>
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px] font-semibold uppercase">
                          Saved
                        </span>
                      )}
                    </div>

                    {/* Resume Details Metadata */}
                    <div className="grid grid-cols-2 gap-2 p-3 rounded-2xl bg-slate-900/60 border border-slate-800/60 text-xs text-slate-300">
                      <div>
                        <span className="text-[10px] font-bold uppercase text-slate-400 block">Uploaded On</span>
                        <span className="font-medium text-slate-200">
                          {new Date(item.uploaded_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] font-bold uppercase text-slate-400 block">File Size</span>
                        <span className="font-medium text-slate-200">
                          {(item.file_size / (1024 * 1024)).toFixed(2)} MB
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Actions Footer */}
                  <div className="pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      {!isActive && (
                        <button
                          onClick={() => handleSetActive(item)}
                          className="px-3 py-1.5 rounded-xl bg-indigo-950/80 hover:bg-indigo-900/80 border border-indigo-500/40 text-indigo-300 text-xs font-bold transition-all"
                        >
                          ★ Set Active
                        </button>
                      )}

                      <button
                        onClick={() => handleOpenAnalysis(item)}
                        className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-all inline-flex items-center space-x-1"
                      >
                        <span>Open</span>
                        <ChevronRightIcon className="w-3.5 h-3.5 text-slate-400" />
                      </button>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleDownload(item.id, item.original_filename)}
                        className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium transition-colors"
                      >
                        Download
                      </button>

                      <button
                        onClick={() => handleDelete(item.id, item.original_filename)}
                        disabled={isDeleting}
                        className="px-3 py-1.5 rounded-xl bg-rose-950/50 hover:bg-rose-900/60 border border-rose-500/30 text-rose-300 text-xs font-medium transition-colors disabled:opacity-50"
                      >
                        {isDeleting ? "Deleting..." : "Delete"}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyResumesPage;
