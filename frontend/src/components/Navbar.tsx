import Link from "next/link";

export default function Navbar() {
  return (
    <nav
      style={{
        background: "rgba(62,39,35,0.96)",
        backdropFilter: "blur(8px)",
        color: "var(--color-cream)",
        padding: "0.7rem 0",
        position: "sticky",
        top: 0,
        zIndex: 50,
        borderBottom: "3px solid var(--color-primary)",
      }}
    >
      <div
        className="container"
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem" }}
      >
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: "0.7rem", color: "var(--color-cream)" }}>
          <img
            src="/images/food.jpeg"
            alt="FoodFlow logo"
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "50%",
              objectFit: "cover",
              border: "2px solid var(--color-accent)",
            }}
          />
          <span style={{ fontSize: "1.4rem", fontWeight: 800, letterSpacing: "0.3px" }}>
            Food<span style={{ color: "var(--color-accent)" }}>Flow</span>
          </span>
        </Link>
        <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: "0.2rem" }}>
          <Link href="/" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>Home</Link>
          <Link href="/menu" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>Menu</Link>
          <Link href="/about" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>About</Link>
          <Link href="/contact" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>Contact</Link>
          <Link
            href="/menu"
            className="btn"
            style={{ padding: "0.5rem 1.1rem", fontSize: "0.9rem", borderRadius: "999px" }}
          >
            Order Now
          </Link>
        </div>
      </div>
    </nav>
  );
}
