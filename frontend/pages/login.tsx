import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { useAuth } from "../src/context/AuthContext";
import { BackendError } from "../src/lib/backend";

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "0.7rem 0.9rem",
  borderRadius: "0.6rem",
  border: "1px solid #e0cfb8",
  fontSize: "1rem",
  boxSizing: "border-box",
};

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(email.trim(), password);
      const next = typeof router.query.next === "string" ? router.query.next : "/menu";
      router.push(next);
    } catch (err: any) {
      setError(err instanceof BackendError ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "440px" }}>
        <h1>Log in</h1>
        <p style={{ color: "#6d5c55" }}>Welcome back. Log in to order.</p>
        <form onSubmit={onSubmit} style={{ display: "grid", gap: "0.9rem", marginTop: "1rem" }}>
          <input
            style={inputStyle}
            type="email"
            required
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            style={inputStyle}
            type="password"
            required
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p style={{ color: "var(--color-primary)", margin: 0 }}>{error}</p>}
          <button type="submit" disabled={busy}>
            {busy ? "Logging in…" : "Log in"}
          </button>
        </form>
        <p style={{ marginTop: "1rem" }}>
          No account? <Link href="/register">Create one</Link>
        </p>
      </div>
    </section>
  );
}
