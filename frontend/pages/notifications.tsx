import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import LoadingSpinner from "../src/components/LoadingSpinner";
import { useAuth } from "../src/context/AuthContext";
import { api, Notification } from "../src/lib/backend";

export default function NotificationsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [items, setItems] = useState<Notification[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      setItems(await api.get<Notification[]>("/api/v1/notifications/"));
    } catch (e: any) {
      setError(e?.message ?? "Failed to load notifications");
    }
  }

  useEffect(() => {
    if (authLoading || !user) return;
    load();
  }, [authLoading, user]);

  if (authLoading) return <LoadingSpinner />;
  if (!user) {
    router.replace("/login?next=/notifications");
    return <LoadingSpinner />;
  }
  if (error) return <p style={{ padding: "2rem" }}>{error}</p>;
  if (!items) return <LoadingSpinner />;

  async function markRead(n: Notification) {
    if (n.is_read) return;
    await api.patch(`/api/v1/notifications/${n.id}/`, { is_read: true });
    await load();
  }

  async function markAllRead() {
    setBusy(true);
    try {
      await api.post("/api/v1/notifications/mark-all-read/", {});
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function dismiss(id: string) {
    await api.del(`/api/v1/notifications/${id}/`);
    await load();
  }

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "720px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1>Notifications</h1>
          {items.some((n) => !n.is_read) && (
            <button onClick={markAllRead} disabled={busy}>
              {busy ? "…" : "Mark all read"}
            </button>
          )}
        </div>
        {items.length === 0 ? (
          <p style={{ color: "#6d5c55" }}>
            Nothing here yet — place an order and updates will show up here.
          </p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "0.8rem" }}>
            {items.map((n) => (
              <li
                key={n.id}
                onClick={() => markRead(n)}
                style={{
                  border: "1px solid #f0e2c8",
                  borderLeft: n.is_read ? "1px solid #f0e2c8" : "4px solid var(--color-primary)",
                  borderRadius: "0.8rem",
                  padding: "0.9rem 1rem",
                  background: n.is_read ? "#fff" : "#FFF8E1",
                  cursor: n.is_read ? "default" : "pointer",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
                  <strong>{n.title}</strong>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      dismiss(n.id);
                    }}
                    aria-label="Dismiss"
                    style={{ background: "transparent", border: "none", color: "#6d5c55", cursor: "pointer" }}
                  >
                    ✕
                  </button>
                </div>
                {n.body && <p style={{ margin: "0.4rem 0", color: "#6d5c55" }}>{n.body}</p>}
                <div style={{ fontSize: "0.85rem", color: "#6d5c55" }}>
                  {new Date(n.created_at).toLocaleString()}
                  {n.order && (
                    <span onClick={(e) => e.stopPropagation()}>
                      {" · "}
                      <Link href={`/orders/${n.order}`}>View order</Link>
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
