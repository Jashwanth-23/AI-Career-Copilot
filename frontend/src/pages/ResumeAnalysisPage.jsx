import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api, { parseApiError } from "../services/api";
import { useResume } from "../context/ResumeContext";
import { useToast } from "../context/ToastContext";
import { CardSkeleton } from "../components/common/SkeletonLoaders";
import {
  DocumentIcon,
  SparklesIcon,
  UploadIcon,
  BriefcaseIcon,
  TargetIcon,
  AlertIcon,
} from "../components/common/Icons";

const ResumeAnalysisPage = () => {
  const { activeResume } = useResume();
  const { showToast } = useToast();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);

  const fetchAnalysis = useCallback(async () => {
    if (!activeResume?.id || loading) return;

    try {
      setLoading(true);
      setError(null);
      const response = await api.post(`/resume/analyze/${activeResume.id}`);
      setAnalysisData(response.data);
    } catch (err) {
      console.error("Resume Analysis Error:", err);
      const message = parseApiError(err);
      setError(message);
      showToast(message, "error");
    } finally {
      setLoading(false);
    }
  }, [activeResume?.id, loading, showToast]);

  useEffect(() => {
    if (activeResume?.id) {
      fetchAnalysis();
    }
  }, [activeResume?.id]);

  if (!activeResume) {
    return (
      <div className="glass-panel p-10 rounded-3xl text-center border border-slate-800 space-y-4 max-w-xl mx-auto my-12">
        <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400">
          <DocumentIcon className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-white">No Resume Uploaded</h2>
        <p className="text-slate-400 text-sm">
          Please upload a resume first to extract and view structured AI analysis.
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

  const structured = analysisData?.structured_data || {};
  const personal = structured.personal_information || {};

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <SparklesIcon className="w-3.5 h-3.5" />
            <span>Gemini AI Parser</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white">Resume Analysis & Breakdown</h1>
          <p className="text-slate-400 text-sm mt-1">
            Document: <span className="text-indigo-400 font-semibold">{activeResume.original_filename}</span>
          </p>
        </div>

        {!loading && analysisData && (
          <div className="px-4 py-2 rounded-xl glass-panel border border-emerald-500/30 text-xs text-emerald-400 font-semibold flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Structured Data Extracted</span>
          </div>
        )}
      </div>

      {error && !loading && (
        <div className="glass-panel p-6 rounded-3xl border border-rose-500/30 bg-rose-950/10 text-center space-y-4 max-w-xl mx-auto my-6">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
            <AlertIcon className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Resume Analysis Unavailable</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{error}</p>
          <button
            onClick={fetchAnalysis}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-xs font-bold hover:shadow-glow transition-all disabled:opacity-50"
          >
            Retry Resume Analysis
          </button>
        </div>
      )}

      {loading ? (
        <div className="space-y-6">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : analysisData ? (
        <div className="space-y-6">
          {/* Summary & Candidate Overview Card */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 p-0.5 shadow-glow flex items-center justify-center">
                  <div className="w-full h-full bg-surface-900 rounded-[14px] flex items-center justify-center text-white font-black text-xl">
                    {personal.name ? personal.name.charAt(0) : "C"}
                  </div>
                </div>
                <div>
                  <h2 className="text-xl sm:text-2xl font-bold text-white">
                    {personal.name || "Candidate Profile"}
                  </h2>
                  <p className="text-xs text-slate-400">
                    {personal.email} {personal.phone && `• ${personal.phone}`} {personal.location && `• ${personal.location}`}
                  </p>
                </div>
              </div>
            </div>

            {/* Professional Summary */}
            {structured.summary && (
              <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  Professional Summary
                </h4>
                <p className="text-sm text-slate-300 leading-relaxed">{structured.summary}</p>
              </div>
            )}
          </div>

          {/* Skills Section */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <TargetIcon className="w-5 h-5 text-indigo-400" />
              <span>Extracted Skills</span>
            </h3>

            {structured.skills && structured.skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {structured.skills.map((skill, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 rounded-xl bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-xs font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No explicit skill keywords parsed.</p>
            )}
          </div>

          {/* Experience Timeline Section */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
              <BriefcaseIcon className="w-5 h-5 text-purple-400" />
              <span>Work Experience</span>
            </h3>

            {structured.experience && structured.experience.length > 0 ? (
              <div className="space-y-6">
                {structured.experience.map((exp, idx) => (
                  <div key={idx} className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <h4 className="text-base font-bold text-white">
                        {exp.position || "Position"} <span className="text-indigo-400 font-medium">@ {exp.company || "Company"}</span>
                      </h4>
                      <span className="text-xs text-slate-400 font-mono">
                        {exp.start_date} - {exp.end_date || "Present"}
                      </span>
                    </div>

                    {exp.description && exp.description.length > 0 && (
                      <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                        {exp.description.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    )}

                    {exp.technologies && exp.technologies.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-2">
                        {exp.technologies.map((tech, ti) => (
                          <span key={ti} className="px-2.5 py-0.5 rounded-md bg-slate-800 text-[11px] text-slate-400">
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No experience records detected.</p>
            )}
          </div>

          {/* Projects & Education Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Education */}
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
              <h3 className="text-lg font-bold text-white">Education History</h3>
              {structured.education && structured.education.length > 0 ? (
                <div className="space-y-4">
                  {structured.education.map((edu, ei) => (
                    <div key={ei} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                      <h4 className="text-sm font-bold text-white">{edu.institution}</h4>
                      <p className="text-xs text-indigo-300">{edu.degree} {edu.field_of_study && `in ${edu.field_of_study}`}</p>
                      <p className="text-[11px] text-slate-400">{edu.start_date} - {edu.end_date}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No education entries specified.</p>
              )}
            </div>

            {/* Projects */}
            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
              <h3 className="text-lg font-bold text-white">Projects</h3>
              {structured.projects && structured.projects.length > 0 ? (
                <div className="space-y-4">
                  {structured.projects.map((proj, pi) => (
                    <div key={pi} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                      <h4 className="text-sm font-bold text-white">{proj.name}</h4>
                      {proj.description && <p className="text-xs text-slate-300">{proj.description}</p>}
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {proj.technologies.map((t, ti) => (
                            <span key={ti} className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-purple-300">
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No projects specified.</p>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default ResumeAnalysisPage;
