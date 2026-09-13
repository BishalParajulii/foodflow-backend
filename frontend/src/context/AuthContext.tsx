import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, clearTokens, setTokens, User } from "../lib/backend";

type AuthState = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    password_confirm: string;
    first_name?: string;
    last_name?: string;
    phone?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("ff_user");
      if (raw && localStorage.getItem("ff_access")) setUser(JSON.parse(raw));
    } catch {
      // ignore corrupt storage
    }
    setLoading(false);
  }, []);

  async function login(email: string, password: string) {
    const data = await api.post<{ access: string; refresh: string; user: User }>(
      "/api/v1/auth/login/",
      { email, password }
    );
    setTokens(data.access, data.refresh);
    localStorage.setItem("ff_user", JSON.stringify(data.user));
    setUser(data.user);
  }

  async function register(data: {
    email: string;
    password: string;
    password_confirm: string;
    first_name?: string;
    last_name?: string;
    phone?: string;
  }) {
    const res = await api.post<{ access: string; refresh: string; user: User }>(
      "/api/v1/auth/signup/",
      data
    );
    setTokens(res.access, res.refresh);
    localStorage.setItem("ff_user", JSON.stringify(res.user));
    setUser(res.user);
  }

  async function logout() {
    try {
      const refresh = localStorage.getItem("ff_refresh");
      if (refresh) await api.post("/api/v1/auth/logout/", { refresh });
    } catch {
      // logout best-effort
    }
    clearTokens();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
