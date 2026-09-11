export default function About() {
  return (
    <>
      <div
        style={{
          backgroundImage:
            "linear-gradient(rgba(30,10,5,0.65), rgba(30,10,5,0.5)), url('/images/food.jpeg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          color: "#fff",
          padding: "4.5rem 1.5rem",
          textAlign: "center",
        }}
      >
        <h1 style={{ color: "#fff", margin: "0 0 0.6rem", fontSize: "2.6rem" }}>About FoodFlow</h1>
        <p style={{ margin: 0, color: "#FFEED6" }}>Rooted in Kathmandu, inspired by tradition.</p>
      </div>

      <section className="section-padding">
        <div
          className="container"
          style={{
            display: "grid",
            gap: "3rem",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            alignItems: "center",
          }}
        >
          <img
            src="/images/food.jpeg"
            alt="Our signature yomari"
            style={{
              width: "100%",
              height: "380px",
              objectFit: "cover",
              borderRadius: "1.2rem",
              boxShadow: "0 16px 40px rgba(62,39,35,0.18)",
            }}
          />
          <div>
            <h2 style={{ marginTop: 0 }}>From a Humble Kathmandu Kitchen</h2>
            <p style={{ lineHeight: 1.7, color: "#5a4a44" }}>
              FoodFlow began as a humble kitchen in Kathmandu, dreamed up by a family passionate aboutsharing
              the rich culinary heritage of Nepal and the vibrant spices of India. Today we serve dozens of
              dishes that honor tradition while embracing fresh, locally‑sourced ingredients.
            </p>
            <p style={{ lineHeight: 1.7, color: "#5a4a44" }}>
              Our yomari — pictured everywhere — is still hand-shaped every morning, just like at home.
            </p>
          </div>
        </div>
      </section>

      <section style={{ background: "#fff", padding: "0 0 4rem" }}>
        <div className="container">
          <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap", justifyContent: "center" }}>
            {[
              ["📍 Our Roots", "Started in 2018, we source recipes from home cooks across the Himalayas and the Gangetic plains."],
              ["🌱 Sustainable", "We work with local farmers to reduce food miles and support community agriculture."],
              ["💬 Feedback Welcome", "Love a dish? Have a suggestion? Drop us a note – we’re always listening."],
            ].map(([title, text]) => (
              <div
                key={title}
                style={{
                  flex: "1 1 280px",
                  textAlign: "center",
                  background: "var(--color-cream)",
                  border: "1px solid #f0e2c8",
                  borderRadius: "1rem",
                  padding: "2rem 1.5rem",
                }}
              >
                <h3>{title}</h3>
                <p style={{ color: "#6d5c55" }}>{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
