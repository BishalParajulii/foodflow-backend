import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { useAuth } from "../src/context/AuthContext";
import { useCart } from "../src/context/CartContext";
import { api, BackendError, Order } from "../src/lib/backend";
import LoadingSpinner from "../src/components/LoadingSpinner";

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "0.7rem 0.9rem",
  borderRadius: "0.6rem",
  border: "1px solid #e0cfb8",
  fontSize: "1rem",
  boxSizing: "border-box",
};

export default function CheckoutPage() {
  const { user, loading: authLoading } = useAuth();
  const { cart, loading: cartLoading, refresh } = useCart();
  const router = useRouter();
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (authLoading || cartLoading) return <LoadingSpinner />;
  if (!user) {
    router.replace("/login?next=/checkout");
    return <LoadingSpinner />;
  }

  const lines = cart?.items ?? [];

  async function placeOrder(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const order = await api.post<Order>("/api/v1/orders/", {
        delivery_address: deliveryAddress,
        phone,
        notes,
      });
      await refresh();
      router.push(`/orders/${order.id}`);
    } catch (err: any) {
      setError(err instanceof BackendError ? err.message : "Checkout failed");
      setBusy(false);
    }
  }

  if (lines.length === 0) {
    return (
      <section className="section-padding">
        <div className="container" style={{ maxWidth: "720px" }}>
          <h1>Checkout</h1>
          <p>
            Your cart is empty. <Link href="/menu">Browse the menu</Link>
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "720px" }}>
        <h1>Checkout</h1>
        <p style={{ color: "#6d5c55" }}>
          {cart?.restaurant_name ? `From ${cart.restaurant_name} · ` : ""}Pay in cash on
          delivery — no online payment needed.
        </p>
        <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "0.5rem" }}>
          {lines.map((l) => (
            <li key={l.id} style={{ display: "flex", justifyContent: "space-between" }}>
              <span>
                {l.quantity} × {l.menu_item_name}
              </span>
              <span>Rs. {Number(l.line_total).toFixed(2)}</span>
            </li>
          ))}
        </ul>
        <p style={{ fontWeight: 800 }}>Total: Rs. {Number(cart?.subtotal ?? 0).toFixed(2)}</p>

        <form onSubmit={placeOrder} style={{ display: "grid", gap: "0.9rem", marginTop: "1rem" }}>
          <input
            style={inputStyle}
            placeholder="Delivery address"
            value={deliveryAddress}
            onChange={(e) => setDeliveryAddress(e.target.value)}
          />
          <input
            style={inputStyle}
            placeholder="Phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
          <textarea
            style={{ ...inputStyle, minHeight: "80px", resize: "vertical" }}
            placeholder="Notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
          {error && <p style={{ color: "var(--color-primary)", margin: 0 }}>{error}</p>}
          <button type="submit" disabled={busy}>
            {busy ? "Placing order…" : "Place order (Cash on Delivery)"}
          </button>
        </form>
      </div>
    </section>
  );
}
