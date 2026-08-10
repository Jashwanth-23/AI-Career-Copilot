import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import { useResume } from "../context/ResumeContext";
import { useToast } from "../context/ToastContext";
import {
  UploadIcon,
  DocumentIcon,
  CheckIcon,
  AlertIcon,
  SparklesIcon,
  ChevronRightIcon,
} from "../components/common/Icons";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc"];

const ResumeUploadPage = () => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  const { setActiveResume } = useResume();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const validateFile = (file) => {
    if (!file) return false;
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      showToast("Invalid file format. Please upload a PDF (.pdf) or DOCX (.docx) document.", "error");
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      showToast(`File size exceeds 5MB limit (${(file.size / (1024 * 1024)).toFixed(2)}MB).`, "error");
      return false;
    }
    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        setUploadSuccess(null);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        setUploadSuccess(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      showToast("Please select a valid resume file first.", "warning");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setUploading(true);
      setProgress(20);

      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 15;
        });
      }, 150);

      const response = await api.post("/resume/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      clearInterval(interval);
      setProgress(100);

      const resumeData = response.data;
      setUploadSuccess(resumeData);
      setActiveResume(resumeData);
      showToast("Resume uploaded and parsed successfully!", "success");
    } catch (err) {
      console.error("Upload error:", err);
      const errorDetail = err.response?.data?.detail || "Failed to upload resume. Please try again.";
      showToast(errorDetail, "error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-2">
          <UploadIcon className="w-3.5 h-3.5" />
          <span>Resume Ingestion</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white">Upload Your Resume</h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload your latest PDF or DOCX resume document (max 5 MB) for AI parsing & analysis.
        </p>
      </div>

      {/* Main Upload Box */}
      <div className="glass-panel p-8 sm:p-10 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden">
        {/* Drag & Drop Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
            dragActive
              ? "border-indigo-400 bg-indigo-950/40 scale-[1.01]"
              : selectedFile
              ? "border-emerald-500/50 bg-emerald-950/20"
              : "border-slate-700 bg-slate-900/50 hover:border-slate-500 hover:bg-slate-900/80"
          }`}
        >
          <input
            type="file"
            id="resume-input"
            accept=".pdf,.docx,.doc"
            onChange={handleFileChange}
            className="hidden"
          />

          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center mx-auto mb-4 text-indigo-400">
            <UploadIcon className="w-8 h-8" />
          </div>

          {selectedFile ? (
            <div className="space-y-2">
              <span className="inline-flex items-center space-x-2 text-emerald-400 font-bold text-base">
                <CheckIcon className="w-5 h-5" />
                <span>File Selected</span>
              </span>
              <p className="text-white font-medium text-lg">{selectedFile.name}</p>
              <p className="text-xs text-slate-400">
                Size: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>

              <label
                htmlFor="resume-input"
                className="inline-block mt-3 text-xs text-indigo-400 underline font-semibold cursor-pointer hover:text-indigo-300"
              >
                Change File
              </label>
            </div>
          ) : (
            <div className="space-y-3">
              <h3 className="text-lg font-bold text-white">Drag & drop your resume file here</h3>
              <p className="text-xs text-slate-400">
                Supports PDF (.pdf) and Word (.docx) format up to 5MB
              </p>
              <label
                htmlFor="resume-input"
                className="inline-block px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-semibold text-xs cursor-pointer transition-colors shadow-sm"
              >
                Browse Files
              </label>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {uploading && (
          <div className="mt-6 space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-300">
              <span>Uploading & Processing Document...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-600 transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Upload Submit Action */}
        {selectedFile && !uploadSuccess && (
          <div className="mt-8 flex justify-end">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-sm hover:shadow-glow transition-all transform hover:-translate-y-0.5 disabled:opacity-50 flex items-center space-x-2"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <SparklesIcon className="w-4 h-4" />
                  <span>Start Upload & AI Processing</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Success Confirmation Card */}
        {uploadSuccess && (
          <div className="mt-8 glass-panel p-6 rounded-2xl border border-emerald-500/40 bg-emerald-950/30 space-y-4">
            <div className="flex items-center space-x-3 text-emerald-400">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <CheckIcon className="w-5 h-5" />
              </div>
              <h4 className="text-lg font-bold text-white">Upload Complete!</h4>
            </div>

            <div className="text-xs space-y-1 text-slate-300">
              <p><strong className="text-slate-400">Resume ID:</strong> #{uploadSuccess.id}</p>
              <p><strong className="text-slate-400">Original Name:</strong> {uploadSuccess.original_filename}</p>
              <p><strong className="text-slate-400">Uploaded At:</strong> {new Date(uploadSuccess.uploaded_at).toLocaleString()}</p>
            </div>

            <div className="pt-4 border-t border-emerald-500/30 flex flex-wrap gap-3">
              <button
                onClick={() => navigate("/analysis")}
                className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all flex items-center space-x-2 shadow-sm"
              >
                <span>View Full AI Analysis</span>
                <ChevronRightIcon className="w-4 h-4" />
              </button>

              <button
                onClick={() => navigate("/ats")}
                className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all flex items-center space-x-2 shadow-sm"
              >
                <span>Check ATS Score Meter</span>
                <ChevronRightIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Resume Upload History Section */}
      <ResumeHistoryList />
    </div>
  );
};

const ResumeHistoryList = () => {
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
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this resume?")) return;
    try {
      setDeletingId(id);
      await deleteResume(id);
      showToast("Resume deleted successfully.", "info");
    } catch (err) {
      showToast(err.message || "Failed to delete resume.", "error");
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownload = async (id, filename) => {
    try {
      await downloadResume(id, filename);
      showToast("Download started...", "success");
    } catch (err) {
      showToast(err.message || "Failed to download file.", "error");
    }
  };

  return (
    <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">Resume History</h3>
          <p className="text-xs text-slate-400">All uploaded resume documents linked to your account</p>
        </div>
        <button
          onClick={fetchResumeHistory}
          className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold underline"
        >
          Refresh List
        </button>
      </div>

      {loadingResumes ? (
        <div className="py-8 text-center text-slate-400 text-xs font-medium space-y-2">
          <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p>Loading resume history...</p>
        </div>
      ) : resumeHistory.length === 0 ? (
        <div className="py-8 text-center text-slate-500 text-sm">
          No resumes uploaded yet. Upload a document above to get started!
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] font-bold tracking-wider">
              <tr>
                <th className="p-3">Status</th>
                <th className="p-3">Filename</th>
                <th className="p-3">Uploaded</th>
                <th className="p-3">Size</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {resumeHistory.map((item) => {
                const isActive = activeResume?.id === item.id;
                return (
                  <tr key={item.id} className="hover:bg-slate-900/30 transition-colors">
                    <td className="p-3">
                      {isActive ? (
                        <span className="px-2.5 py-1 rounded-md bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 font-bold text-[10px] uppercase">
                          Active
                        </span>
                      ) : (
                        <button
                          onClick={() => {
                            setActiveResume(item);
                            showToast(`Set "${item.original_filename}" as active resume.`, "info");
                          }}
                          className="px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-400 font-medium text-[10px]"
                        >
                          Select
                        </button>
                      )}
                    </td>
                    <td className="p-3 font-semibold text-white">
                      <div className="flex items-center space-x-2">
                        <DocumentIcon className="w-4 h-4 text-indigo-400" />
                        <span>{item.original_filename}</span>
                      </div>
                    </td>
                    <td className="p-3 text-slate-400">
                      {new Date(item.uploaded_at).toLocaleDateString()}
                    </td>
                    <td className="p-3 text-slate-400">
                      {(item.file_size / (1024 * 1024)).toFixed(2)} MB
                    </td>
                    <td className="p-3 text-right space-x-2">
                      <button
                        onClick={() => handleDownload(item.id, item.original_filename)}
                        className="px-2.5 py-1 rounded-md bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 font-medium hover:bg-indigo-900/60 transition-colors"
                      >
                        Download
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        disabled={deletingId === item.id}
                        className="px-2.5 py-1 rounded-md bg-red-950/60 border border-red-500/30 text-red-300 font-medium hover:bg-red-900/60 transition-colors disabled:opacity-50"
                      >
                        {deletingId === item.id ? "Deleting..." : "Delete"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ResumeUploadPage;

