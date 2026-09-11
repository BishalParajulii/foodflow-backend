export default function Hero() {
  return (
    <section
      style={{
        backgroundImage:
          "linear-gradient(rgba(30,10,5,0.62), rgba(30,10,5,0.45)), url('/images/food.jpeg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        color: "#fff",
        padding: "7rem 1.5rem 6rem",
        position: "relative",
      }}
    >
      <div
        className="container"
        style={{
          display: "grid",
          gap: "3rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          alignItems: "center",
        }}
      >
        {/* Left copy */}
        <div>
          <span
            style={{
              display: "inline-block",
              background: "rgba(255,255,255,0.15)",
              backdropFilter: "blur(6px)",
              border: "1px solid rgba(255,255,255,0.3)",
              padding: "0.4rem 1rem",
              borderRadius: "999px",
              fontSize: "0.85rem",
              letterSpacing: "0.5px",
              marginBottom: "1.2rem",
            }}
          >
            ✨ Authentic Yomari • Momo • Biryani
          </span>
          <h1
            style={{
              fontSize: "clamp(2.4rem, 5vw, 3.8rem)",
              margin: "0 0 1rem",
              color: "#fff",
              lineHeight: 1.05,
              fontWeight: 800,
            }}
          >
            Authentic Nepali &<br /> Indian Flavors
          </h1>
          <p
            style={{
              fontSize: "1.15rem",
              marginBottom: "2rem",
              color: "#FFEED6",
              maxWidth: "520px",
              lineHeight: 1.6,
            }}
          >
            From steaming yomari filled with sweet chaku to hearty momos and
            fragrant biryanis — taste tradition, made fresh daily.
          </p>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
            <a href="/menu" className="btn" style={{ fontSize: "1.05rem" }}>
              Explore Our Menu →
            </a>
            <a
              href="/about"
              style={{
                display: "inline-block",
                padding: "0.75rem 1.5rem",
                borderRadius: "0.5rem",
                border: "2px solid #fff",
                color: "#fff",
                fontWeight: 600,
              }}
            >
              Our Story
            </a>
          </div>
          <div
            style={{
              display: "flex",
              gap: "2rem",
              marginTop: "2.5rem",
              flexWrap: "wrap",
            }}
          >
            {[
              ["4.9★", "2k+ reviews"],
              ["30+", "traditional dishes"],
              ["25 min", "avg. delivery"],
            ].map(([big, small]) => (
              <div key={small}>
                <div style={{ fontSize: "1.4rem", fontWeight: 800 }}>{big}</div>
                <div style={{ fontSize: "0.9rem", opacity: 0.85 }}>{small}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right image card */}
        <div style={{ display: "flex", justifyContent: "center" }}>
          <div
            style={{
              background: "#fff",
              borderRadius: "1.2rem",
              overflow: "hidden",
              maxWidth: "420px",
              width: "100%",
              boxShadow: "0 20px 60px rgba(0,0,0,0.35)",
              transform: "rotate(1.5deg)",
            }}
          >
            <img
              src="/images/food.jpeg"
              alt="Traditional Nepali Yomari served on clay plate"
              style={{ width: "100%", height: "300px", objectFit: "cover", display: "block" }}
            />
            <div style={{ padding: "1.25rem 1.4rem", color: "#3E2723" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "0.4rem",
                }}
              >
                <strong style={{ fontSize: "1.1rem" }}>Special Yomari Set</strong>
                <span
                  style={{
                    background: "#FFF3E0",
                    color: "#C41E3A",
                    fontWeight: 800,
                    padding: "0.25rem 0.7rem",
                    borderRadius: "999px",
                    fontSize: "0.9rem",
                  }}
                >
                  Rs. 180
                </span>
              </div>
              <p style={{ margin: 0, color: "#666", fontSize: "0.95rem" }}>
                Steamed rice-flour dumplings with rich chaku & sesame filling —
                our signature.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
