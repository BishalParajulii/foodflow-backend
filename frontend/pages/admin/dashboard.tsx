import { useEffect, useState } from "react";
import { GetServerSideProps, NextPage } from "next";
import { useRouter } from "next/router";
import { readJSON } from "@/src/lib/file";

// Helper to check admin cookie from req (used in getServerSideProps)
function isAdminReq(req: any): boolean {
  const cookie = req.headers.cookie;
  if (!cookie) return false;
  const match = cookie.match(/adminToken=([^;]+)/);
  return match && match[1] === "secret";
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { req } = context;
  if (!isAdminReq(req)) {
    return {
      redirect: {
        destination: "/admin/login",
        permanent: false,
      },
    };
  }
  // Fetch initial data for messages and menu.
  // NOTE: read JSON files directly server-side instead of HTTP self-fetch.
  // The old code did fetch(`${process.env.NEXT_PUBLIC_BASE_URL || ""}/api/...`)
  // but NEXT_PUBLIC_BASE_URL is never defined, so Node got a relative URL
  // (throws "Failed to parse URL") and the dashboard always started empty.
  // Reading the files also avoids an extra hop and works in Docker.
  let messages: any[] = [];
  let menu: any[] = [];
  try {
    messages = await readJSON<any[]>("src/data/messages.json");
  } catch (e) {
    messages = [];
  }
  try {
    menu = await readJSON<any[]>("src/data/menu.json");
  } catch (e) {
    menu = [];
  }
  return {
    props: {
      initialMessages: messages,
      initialMenu: menu,
    },
  };
};

type Message = {
  id: string;
  name: string;
  email: string;
  message: string;
  timestamp: string;
};

type MenuItem = {
  id: number | string;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
};

type Props = {
  initialMessages: Message[];
  initialMenu: MenuItem[];
};

const AdminDashboard: NextPage<Props> = ({ initialMessages, initialMenu }) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [menuItems, setMenuItems] = useState<MenuItem[]>(initialMenu);
  const [activeTab, setActiveTab] = useState<"messages" | "menu">("messages");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Message handling
  const deleteMessage = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/contact`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to delete");
      // Optimistically remove
      setMessages(messages.filter(m => m.id !== id));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Menu handling
  const addMenuItem = async (item: Omit<MenuItem, "id">) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/menu", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to add menu item");
      const newItem = await res.json();
      setMenuItems([...menuItems, newItem]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateMenuItem = async (item: MenuItem) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/menu`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to update menu item");
      const updated = await res.json();
      setMenuItems(prev => prev.map(i => (i.id === item.id ? updated : i)));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteMenuItem = async (id: number | string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/menu", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to delete menu item");
      setMenuItems(menuItems.filter(i => i.id !== id));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Local state for editing menu item
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [newItem, setNewItem] = useState<Omit<MenuItem, "id">>({
    name: "",
    description: "",
    price: 0,
    image: "",
    category: "",
  });

  useEffect(() => {
    if (editingItem) {
      setNewItem({
        name: editingItem.name,
        description: editingItem.description,
        price: editingItem.price,
        image: editingItem.image,
        category: editingItem.category,
      });
    }
  }, [editingItem]);

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewItem(prev => ({ ...prev, name: e.target.value }));
  };
  const handleDescChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNewItem(prev => ({ ...prev, description: e.target.value }));
  };
  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewItem(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }));
  };
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewItem(prev => ({ ...prev, image: e.target.value }));
  };
  const handleCategoryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewItem(prev => ({ ...prev, category: e.target.value }));
  };

  const handleSaveMenu = async () => {
    if (editingItem) {
      await updateMenuItem({ ...newItem, id: editingItem.id });
      setEditingItem(null);
      // reset newItem
      setNewItem({ name: "", description: "", price: 0, image: "", category: "" });
    } else {
      await addMenuItem(newItem);
      // reset after add
      setNewItem({ name: "", description: "", price: 0, image: "", category: "" });
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#f8f5f0" }}>
      <nav style={{ background: "var(--color-dark)", color: "var(--color-cream)", padding: "1rem 0" }}>
        <div className="container" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: "1.5rem" }}>FoodFlow Admin</h1>
          </div>
          <div>
            <button
              onClick={() => {
                // Call logout API
                fetch("/api/admin/logout", { method: "POST", credentials: "include" }).then(() => {
                  router.push("/admin/login");
                });
              }}
              className="btn"
              style={{ background: "transparent", color: "var(--color-cream)", border: "1px solid var(--color-cream)" }}
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main style={{ padding: "2rem 0" }}>
        <div className="container">
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}>
            <button
              onClick={() => setActiveTab("messages")}
              className="btn"
              style={{ background: activeTab === "messages" ? "var(--color-primary)" : "transparent", color: activeTab === "messages" ? "#fff" : "var(--color-dark)", border: activeTab === "messages" ? "none" : "1px solid var(--color-dark)" }}
            >
              Messages
            </button>
            <button
              onClick={() => setActiveTab("menu")}
              className="btn"
              style={{ background: activeTab === "menu" ? "var(--color-primary)" : "transparent", color: activeTab === "menu" ? "#fff" : "var(--color-dark)", border: activeTab === "menu" ? "none" : "1px solid var(--color-dark)" }}
            >
              Menu Management
            </button>
          </div>

          {activeTab === "messages" ? (
            <section>
              <h2 style={{ color: "var(--color-dark)", marginBottom: "1rem" }}>User Messages</h2>
              {error && <p style={{ color: "#c00" }}>{error}</p>}
              {loading && <p>Loading…</p>}
              {messages.length === 0 ? (
                <p>No messages yet.</p>
              ) : (
                <div style={{ display: "grid", gap: "1rem" }}>
                  {messages.map(msg => (
                    <div key={msg.id} style={{ background: "#fff", borderRadius: "0.5rem", padding: "1rem", boxShadow: "0 2px 4px rgba(0,0,0,0.05)" }}>
                      <p>
                        <strong>{msg.name}</strong> ({msg.email}) <br />
                        <span style={{ color: "#666" }}>{new Date(msg.timestamp).toLocaleString()}</span>
                      </p>
                      <p style={{ margin: "0.5rem 0", color: "#333" }}>{msg.message}</p>
                      <button
                        onClick={() => deleteMessage(msg.id)}
                        className="btn"
                        style={{ background: "#c00", color: "#fff", fontSize: "0.85rem", padding: "0.5rem 1rem" }}
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>
          ) : (
            <section>
              <h2 style={{ color: "var(--color-dark)", marginBottom: "1rem" }}>Menu Management</h2>
              {error && <p style={{ color: "#c00" }}>{error}</p>}
              {/* Add / Edit Form */}
              <div style={{ background: "#fff", padding: "1.5rem", borderRadius: "0.5rem", boxShadow: "0 2px 4px rgba(0,0,0,0.05)", marginBottom: "2rem" }}>
                {editingItem ? (
                  <h3 style={{ marginTop: 0 }}>Edit Menu Item</h3>
                ) : (
                  <h3 style={{ marginTop: 0 }}>Add New Menu Item</h3>
                )}
                <form onSubmit={e => {
                  e.preventDefault();
                  handleSaveMenu();
                }} style={{ display: "grid", gap: "1rem" }}>
                  <label>
                    Name
                    <input
                      type="text"
                      value={newItem.name}
                      onChange={handleNameChange}
                      required
                      style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: "0.3rem" }}
                    />
                  </label>
                  <label>
                    Description
                    <textarea
                      value={newItem.description}
                      onChange={handleDescChange}
                      required
                      style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: "0.3rem" }}
                      rows={3}
                    />
                  </label>
                  <label>
                    Price (₹)
                    <input
                      type="number"
                      value={newItem.price}
                      onChange={handlePriceChange}
                      required
                      style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: "0.3rem" }}
                    />
                  </label>
                  <label>
                    Image URL (relative to /public)
                    <input
                      type="text"
                      value={newItem.image}
                      onChange={handleImageChange}
                      required
                      style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: "0.3rem" }}
                    />
                  </label>
                  <label>
                    Category
                    <input
                      type="text"
                      value={newItem.category}
                      onChange={handleCategoryChange}
                      required
                      style={{ width: "100%", padding: "0.5rem", border: "1px solid #ccc", borderRadius: "0.3rem" }}
                    />
                  </label>
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <button type="submit" className="btn">
                      {editingItem ? "Update" : "Add"}
                    </button>
                    {editingItem && (
                      <button
                        type="button"
                        onClick={() => {
                          setEditingItem(null);
                          setNewItem({ name: "", description: "", price: 0, image: "", category: "" });
                        }}
                        className="btn"
                        style={{ background: "#666", color: "#fff" }}
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </form>
              </div>

              {/* Menu List */}
              <div>
                <h3>Current Menu Items</h3>
                {menuItems.length === 0 ? (
                  <p>No menu items.</p>
                ) : (
                  <div style={{ display: "grid", gap: "1rem" }}>
                    {menuItems.map(item => (
                      <div key={item.id} style={{ background: "#fff", borderRadius: "0.5rem", padding: "1rem", boxShadow: "0 2px 4px rgba(0,0,0,0.05)" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.5rem" }}>
                          <h4 style={{ margin: 0, color: "var(--color-dark)" }}>{item.name}</h4>
                          <span style={{ color: "var(--color-primary)", fontWeight: 600 }}>₹ {item.price}</span>
                        </div>
                        <p style={{ color: "#555", margin: "0 0 0.5rem", fontSize: "0.9rem" }}>{item.description}</p>
                        <p style={{ color: "#666", fontSize: "0.85rem" }}>Category: {item.category}</p>
                        <div style={{ display: "flex", gap: "0.5rem" }}>
                          <button
                            onClick={() => setEditingItem(item)}
                            className="btn"
                            style={{ background: "var(--color-secondary)", color: "#fff", fontSize: "0.85rem", padding: "0.5rem 1rem" }}
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteMenuItem(item.id)}
                            className="btn"
                            style={{ background: "#c00", color: "#fff", fontSize: "0.85rem", padding: "0.5rem 1rem" }}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      </main>

      <footer style={{ background: "var(--color-dark)", color: "var(--color-cream)", textAlign: "center", padding: "2rem 0", fontSize: "0.9rem" }}>
        © {new Date().getFullYear()} FoodFlow Admin Panel
      </footer>
    </div>
  );
};

export default AdminDashboard;