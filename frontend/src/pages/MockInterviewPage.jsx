import React, { useState, useEffect, useCallback } from "react";
import interviewService from "../services/interviewService";
import InterviewSetup from "../components/interview/InterviewSetup";
import InterviewQuestion from "../components/interview/InterviewQuestion";
import AnswerEvaluation from "../components/interview/AnswerEvaluation";
import InterviewResults from "../components/interview/InterviewResults";
import InterviewHistory from "../components/interview/InterviewHistory";

const MockInterviewPage = () => {
  const [viewMode, setViewMode] = useState("setup"); // setup, question, evaluation, results, history
  const [session, setSession] = useState(null);
  const [activeQuestion, setActiveQuestion] = useState(null);
  const [lastEvaluation, setLastEvaluation] = useState(null);
  const [reportData, setReportData] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Restore active session on initial page load (Browser Refresh Safety)
  useEffect(() => {
    const savedSessionId = localStorage.getItem("activeInterviewSessionId");
    if (savedSessionId) {
      restoreSession(Number(savedSessionId));
    }
  }, []);

  const restoreSession = async (sessionId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await interviewService.getSession(sessionId);
      setSession(data);
      setActiveQuestion(data.current_question);

      if (data.status === "completed") {
        setReportData(data);
        setViewMode("results");
      } else {
        setViewMode("question");
      }
    } catch (err) {
      console.warn("[MockInterviewPage] Active session recovery failed:", err.message);
      localStorage.removeItem("activeInterviewSessionId");
      setViewMode("setup");
    } finally {
      setLoading(false);
    }
  };

  // Start new interview session
  const handleStartInterview = async (startPayload) => {
    try {
      setLoading(true);
      setError(null);
      const data = await interviewService.startInterview(startPayload);
      setSession(data);
      setActiveQuestion(data.current_question);
      setLastEvaluation(null);
      setReportData(null);
      localStorage.setItem("activeInterviewSessionId", data.session_id);
      setViewMode("question");
    } catch (err) {
      setError(err.message || "Failed to start AI interview.");
    } finally {
      setLoading(false);
    }
  };

  // Submit candidate answer
  const handleSubmitAnswer = async (answerText) => {
    if (!session) return;
    try {
      setLoading(true);
      setError(null);
      const res = await interviewService.submitAnswer(session.session_id, answerText);

      setLastEvaluation(res.evaluation);

      if (res.next_question) {
        setActiveQuestion(res.next_question);
        setSession((prev) => ({
          ...prev,
          current_question_number: res.question_number,
        }));
      }

      if (res.completed) {
        localStorage.removeItem("activeInterviewSessionId");
      }

      setViewMode("evaluation");
    } catch (err) {
      setError(err.message || "Failed to process answer evaluation.");
    } finally {
      setLoading(false);
    }
  };

  // Continue to next question or view report
  const handleContinueAfterEvaluation = async () => {
    if (!session) return;

    // Check if session is completed or total questions reached
    if (session.current_question_number > session.total_questions || !activeQuestion || lastEvaluation && session.current_question_number === session.total_questions && !activeQuestion?.user_answer) {
      try {
        setLoading(true);
        const report = await interviewService.getReport(session.session_id);
        setReportData(report);
        localStorage.removeItem("activeInterviewSessionId");
        setViewMode("results");
      } catch (err) {
        setError(err.message || "Failed to load final report.");
      } finally {
        setLoading(false);
      }
    } else {
      setViewMode("question");
    }
  };

  // Practice Again (Create new session)
  const handlePracticeAgain = () => {
    localStorage.removeItem("activeInterviewSessionId");
    setSession(null);
    setActiveQuestion(null);
    setLastEvaluation(null);
    setReportData(null);
    setError(null);
    setViewMode("setup");
  };

  // View specific session report from history
  const handleViewSessionReport = async (sessionId) => {
    try {
      setLoading(true);
      setError(null);
      const report = await interviewService.getReport(sessionId);
      setReportData(report);
      setSession({
        session_id: report.session_id,
        target_role: report.target_role,
        interview_type: report.interview_type,
        difficulty: report.difficulty,
        total_questions: report.total_questions,
        overall_score: report.overall_score,
        performance_rating: report.performance_rating,
        final_report: report.report,
      });
      setViewMode("results");
    } catch (err) {
      setError(err.message || "Failed to retrieve session report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-950 text-slate-100 p-4 sm:p-6 lg:p-8">
      {/* Top Header Navigation Tabs */}
      <div className="max-w-4xl mx-auto flex items-center justify-between border-b border-slate-800/80 pb-4 mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 p-0.5 shadow-glow flex items-center justify-center text-lg">
            🎤
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              AI Mock Interview
            </h1>
            <p className="text-xs text-slate-400">
              Personalized, adaptive technical & behavioral interview practice
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {viewMode !== "setup" && (
            <button
              type="button"
              onClick={handlePracticeAgain}
              className="px-3.5 py-2 rounded-xl bg-surface-900 border border-slate-800 text-slate-300 font-semibold text-xs hover:text-white hover:bg-slate-800 transition-all"
            >
              + New Interview
            </button>
          )}

          <button
            type="button"
            onClick={() => setViewMode("history")}
            className={`px-3.5 py-2 rounded-xl border font-semibold text-xs transition-all ${
              viewMode === "history"
                ? "bg-indigo-600 text-white border-indigo-400 shadow-glow"
                : "bg-surface-900 border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800"
            }`}
          >
            History
          </button>
        </div>
      </div>

      {/* Dynamic View Rendering */}
      <main>
        {viewMode === "setup" && (
          <InterviewSetup
            onStart={handleStartInterview}
            loading={loading}
            error={error}
          />
        )}

        {viewMode === "question" && (
          <InterviewQuestion
            session={session}
            activeQuestion={activeQuestion}
            onSubmitAnswer={handleSubmitAnswer}
            loading={loading}
            error={error}
          />
        )}

        {viewMode === "evaluation" && (
          <AnswerEvaluation
            evaluation={lastEvaluation}
            onContinue={handleContinueAfterEvaluation}
            isLastQuestion={session?.current_question_number >= session?.total_questions}
            loading={loading}
          />
        )}

        {viewMode === "results" && (
          <InterviewResults
            session={session}
            reportData={reportData}
            onPracticeAgain={handlePracticeAgain}
            onViewHistory={() => setViewMode("history")}
          />
        )}

        {viewMode === "history" && (
          <InterviewHistory
            onViewSessionReport={handleViewSessionReport}
            onStartNew={handlePracticeAgain}
          />
        )}
      </main>
    </div>
  );
};

export default MockInterviewPage;
