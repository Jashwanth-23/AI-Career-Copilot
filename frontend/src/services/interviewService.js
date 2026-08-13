import api, { parseApiError } from "./api";

/**
 * Service for interacting with backend AI Mock Interview REST endpoints.
 */

// Extended timeout for Gemini LLM question generation & answer evaluations
const AI_TIMEOUT = 45000;

export const interviewService = {
  /**
   * Start a new personalized AI mock interview session.
   */
  startInterview: async (payload) => {
    try {
      const response = await api.post("/interview/start", payload, {
        timeout: AI_TIMEOUT,
      });
      return response.data;
    } catch (error) {
      throw new Error(parseApiError(error));
    }
  },

  /**
   * Retrieve current interview session state and active question.
   */
  getSession: async (sessionId) => {
    try {
      const response = await api.get(`/interview/session/${sessionId}`);
      return response.data;
    } catch (error) {
      throw new Error(parseApiError(error));
    }
  },

  /**
   * Submit candidate's text answer for evaluation and get next question.
   */
  submitAnswer: async (sessionId, answer) => {
    try {
      const response = await api.post(
        `/interview/session/${sessionId}/answer`,
        { answer },
        { timeout: AI_TIMEOUT }
      );
      return response.data;
    } catch (error) {
      throw new Error(parseApiError(error));
    }
  },

  /**
   * Finalize interview session and generate complete report.
   */
  finishInterview: async (sessionId) => {
    try {
      const response = await api.post(
        `/interview/session/${sessionId}/finish`,
        {},
        { timeout: AI_TIMEOUT }
      );
      return response.data;
    } catch (error) {
      throw new Error(parseApiError(error));
    }
  },

  /**
   * Get final performance report for completed interview.
   */
  getReport: async (sessionId) => {
    try {
      const response = await api.get(`/interview/session/${sessionId}/report`);
      return response.data;
    } catch (error) {
      throw new Error(parseApiError(error));
    }
  },

  /**
   * Fetch history of user's past mock interview practice sessions.
   */
  getHistory: async () => {
    try {
      const response = await api.get("/interview/history");
      return response.data;
    } catch (error) {
      throw new Error(parseApiError(error));
    }
  },

  /**
   * Delete an interview session from history.
   */
  deleteInterview: async (sessionId) => {
    try {
      const response = await api.delete(`/interview/session/${sessionId}`);
      return response.data;
    } catch (error) {
      throw new Error(parseApiError(error));
    }
  },
};

export default interviewService;
