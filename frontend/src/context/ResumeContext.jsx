import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import api, { parseApiError } from "../services/api";
import { useAuth } from "./AuthContext";

const ResumeContext = createContext(null);

export const ResumeProvider = ({ children }) => {
  const { isAuthenticated } = useAuth();

  const [activeResume, setActiveResumeState] = useState(() => {
    const saved = localStorage.getItem("activeResume");
    return saved ? JSON.parse(saved) : null;
  });

  const [resumeHistory, setResumeHistory] = useState([]);
  const [loadingResumes, setLoadingResumes] = useState(false);

  const [targetRole, setTargetRole] = useState("Full Stack Developer");
  const [experienceLevel, setExperienceLevel] = useState("Fresher");
  const [preferredLocation, setPreferredLocation] = useState("Remote");

  const setActiveResume = (resumeData) => {
    if (resumeData) {
      localStorage.setItem("activeResume", JSON.stringify(resumeData));
      setActiveResumeState(resumeData);
    } else {
      localStorage.removeItem("activeResume");
      setActiveResumeState(null);
    }
  };

  const fetchResumeHistory = useCallback(async () => {
    if (!isAuthenticated) {
      setResumeHistory([]);
      setActiveResumeState(null);
      localStorage.removeItem("activeResume");
      return;
    }

    try {
      setLoadingResumes(true);
      const response = await api.get("/resume/history");
      const list = response.data || [];
      setResumeHistory(list);

      // If activeResume is not set or not in current history, set to latest
      if (list.length > 0) {
        const stored = localStorage.getItem("activeResume");
        const currentActive = stored ? JSON.parse(stored) : null;
        const exists = currentActive && list.some((r) => r.id === currentActive.id);
        if (!exists) {
          setActiveResume(list[0]);
        }
      } else {
        setActiveResume(null);
      }
    } catch (err) {
      console.error("[ResumeContext.fetchResumeHistory] Failed:", err);
    } finally {
      setLoadingResumes(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchResumeHistory();
  }, [fetchResumeHistory]);

  const deleteResume = async (resumeId) => {
    try {
      await api.delete(`/resume/${resumeId}`);
      if (activeResume && activeResume.id === resumeId) {
        const remaining = resumeHistory.filter((r) => r.id !== resumeId);
        setActiveResume(remaining.length > 0 ? remaining[0] : null);
      }
      await fetchResumeHistory();
    } catch (err) {
      throw new Error(parseApiError(err));
    }
  };

  const downloadResume = async (resumeId, originalFilename) => {
    try {
      const response = await api.get(`/resume/download/${resumeId}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", originalFilename || `resume_${resumeId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      throw new Error(parseApiError(err));
    }
  };

  return (
    <ResumeContext.Provider
      value={{
        activeResume,
        setActiveResume,
        resumeHistory,
        loadingResumes,
        fetchResumeHistory,
        deleteResume,
        downloadResume,
        targetRole,
        setTargetRole,
        experienceLevel,
        setExperienceLevel,
        preferredLocation,
        setPreferredLocation,
      }}
    >
      {children}
    </ResumeContext.Provider>
  );
};

export const useResume = () => {
  const context = useContext(ResumeContext);
  if (!context) throw new Error("useResume must be used within ResumeProvider");
  return context;
};

