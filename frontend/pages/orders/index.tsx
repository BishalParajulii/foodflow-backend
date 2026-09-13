import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import LoadingSpinner from "../../src/components/LoadingSpinner";
import { useAuth } from "../../src/context/AuthContext";
import { api, Order } from "../../src/lib/backend";

export function statusLabel(status: string): string {
  return status
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export default function OrdersPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading || !user) return;
    api
      .get<Order[]>("/api/v1/orders/")
      .then(setOrders)
      .catch((e: any) => setError(e?.message ?? "Failed to load orders"));
  }, [authLoading, user]);

  if (authLoading) return <LoadingSpinner />;
  if (!user) {
    router.replace("/login?next=/orders");
    return <LoadingSpinner />;
  }
  if (error) return <p style={{ padding: "2rem" }}>{error}</p>;
  if (!orders) return <LoadingSpinner />;

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "720px" }}>
        <h1>Your orders</h1>
        {orders.length === 0 ? (
          <p>
            No orders yet. <Link href="/menu">Order something</Link>
          </p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "0.8rem" }}>
            {orders.map((o) => (
              <li
                key={o.id}
                style={{
                  border: "1px solid #f0e2c8",
                  borderRadius: "0.8rem",
                  padding: "0.9rem 1rem",
                  background: "#fff",
                }}
              >
                <Link href={`/orders/${o.id}`} style={{ fontWeight: 700 }}>
                  {o.restaurant_name || "Order"} · Rs. {Number(o.total).toFixed(2)}
                </Link>
                <div style={{ color: "#6d5c55", fontSize: "0.9rem" }}>
                  {statusLabel(o.status)} · {o.item_count} items ·{" "}
                  {new Date(o.created_at).toLocaleString()}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
