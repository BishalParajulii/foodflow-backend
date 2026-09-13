import { useState } from "react";

export default function Contact() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "success" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("sending");
    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, message }),
      });
      if (!res.ok) throw new Error("Network error");
      await res.json(); // we don't need data
      setStatus("success");
      setName("");
      setEmail("");
      setMessage("");
    } catch (err: any) {
      console.error(err);
      setStatus("error");
    }
  };

  return (
    <section className="section-padding">
      <div
        className="container"
        style={{
          display: "grid",
          gap: "2.5rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(min(300px, 100%), 1fr))",
          alignItems: "stretch",
        }}
      >
        {/* Left image + info */}
        <div
          style={{
            borderRadius: "1.2rem",
            overflow: "hidden",
            background: "#fff",
            border: "1px solid #f0e2c8",
            boxShadow: "0 8px 24px rgba(62,39,35,0.08)",
          }}
        >
          <img
            src="/images/food.jpeg"
            alt="Visit us"
            style={{ width: "100%", height: "clamp(180px, 45vw, 260px)", objectFit: "cover", display: "block" }}
          />
          <div style={{ padding: "1.8rem" }}>
            <h1 style={{ margin: "0 0 0.6rem" }}>Contact Us</h1>
            <p style={{ color: "#6d5c55", marginBottom: "1.2rem" }}>
              Got questions, feedback, or want to book a table? Reach out below.
            </p>
            <p style={{ lineHeight: 1.8, margin: 0 }}>
              📍 Thamel, Kathmandu
              <br />
              📞 01-4444444
              <br />
              ✉️ hello@foodflow.com
              <br />
              🕒 Sun–Fri 10am–10pm
            </p>
          </div>
        </div>

        {/* Right form */}
        <div
          style={{
            background: "#fff",
            border: "1px solid #f0e2c8",
            borderRadius: "1.2rem",
            padding: "2rem",
            boxShadow: "0 8px 24px rgba(62,39,35,0.08)",
          }}
        >
          <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
            <label>
              Name
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ width: "100%", padding: "0.75rem", border: "1px solid #ccc", borderRadius: "0.4rem", marginTop: "0.3rem" }}
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ width: "100%", padding: "0.75rem", border: "1px solid #ccc", borderRadius: "0.4rem", marginTop: "0.3rem" }}
              />
            </label>
            <label>
              Message
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={5}
                required
                style={{ width: "100%", padding: "0.75rem", border: "1px solid #ccc", borderRadius: "0.4rem", marginTop: "0.3rem" }}
              />
            </label>
            <button type="submit" disabled={status === "sending"} className="btn">
              {status === "sending" ? "Sending…" : "Send Message"}
            </button>
          </form>

          {status === "success" && (
            <p style={{ textAlign: "center", marginTop: "1.5rem", color: "var(--color-primary)" }}>
              Thanks! We’ll get back to you shortly.
            </p>
          )}
          {status === "error" && (
            <p style={{ textAlign: "center", marginTop: "1.5rem", color: "#c00" }}>
              Oops! Something went wrong. Please try again later.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}