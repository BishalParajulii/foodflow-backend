import { useState } from "react";
import { useRouter } from "next/router";

export default function AdminLogin() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Login failed");
      // Login successful, redirect to dashboard
      router.push("/admin/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f8f5f0", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ background: "#fff", padding: "2rem", borderRadius: "1rem", boxShadow: "0 4px 20px rgba(0,0,0,0.08)", width: "100%", maxWidth: "400px" }}>
        <h2 style={{ textAlign: "center", marginBottom: "1.5rem", color: "var(--color-dark)" }}>Admin Login</h2>
        {error && (
          <p style={{ color: "#c00", textAlign: "center", marginBottom: "1rem" }}>
            {error}
          </p>
        )}
        <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
          <label>
            Username
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{ width: "100%", padding: "0.75rem", border: "1px solid #ccc", borderRadius: "0.4rem" }}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: "100%", padding: "0.75rem", border: "1px solid #ccc", borderRadius: "0.4rem" }}
            />
          </label>
          <button type="submit" disabled={loading} className="btn" style={{ cursor: loading ? "not-allowed" : "pointer" }}>
            {loading ? "Logging in…" : "Sign In"}
          </button>
        </form>
        <p style={{ textAlign: "center", marginTop: "1.5rem", fontSize: "0.9rem", color: "#666" }}>
          Demo credentials: username <strong>admin</strong>, password <strong>admin123</strong>
        </p>
      </div>
    </div>
  );
}