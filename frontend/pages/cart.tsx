import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "../src/context/AuthContext";
import { useCart } from "../src/context/CartContext";
import LoadingSpinner from "../src/components/LoadingSpinner";

export default function CartPage() {
  const { user, loading: authLoading } = useAuth();
  const { cart, loading, error, updateLine, removeLine, clear } = useCart();
  const router = useRouter();

  if (authLoading || loading) return <LoadingSpinner />;
  if (!user) {
    router.replace("/login?next=/cart");
    return <LoadingSpinner />;
  }

  const lines = cart?.items ?? [];

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "720px" }}>
        <h1>Your cart</h1>
        {cart?.restaurant_name && (
          <p style={{ color: "#6d5c55" }}>From {cart.restaurant_name}</p>
        )}
        {error && <p style={{ color: "var(--color-primary)" }}>{error}</p>}
        {lines.length === 0 ? (
          <p>
            Your cart is empty. <Link href="/menu">Browse the menu</Link>
          </p>
        ) : (
          <>
            <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "0.8rem" }}>
              {lines.map((line) => (
                <li
                  key={line.id}
                  style={{
                    border: "1px solid #f0e2c8",
                    borderRadius: "0.8rem",
                    padding: "0.9rem 1rem",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: "1rem",
                    background: "#fff",
                  }}
                >
                  <div>
                    <strong>{line.menu_item_name}</strong>
                    <div style={{ color: "#6d5c55", fontSize: "0.9rem" }}>
                      Rs. {Number(line.unit_price).toFixed(2)} each · Rs.{" "}
                      {Number(line.line_total).toFixed(2)}
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <button
                      aria-label="decrease"
                      onClick={() =>
                        line.quantity <= 1
                          ? removeLine(line.id)
                          : updateLine(line.id, line.quantity - 1)
                      }
                      style={{ padding: "0.3rem 0.7rem" }}
                    >
                      −
                    </button>
                    <span>{line.quantity}</span>
                    <button
                      aria-label="increase"
                      onClick={() => updateLine(line.id, line.quantity + 1)}
                      style={{ padding: "0.3rem 0.7rem" }}
                    >
                      +
                    </button>
                    <button
                      onClick={() => removeLine(line.id)}
                      style={{ padding: "0.3rem 0.7rem", background: "transparent", color: "var(--color-primary)", border: "1px solid var(--color-primary)" }}
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.8rem", marginTop: "1.2rem" }}>
              <button
                onClick={() => clear()}
                style={{ background: "transparent", color: "#6d5c55", border: "1px solid #e0cfb8" }}
              >
                Clear cart
              </button>
              <p style={{ fontWeight: 800, fontSize: "1.1rem" }}>
                Subtotal: Rs. {Number(cart?.subtotal ?? 0).toFixed(2)}
              </p>
            </div>
            <div style={{ marginTop: "1rem" }}>
              <Link href="/checkout" className="btn" style={{ display: "inline-block", padding: "0.7rem 1.6rem" }}>
                Proceed to checkout (Cash on Delivery)
              </Link>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
