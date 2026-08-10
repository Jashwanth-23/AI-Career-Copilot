import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Requirement #7: 15 seconds timeout
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: Attach JWT token & add detailed console logs (Requirement #8)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const fullUrl = `${config.baseURL || ""}${config.url || ""}`;
    console.log(`[API Request] URL: ${config.method?.toUpperCase()} ${fullUrl}`, {
      url: fullUrl,
      method: config.method?.toUpperCase(),
      payload: config.data || null,
      headers: config.headers,
    });

    return config;
  },
  (error) => {
    console.error("[API Request Error]", error);
    return Promise.reject(error);
  }
);

// Response interceptor: Log response data & handle 401 unauthenticated (Requirement #8)
api.interceptors.response.use(
  (response) => {
    const fullUrl = `${response.config.baseURL || ""}${response.config.url || ""}`;
    console.log(`[API Response] ${response.status} ${response.config.method?.toUpperCase()} ${fullUrl}`, {
      url: fullUrl,
      status: response.status,
      response: response.data,
    });
    return response;
  },
  (error) => {
    const fullUrl = error.config ? `${error.config.baseURL || ""}${error.config.url || ""}` : "Unknown URL";
    console.error(`[API Error] ${error.config?.method?.toUpperCase() || ""} ${fullUrl}`, {
      url: fullUrl,
      status: error.response?.status || "NO_RESPONSE",
      response: error.response?.data || null,
      message: error.message,
      code: error.code,
    });

    if (error.response && error.response.status === 401) {
      const requestUrl = error.config?.url || "";
      if (!requestUrl.includes("/auth/login") && !requestUrl.includes("/auth/register")) {
        localStorage.removeItem("token");
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Helper utility to parse human-readable error messages from backend responses.
 */
export const parseApiError = (error) => {
  if (!error) return "An unexpected error occurred.";

  if (error.code === "ECONNABORTED" || error.message?.includes("timeout")) {
    return "Request timed out (15 seconds exceeded). The server took too long to respond. Please try again.";
  }

  if (error.response) {
    const status = error.response.status;

    if (status === 429) {
      return "AI service quota is temporarily exhausted. Please wait a little and try again.";
    }

    if (status === 401 || status === 403) {
      const detail = error.response.data?.detail;
      if (typeof detail === "string" && detail.includes("Gemini")) {
        return "Gemini API authentication failed. Please check the API configuration.";
      }
    }

    const detail = error.response.data?.detail;

    if (typeof detail === "string") {
      if (detail.includes("RESOURCE_EXHAUSTED") || detail.includes("quota")) {
        return "AI service quota is temporarily exhausted. Please wait a little and try again.";
      }
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => (typeof item === "string" ? item : item.msg || JSON.stringify(item)))
        .join("; ");
    }

    if (detail && typeof detail === "object") {
      return detail.msg || JSON.stringify(detail);
    }

    if (error.response.data?.message) {
      return error.response.data.message;
    }

    if (status >= 500) {
      return "AI analysis failed. Please try again.";
    }

    return `Server returned error (${status}).`;
  }

  if (error.request) {
    return "Unable to connect to backend server. Please verify backend is running on http://localhost:8000.";
  }

  return error.message || "An error occurred while setting up the request.";
};

export default api;