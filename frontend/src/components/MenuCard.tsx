type MenuItem = {
  id: number | string;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
};

const FALLBACK_IMG = "/images/food.jpeg";

export default function MenuCard({
  item,
  onAdd,
  adding,
}: {
  item: MenuItem;
  onAdd?: () => void;
  adding?: boolean;
}) {
  return (
    <div
      style={{
        border: "1px solid #f0e2c8",
        borderRadius: "1rem",
        overflow: "hidden",
        background: "#fff",
        boxShadow: "0 4px 16px rgba(62,39,35,0.08)",
        transition: "transform 0.2s, box-shadow 0.2s",
        display: "flex",
        flexDirection: "column",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = "0 12px 28px rgba(196,30,58,0.15)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "0 4px 16px rgba(62,39,35,0.08)";
      }}
    >
      <div style={{ position: "relative" }}>
        <img
          src={FALLBACK_IMG}
          alt={item.name}
          style={{ width: "100%", height: "190px", objectFit: "cover", display: "block" }}
          // All dishes use food.jpeg for now — fallback if specific image missing
          onError={(e) => {
            (e.target as HTMLImageElement).src = FALLBACK_IMG;
          }}
        />
        <span
          style={{
            position: "absolute",
            top: "0.8rem",
            left: "0.8rem",
            background: "rgba(62,39,35,0.85)",
            backdropFilter: "blur(4px)",
            color: "#FFF8E1",
            fontSize: "0.75rem",
            fontWeight: 700,
            letterSpacing: "0.4px",
            textTransform: "uppercase",
            padding: "0.3rem 0.7rem",
            borderRadius: "999px",
          }}
        >
          {item.category}
        </span>
      </div>
      <div style={{ padding: "1.1rem 1.2rem 1.3rem", flex: 1, display: "flex", flexDirection: "column" }}>
        <h3 style={{ margin: "0 0 0.4rem", color: "var(--color-dark)", fontSize: "1.1rem" }}>
          {item.name}
        </h3>
        <p style={{ margin: "0 0 1rem", color: "#6d5c55", fontSize: "0.9rem", flex: 1 }}>
          {item.description}
        </p>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <p style={{ margin: 0, fontWeight: 800, color: "var(--color-primary)", fontSize: "1.05rem" }}>
            Rs. {item.price.toFixed(2)}
          </p>
          <button
            onClick={onAdd}
            disabled={!onAdd || adding}
            title={!onAdd ? "Log in to order" : "Add to cart"}
            style={{
              padding: "0.5rem 1rem",
              fontSize: "0.85rem",
              borderRadius: "999px",
              opacity: !onAdd ? 0.55 : 1,
              cursor: !onAdd ? "not-allowed" : "pointer",
            }}
          >
            {adding ? "Adding…" : "+ Add"}
          </button>
        </div>
      </div>
    </div>
  );
}
