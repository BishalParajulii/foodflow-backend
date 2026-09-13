import Hero from "../src/components/Hero";
import Link from "next/link";

const features = [
  {
    icon: "🌿",
    title: "Fresh Ingredients",
    text: "Locally sourced vegetables, spices, and meats — prepped fresh every morning.",
  },
  {
    icon: "👨‍🍳",
    title: "Authentic Recipes",
    text: "Handed down through generations, crafted by expert Newari & Indian chefs.",
  },
  {
    icon: "🚚",
    title: "Quick Delivery",
    text: "Enjoy your meal hot and fresh, right at your doorstep in ~25 mins.",
  },
];

export default function Home() {
  return (
    <>
      <Hero />

      {/* Why Choose */}
      <section className="section-padding">
        <div className="container">
          <h2 className="text-center" style={{ marginBottom: "0.5rem" }}>Why Choose FoodFlow?</h2>
          <p className="text-center" style={{ maxWidth: "700px", margin: "0 auto 2.5rem", color: "#6d5c55" }}>
            We bring the authentic flavors of Nepal and India to your table, using
            traditional recipes and fresh, locally‑sourced ingredients.
          </p>
          <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(min(260px, 100%), 1fr))" }}>
            {features.map((f) => (
              <div
                key={f.title}
                style={{
                  background: "#fff",
                  border: "1px solid #f0e2c8",
                  borderRadius: "1rem",
                  padding: "2rem 1.5rem",
                  textAlign: "center",
                  boxShadow: "0 4px 16px rgba(62,39,35,0.06)",
                }}
              >
                <div style={{ fontSize: "2.2rem", marginBottom: "0.8rem" }}>{f.icon}</div>
                <h3 style={{ margin: "0 0 0.6rem", color: "var(--color-dark)" }}>{f.title}</h3>
                <p style={{ margin: 0, color: "#6d5c55", fontSize: "0.95rem" }}>{f.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured dish spotlight */}
      <section style={{ background: "#fff", padding: "4rem 0", borderTop: "1px solid #f5e6c8", borderBottom: "1px solid #f5e6c8" }}>
        <div
          className="container"
          style={{
            display: "grid",
            gap: "3rem",
            gridTemplateColumns: "repeat(auto-fit, minmax(min(300px, 100%), 1fr))",
            alignItems: "center",
          }}
        >
          <div style={{ position: "relative" }}>
            <img
              src="/images/food.jpeg"
              alt="Yomari close-up"
              style={{
                width: "100%",
                height: "clamp(220px, 55vw, 380px)",
                objectFit: "cover",
                borderRadius: "1.2rem",
                boxShadow: "0 16px 40px rgba(62,39,35,0.18)",
              }}
            />
            <span
              style={{
                position: "absolute",
                bottom: "1rem",
                left: "1rem",
                background: "var(--color-primary)",
                color: "#fff",
                padding: "0.5rem 1rem",
                borderRadius: "999px",
                fontWeight: 700,
                fontSize: "0.85rem",
              }}
            >
              ⭐ Chef&apos;s Special
            </span>
          </div>
          <div>
            <p style={{ color: "var(--color-secondary)", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", fontSize: "0.85rem", margin: "0 0 0.6rem" }}>
              Dish of the week
            </p>
            <h2 style={{ margin: "0 0 1rem", fontSize: "clamp(1.6rem, 5vw, 2.2rem)", color: "var(--color-dark)" }}>
              Steamed Yomari with Chaku Filling
            </h2>
            <p style={{ color: "#6d5c55", lineHeight: 1.7, marginBottom: "1.5rem" }}>
              Soft rice-flour shells, molasses-sesame heart, served warm on a
              traditional clay plate. Sweet, nutty, unforgettable — just like in
              the photo, made fresh to order.
            </p>
            <ul style={{ listStyle: "none", padding: 0, margin: "0 0 1.8rem", display: "grid", gap: "0.6rem", color: "#3E2723" }}>
              <li>✅ Gluten-friendly rice flour</li>
              <li>✅ No preservatives, steamed not fried</li>
              <li>✅ Veg option available</li>
            </ul>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
              <Link href="/menu" className="btn">Order Yomari — Rs. 180</Link>
              <span style={{ color: "#888", fontSize: "0.9rem" }}>4.9 ★ (320 reviews)</span>
            </div>
          </div>
        </div>
      </section>

      {/* Gallery strip using same image with different crops */}
      <section className="section-padding">
        <div className="container">
          <h2 className="text-center">Fresh From Our Kitchen</h2>
          <p className="text-center" style={{ color: "#6d5c55", marginBottom: "2rem" }}>
            One signature dish, endless cravings — served all day.
          </p>
          <div style={{ display: "grid", gap: "1.2rem", gridTemplateColumns: "repeat(auto-fit, minmax(min(220px, 100%), 1fr))" }}>
            {[
              { pos: "center", label: "Steamed Fresh" },
              { pos: "left center", label: "Chaku Filled" },
              { pos: "right center", label: "Served Warm" },
            ].map((g) => (
              <div key={g.label} style={{ position: "relative", borderRadius: "1rem", overflow: "hidden", height: "220px" }}>
                <img
                  src="/images/food.jpeg"
                  alt={g.label}
                  style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: g.pos }}
                />
                <span
                  style={{
                    position: "absolute",
                    bottom: "0.8rem",
                    left: "0.8rem",
                    background: "rgba(0,0,0,0.65)",
                    color: "#fff",
                    padding: "0.3rem 0.8rem",
                    borderRadius: "999px",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                  }}
                >
                  {g.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
