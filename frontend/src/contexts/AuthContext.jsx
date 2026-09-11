import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, formatApiError } from "@/lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [state, setState] = useState({
    status: "loading", // 'loading' | 'authenticated' | 'unauthenticated'
    user: null,
    company: null,
    role: null,
    needsOnboarding: false,
  });

  const setAuthed = useCallback((payload) => {
    setState({
      status: "authenticated",
      user: payload.user,
      company: payload.active_company || null,
      role: payload.active_role || null,
      needsOnboarding: !!payload.needs_onboarding,
    });
  }, []);

  const setAnonymous = useCallback(() => {
    setState({
      status: "unauthenticated",
      user: null,
      company: null,
      role: null,
      needsOnboarding: false,
    });
  }, []);

  const bootstrap = useCallback(async () => {
    try {
      const { data } = await api.get("/auth/me");
      setAuthed(data);
    } catch (e) {
      setAnonymous();
    }
  }, [setAuthed, setAnonymous]);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const login = useCallback(
    async ({ email, password }) => {
      const { data } = await api.post("/auth/login", { email, password });
      setAuthed(data);
      return data;
    },
    [setAuthed]
  );

  const register = useCallback(
    async (payload) => {
      const { data } = await api.post("/auth/register", payload);
      setAuthed(data);
      return data;
    },
    [setAuthed]
  );

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      /* ignore */
    }
    setAnonymous();
  }, [setAnonymous]);

  const refreshContext = useCallback(async () => {
    const { data } = await api.get("/auth/me");
    setAuthed(data);
    return data;
  }, [setAuthed]);

  const value = useMemo(
    () => ({ ...state, login, register, logout, refreshContext, formatApiError }),
    [state, login, register, logout, refreshContext]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
