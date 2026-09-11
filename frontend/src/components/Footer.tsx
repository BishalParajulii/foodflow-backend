import Link from "next/link";

export default function Footer() {
  return (
    <footer
      style={{
        background: "#2a1a17",
        color: "var(--color-cream)",
        padding: "0",
        fontSize: "0.92rem",
        marginTop: "0",
      }}
    >
      {/* Top banner with food image */}
      <div
        style={{
          backgroundImage:
            "linear-gradient(rgba(42,26,23,0.88), rgba(42,26,23,0.88)), url('/images/food.jpeg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          padding: "3rem 1.5rem",
          textAlign: "center",
        }}
      >
        <h2 style={{ color: "#fff", margin: "0 0 0.5rem", fontSize: "1.8rem" }}>
          Hungry? Let&apos;s fix that.
        </h2>
        <p style={{ color: "#F2CC8F", margin: "0 0 1.5rem" }}>
          Fresh yomari, momos & biryani — ready in minutes.
        </p>
        <Link href="/menu" className="btn">
          View Full Menu →
        </Link>
      </div>

      <div
        className="container"
        style={{
          display: "grid",
          gap: "2rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          padding: "2.5rem 1.5rem",
        }}
      >
        <div style={{ display: "flex", gap: "0.8rem", alignItems: "flex-start" }}>
          <img
            src="/images/food.jpeg"
            alt="FoodFlow"
            style={{ width: "52px", height: "52px", borderRadius: "12px", objectFit: "cover" }}
          />
          <div>
            <strong style={{ fontSize: "1.1rem" }}>FoodFlow Restaurant</strong>
            <p style={{ margin: "0.4rem 0 0", opacity: 0.8, lineHeight: 1.5 }}>
              Authentic Nepali & Indian kitchen in the heart of the city.
            </p>
          </div>
        </div>
        <div>
          <strong>Explore</strong>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", marginTop: "0.7rem" }}>
            <Link href="/" style={{ color: "#F2CC8F" }}>Home</Link>
            <Link href="/menu" style={{ color: "#F2CC8F" }}>Menu</Link>
            <Link href="/about" style={{ color: "#F2CC8F" }}>About</Link>
            <Link href="/contact" style={{ color: "#F2CC8F" }}>Contact</Link>
          </div>
        </div>
        <div>
          <strong>Hours</strong>
          <p style={{ margin: "0.7rem 0 0", opacity: 0.85, lineHeight: 1.7 }}>
            Sun–Fri: 10am – 10pm
            <br />
            Sat: 11am – 11pm
            <br />
            📞 01-4444444
          </p>
        </div>
      </div>

      <div
        style={{
          borderTop: "1px solid rgba(255,255,255,0.12)",
          textAlign: "center",
          padding: "1.2rem",
          opacity: 0.75,
        }}
      >
        © {new Date().getFullYear()} FoodFlow Restaurant. All rights reserved.
      </div>
    </footer>
  );
}
