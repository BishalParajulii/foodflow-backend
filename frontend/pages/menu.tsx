import { useEffect, useState } from "react";
import MenuCard from "../src/components/MenuCard";
import LoadingSpinner from "../src/components/LoadingSpinner";
import ErrorMessage from "../src/components/ErrorMessage";
import { fetcher } from "../src/lib/api";

type MenuItem = {
  id: number;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
};

export default function MenuPage() {
  const [items, setItems] = useState<MenuItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadMenu() {
      try {
        // Internal Next.js route (pages/api/menu.ts, served on :3000).
        // Do NOT prefix with NEXT_PUBLIC_API_URL — that points at Django
        // (:8000) where the route is /api/v1/menu/items/, not /api/menu.
        const data = await fetcher<MenuItem[]>("/api/menu");
        setItems(data);
        // To use Django instead (requires seeded DB):
        //   import { backendFetcher } from "../src/lib/api";
        //   type DjangoItem = { id: string; name: string; description: string;
        //     price: string; image_url: string; category_name: string };
        //   const rows = await backendFetcher<DjangoItem[]>("/api/v1/menu/items/");
        //   setItems(rows.map(r => ({ id: Number(r.id.slice(0,8)) || 0, name: r.name,
        //     description: r.description, price: Number(r.price),
        //     image: r.image_url, category: r.category_name })));
      } catch (err: any) {
        setError(err.message ?? "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    loadMenu();
  }, []);

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
          {Object.keys(grouped).map((category) => (
            <section key={category} style={{ marginBottom: "3rem" }}>
              <h2 style={{ color: "var(--color-primary)", borderBottom: "2px solid var(--color-accent)", display: "inline-block", paddingBottom: "0.3rem" }}>
                {category}
              </h2>
              <div style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", marginTop: "1.2rem" }}>
                {grouped[category].map((item) => (
                  <MenuCard key={item.id} item={item} />
                ))}
              </div>
            </section>
          ))}
        </div>
      </section>
    </>
  );
}
