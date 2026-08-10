import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import api, { parseApiError } from "../services/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [loading, setLoading] = useState(true);

  // Auto-login / session verification on mount
  const checkAuth = useCallback(async () => {
    const savedToken = localStorage.getItem("token");
    if (!savedToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await api.get("/auth/me");
      setUser(response.data);
      setToken(savedToken);
    } catch (error) {
      console.error("[AuthContext.checkAuth] Verification error:", error);
      localStorage.removeItem("token");
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Login handler
  const login = async (email, password) => {
    const payload = {
      email: email.trim(),
      password: password,
    };

    console.log("[AuthContext.login] Request URL: /auth/login", { payload });

    const response = await api.post("/auth/login", payload);
    const { access_token } = response.data;

    console.log("[AuthContext.login] Token acquired successfully:", response.data);

    localStorage.setItem("token", access_token);
    setToken(access_token);

    // Fetch user profile
    const userRes = await api.get("/auth/me", {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    setUser(userRes.data);
    return userRes.data;
  };

  // Register handler
  const register = async (name, email, password) => {
    const payload = {
      name: name.trim(),
      email: email.trim(),
      password: password,
    };

    console.log("[AuthContext.register] Request URL: /auth/register", { payload });

    const response = await api.post("/auth/register", payload);

    console.log("[AuthContext.register] Registration response:", {
      status: response.status,
      response: response.data,
    });

    // Attempt auto-login after successful registration
    try {
      await login(email, password);
    } catch (loginError) {
      console.warn("[AuthContext.register] Auto-login failed after registration:", loginError);
    }

    return response.data;
  };

  // Logout handler
  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
