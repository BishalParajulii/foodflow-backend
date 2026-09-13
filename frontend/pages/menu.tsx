import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import MenuCard from "../src/components/MenuCard";
import LoadingSpinner from "../src/components/LoadingSpinner";
import ErrorMessage from "../src/components/ErrorMessage";
import { fetcher } from "../src/lib/api";
import { api, BackendError, MenuItem as DjangoItem } from "../src/lib/backend";
import { useAuth } from "../src/context/AuthContext";
import { useCart } from "../src/context/CartContext";

type MenuItem = {
  id: number | string;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
};

function fromDjango(rows: DjangoItem[]): MenuItem[] {
  return rows
    .filter((r) => r.is_available)
    .map((r) => ({
      id: r.id,
      name: r.name,
      description: r.description,
      price: Number(r.price),
      image: r.image_url || "/images/food.jpeg",
      category: r.category_name || "Menu",
    }));
}

export default function MenuPage() {
  const [items, setItems] = useState<MenuItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [addingId, setAddingId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const { user } = useAuth();
  const { addItem } = useCart();
  const router = useRouter();

  useEffect(() => {
    async function loadMenu() {
      // Prefer the live Django menu (via same-origin proxy); fall back to
      // the static file menu when the backend is unreachable/empty.
      try {
        const rows = await api.get<DjangoItem[]>("/api/v1/menu/items/");
        if (rows.length > 0) {
          setItems(fromDjango(rows));
          setLoading(false);
          return;
        }
      } catch {
        // fall through to static menu
      }
      try {
        const data = await fetcher<MenuItem[]>("/api/menu");
        setItems(data);
      } catch (err: any) {
        setError(err.message ?? "Unknown error");
      } finally {
        setLoading(false);
      }
      setLoading(false);
    }
    loadMenu();
  }, []);

  async function handleAdd(item: MenuItem) {
    if (!user) {
      router.push("/login?next=/menu");
      return;
    }
    if (typeof item.id !== "string" || item.id.includes("-") === false) {
      // Static fallback items have numeric ids — they don't exist in Django.
      setNotice("This demo item isn't in the live menu yet — showing static menu.");
      return;
    }
    setAddingId(String(item.id));
    setNotice(null);
    try {
      await addItem(String(item.id), 1);
      router.push("/cart");
    } catch (err: any) {
      setNotice(err instanceof BackendError ? err.message : "Could not add item");
    } finally {
      setAddingId(null);
    }
  }

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!items || items.length === 0) return <p>No menu items available.</p>;

  // Group by category for nicer layout
  const grouped = items.reduce((acc: Record<string, MenuItem[]>, item) => {
    (acc[item.category] = acc[item.category] || []).push(item);
    return acc;
  }, {} as Record<string, MenuItem[]>);

  return (
    <>
      {/* Banner header */}
      <div
        style={{
          backgroundImage:
            "linear-gradient(rgba(30,10,5,0.68), rgba(30,10,5,0.55)), url('/images/food.jpeg')",
          backgroundSize: "cover",
          backgroundPosition: "center",
          color: "#fff",
          padding: "4.5rem 1.5rem",
          textAlign: "center",
        }}
      >
        <h1 style={{ color: "#fff", margin: "0 0 0.6rem", fontSize: "2.6rem" }}>Our Menu</h1>
        <p style={{ margin: 0, color: "#FFEED6", fontSize: "1.1rem" }}>
          Browse our selection of Nepali & Indian delicacies — all photos feature our fresh yomari.
        </p>
      </div>

      <section className="section-padding" style={{ paddingTop: "2.5rem" }}>
        <div className="container">
          {notice && (
            <p style={{ background: "#FFF8E1", border: "1px solid #e0cfb8", borderRadius: "0.6rem", padding: "0.7rem 1rem" }}>
              {notice}{" "}
              <button onClick={() => setNotice(null)} style={{ background: "transparent", border: "none", color: "var(--color-primary)", cursor: "pointer", fontWeight: 700 }}>
                Dismiss
              </button>
            </p>
          )}
          {Object.keys(grouped).map((category) => (
            <section key={category} style={{ marginBottom: "3rem" }}>
              <h2 style={{ color: "var(--color-primary)", borderBottom: "2px solid var(--color-accent)", display: "inline-block", paddingBottom: "0.3rem" }}>
                {category}
              </h2>
              <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", marginTop: "1.2rem" }}>
                {grouped[category].map((item) => (
                  <MenuCard
                    key={String(item.id)}
                    item={item}
                    onAdd={user ? () => handleAdd(item) : undefined}
                    adding={addingId === String(item.id)}
                  />
                ))}
              </div>
            </section>
          ))}
          {!user && (
            <p style={{ color: "#6d5c55" }}>
              Log in to add items to your cart.
            </p>
          )}
        </div>
      </section>
    </>
  );
}
