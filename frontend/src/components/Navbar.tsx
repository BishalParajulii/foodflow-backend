import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { api } from "../lib/backend";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const router = useRouter();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!user) {
      setUnread(0);
      return;
    }
    let alive = true;
    async function poll() {
      try {
        const data = await api.get<{ unread_count: number }>(
          "/api/v1/notifications/unread-count/"
        );
        if (alive) setUnread(data.unread_count);
      } catch {
        // backend down or static demo — hide the badge silently
      }
    }
    poll();
    const timer = setInterval(poll, 30000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [user?.id]);

  async function handleLogout() {
    await logout();
    router.push("/");
  }

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
          {user ? (
            <>
              <Link href="/orders" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>Orders</Link>
              <Link href="/notifications" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>
                Notifications{unread > 0 ? ` (${unread})` : ""}
              </Link>
              <Link href="/cart" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>
                Cart{cart && cart.item_count > 0 ? ` (${cart.item_count})` : ""}
              </Link>
              <span style={{ marginRight: "1.2rem", color: "var(--color-accent)", fontSize: "0.9rem" }}>
                {user.first_name || user.email}
              </span>
              <button
                onClick={handleLogout}
                style={{ background: "transparent", border: "1px solid var(--color-accent)", color: "#fff", padding: "0.4rem 0.9rem", fontSize: "0.85rem" }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" style={{ marginRight: "1.2rem", color: "#fff", fontWeight: 500 }}>Login</Link>
              <Link
                href="/menu"
                className="btn"
                style={{ padding: "0.5rem 1.1rem", fontSize: "0.9rem", borderRadius: "999px" }}
              >
                Order Now
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
