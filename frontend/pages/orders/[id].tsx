import { useRouter } from "next/router";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import LoadingSpinner from "../../src/components/LoadingSpinner";
import ErrorMessage from "../../src/components/ErrorMessage";
import { useAuth } from "../../src/context/AuthContext";
import { api, BackendError, ORDER_FLOW, Order } from "../../src/lib/backend";
import { statusLabel } from "./index";

export default function OrderDetailPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const { id } = router.query;
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (typeof id !== "string") return;
    setError(null);
    try {
      setOrder(await api.get<Order>(`/api/v1/orders/${id}/`));
    } catch (e: any) {
      setError(e?.message ?? "Failed to load order");
    }
  }, [id]);

  useEffect(() => {
    if (authLoading || !user || typeof id !== "string") return;
    load();
  }, [authLoading, user, id, load]);

  if (authLoading) return <LoadingSpinner />;
  if (!user) {
    router.replace(`/login?next=/orders/${id}`);
    return <LoadingSpinner />;
  }
  if (error) return <ErrorMessage message={error} />;
  if (!order) return <LoadingSpinner />;

  const stepIndex = ORDER_FLOW.indexOf(order.status);
  const cancellable = order.status === "pending" || order.status === "confirmed";

  async function cancelOrder() {
    setActionError(null);
    setBusy(true);
    try {
      setOrder(await api.post<Order>(`/api/v1/orders/${order!.id}/cancel/`));
    } catch (e: any) {
      setActionError(e instanceof BackendError ? e.message : "Cancel failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "720px" }}>
        <p>
          <Link href="/orders">← All orders</Link>
        </p>
        <h1>{order.restaurant_name || "Order"}</h1>
        <p style={{ color: "#6d5c55" }}>
          {statusLabel(order.status)} · placed {new Date(order.created_at).toLocaleString()}
        </p>

        {/* Tracking timeline */}
        {order.status !== "cancelled" ? (
          <ol
            style={{
              listStyle: "none",
              padding: 0,
              display: "flex",
              gap: "0.4rem",
              flexWrap: "wrap",
              margin: "1rem 0",
            }}
          >
            {ORDER_FLOW.map((s, i) => (
              <li
                key={s}
                style={{
                  padding: "0.35rem 0.7rem",
                  borderRadius: "999px",
                  fontSize: "0.8rem",
                  fontWeight: 700,
                  background: i <= stepIndex ? "var(--color-primary)" : "#f3e8d5",
                  color: i <= stepIndex ? "#fff" : "#6d5c55",
                }}
              >
                {statusLabel(s)}
              </li>
            ))}
          </ol>
        ) : (
          <p style={{ color: "var(--color-primary)", fontWeight: 700 }}>This order was cancelled.</p>
        )}

        <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "0.5rem" }}>
          {order.items.map((it) => (
            <li key={it.id} style={{ display: "flex", justifyContent: "space-between" }}>
              <span>
                {it.quantity} × {it.menu_item_name}
              </span>
              <span>Rs. {Number(it.line_total).toFixed(2)}</span>
            </li>
          ))}
        </ul>
        <p>
          Subtotal: Rs. {Number(order.subtotal).toFixed(2)}
          {Number(order.delivery_fee) > 0 &&
            ` · Delivery: Rs. ${Number(order.delivery_fee).toFixed(2)}`}
        </p>
        <p style={{ fontWeight: 800 }}>Total (Cash on Delivery): Rs. {Number(order.total).toFixed(2)}</p>
        {order.delivery_address && <p>Deliver to: {order.delivery_address}</p>}

        {order.status === "delivered" && (
          <p style={{ marginTop: "1rem" }}>
            Enjoyed your meal?{" "}
            <Link href={`/restaurants/${order.restaurant}`}>★ Leave a review</Link>
          </p>
        )}
        {actionError && <p style={{ color: "var(--color-primary)" }}>{actionError}</p>}
        <div style={{ display: "flex", gap: "0.8rem", marginTop: "1rem" }}>
          <button onClick={load} disabled={busy} style={{ background: "transparent", color: "#6d5c55", border: "1px solid #e0cfb8" }}>
            Refresh status
          </button>
          {cancellable && (
            <button onClick={cancelOrder} disabled={busy}>
              {busy ? "Cancelling…" : "Cancel order"}
            </button>
          )}
        </div>
      </div>
    </section>
  );
}
