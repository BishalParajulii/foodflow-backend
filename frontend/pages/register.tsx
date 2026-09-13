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

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    phone: "",
    password: "",
    password_confirm: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function set(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value }));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (form.password !== form.password_confirm) {
      setError("Passwords do not match");
      return;
    }
    setBusy(true);
    try {
      await register({ ...form, email: form.email.trim() });
      router.push("/menu");
    } catch (err: any) {
      setError(err instanceof BackendError ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "440px" }}>
        <h1>Create account</h1>
        <p style={{ color: "#6d5c55" }}>Sign up to place orders (Cash on Delivery).</p>
        <form onSubmit={onSubmit} style={{ display: "grid", gap: "0.9rem", marginTop: "1rem" }}>
          <input style={inputStyle} type="email" required placeholder="Email" value={form.email} onChange={set("email")} />
          <div style={{ display: "flex", gap: "0.9rem" }}>
            <input style={inputStyle} placeholder="First name" value={form.first_name} onChange={set("first_name")} />
            <input style={inputStyle} placeholder="Last name" value={form.last_name} onChange={set("last_name")} />
          </div>
          <input style={inputStyle} placeholder="Phone (optional)" value={form.phone} onChange={set("phone")} />
          <input style={inputStyle} type="password" required placeholder="Password (min 8 chars)" value={form.password} onChange={set("password")} />
          <input style={inputStyle} type="password" required placeholder="Confirm password" value={form.password_confirm} onChange={set("password_confirm")} />
          {error && <p style={{ color: "var(--color-primary)", margin: 0 }}>{error}</p>}
          <button type="submit" disabled={busy}>
            {busy ? "Creating…" : "Create account"}
          </button>
        </form>
        <p style={{ marginTop: "1rem" }}>
          Have an account? <Link href="/login">Log in</Link>
        </p>
      </div>
    </section>
  );
}
