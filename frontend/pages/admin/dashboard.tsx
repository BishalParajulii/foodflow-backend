import { useEffect, useMemo, useState } from "react";
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

const DEFAULT_CATEGORIES = ["Starters", "Main Course", "Dessert", "Beverage"];
const DEFAULT_IMAGE = "food.jpeg";

type FormState = {
  name: string;
  description: string;
  price: string;
  category: string;
  image: string;
};

const EMPTY_FORM: FormState = {
  name: "",
  description: "",
  price: "",
  category: "",
  image: "",
};

function toForm(item?: MenuItem | null): FormState {
  if (!item) return EMPTY_FORM;
  return {
    name: item.name ?? "",
    description: item.description ?? "",
    price: String(item.price ?? ""),
    category: item.category ?? "",
    image: item.image ?? "",
  };
}

const AdminDashboard: NextPage<Props> = ({ initialMessages, initialMenu }) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [menuItems, setMenuItems] = useState<MenuItem[]>(initialMenu);
  const [activeTab, setActiveTab] = useState<"messages" | "menu">("menu");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // --- menu UI state ---
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState<Partial<FormState>>({});
  const [search, setSearch] = useState("");
  const [filterCategory, setFilterCategory] = useState("All");
  const [deletingId, setDeletingId] = useState<number | string | null>(null);

  const categories = useMemo(() => {
    const fromItems = menuItems.map((i) => i.category).filter(Boolean);
    return Array.from(new Set([...DEFAULT_CATEGORIES, ...fromItems]));
  }, [menuItems]);

  const filteredItems = useMemo(() => {
    const q = search.trim().toLowerCase();
    return menuItems.filter((item) => {
      const matchCat = filterCategory === "All" || item.category === filterCategory;
      const matchQ =
        !q ||
        item.name.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q);
      return matchCat && matchQ;
    });
  }, [menuItems, search, filterCategory]);

  // Close modal on Escape
  useEffect(() => {
    if (!modalOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closeModal();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [modalOpen]);

  // --- messages ---
  const deleteMessage = async (id: string) => {
    if (!confirm("Delete this message?")) return;
    setError(null);
    try {
      const res = await fetch(`/api/contact`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to delete message");
      setMessages((prev) => prev.filter((m) => m.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  // --- menu CRUD ---
  const openAdd = () => {
    setEditingItem(null);
    setForm(EMPTY_FORM);
    setFormErrors({});
    setError(null);
    setModalOpen(true);
  };

  const openEdit = (item: MenuItem) => {
    setEditingItem(item);
    setForm(toForm(item));
    setFormErrors({});
    setError(null);
    setModalOpen(true);
  };

  const closeModal = () => {
    if (saving) return;
    setModalOpen(false);
    setEditingItem(null);
    setForm(EMPTY_FORM);
    setFormErrors({});
  };

  const update = (key: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    // clear field error as user types
    if (formErrors[key]) {
      setFormErrors((prev) => ({ ...prev, [key]: undefined }));
    }
  };

  const validate = (): boolean => {
    const errs: Partial<FormState> = {};
    if (form.name.trim().length < 2) errs.name = "Enter a name (min 2 characters).";
    const priceNum = Number(form.price);
    if (!form.price.trim()) errs.price = "Enter a price.";
    else if (Number.isNaN(priceNum) || priceNum <= 0)
      errs.price = "Price must be a number greater than 0.";
    if (!form.category.trim()) errs.category = "Pick a category.";
    if (form.description.trim().length < 5)
      errs.description = "Add a short description (min 5 characters).";
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSave = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!validate()) return;
    setSaving(true);
    setError(null);
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      price: Number(form.price),
      category: form.category.trim(),
      image: form.image.trim() || DEFAULT_IMAGE,
    };
    try {
      if (editingItem) {
        const res = await fetch(`/api/menu`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...payload, id: editingItem.id }),
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to update item");
        const updated: MenuItem = await res.json();
        setMenuItems((prev) => prev.map((i) => (i.id === editingItem.id ? updated : i)));
      } else {
        const res = await fetch("/api/menu", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to add item");
        const created: MenuItem = await res.json();
        setMenuItems((prev) => [...prev, created]);
      }
      closeModal();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number | string) => {
    if (!confirm("Delete this item from the menu?")) return;
    setDeletingId(id);
    setError(null);
    try {
      const res = await fetch("/api/menu", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to delete item");
      setMenuItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = async () => {
    await fetch("/api/admin/logout", { method: "POST", credentials: "include" });
    router.push("/admin/login");
  };

  const pricePreview = Number(form.price);
  const showPricePreview = form.price.trim() !== "" && !Number.isNaN(pricePreview);

  return (
    <div className="admin-page">
      <nav className="admin-nav">
        <div className="container admin-nav-inner">
          <h1 className="admin-brand">FoodFlow Admin</h1>
          <button onClick={handleLogout} className="btn-ghost">
            Logout
          </button>
        </div>
      </nav>

      <main className="container admin-main">
        <div className="tabs">
          <button
            onClick={() => setActiveTab("menu")}
            className={`tab ${activeTab === "menu" ? "active" : ""}`}
          >
            Menu · {menuItems.length}
          </button>
          <button
            onClick={() => setActiveTab("messages")}
            className={`tab ${activeTab === "messages" ? "active" : ""}`}
          >
            Messages · {messages.length}
          </button>
        </div>

        {error && <p className="error-banner">{error}</p>}

        {activeTab === "menu" ? (
          <section>
            <div className="menu-header">
              <div>
                <h2>Menu items</h2>
                <p className="muted">
                  {filteredItems.length} of {menuItems.length} showing
                </p>
              </div>
              <button onClick={openAdd} className="btn">
                + Add item
              </button>
            </div>

            <div className="toolbar">
              <input
                type="search"
                placeholder="Search name or description…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input"
                aria-label="Search menu items"
              />
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="input select"
                aria-label="Filter by category"
              >
                <option value="All">All categories</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            {filteredItems.length === 0 ? (
              <div className="empty">
                <p className="empty-title">
                  {menuItems.length === 0 ? "No items yet" : "No matches"}
                </p>
                <p className="muted">
                  {menuItems.length === 0
                    ? "Add your first dish to get started."
                    : "Try a different search or category."}
                </p>
                {menuItems.length === 0 && (
                  <button onClick={openAdd} className="btn" style={{ marginTop: "0.75rem" }}>
                    + Add item
                  </button>
                )}
              </div>
            ) : (
              <div className="cards">
                {filteredItems.map((item) => (
                  <article key={item.id} className="card">
                    <div className="card-top">
                      <span className="pill">{item.category}</span>
                      <span className="price">Rs. {Number(item.price).toFixed(2)}</span>
                    </div>
                    <h3 className="card-name">{item.name}</h3>
                    <p className="card-desc">{item.description}</p>
                    <div className="card-actions">
                      <button onClick={() => openEdit(item)} className="btn-small secondary">
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="btn-small danger"
                        disabled={deletingId === item.id}
                      >
                        {deletingId === item.id ? "Deleting…" : "Delete"}
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        ) : (
          <section>
            <div className="menu-header">
              <div>
                <h2>Messages</h2>
                <p className="muted">{messages.length} total</p>
              </div>
            </div>
            {messages.length === 0 ? (
              <div className="empty">
                <p className="empty-title">No messages yet</p>
              </div>
            ) : (
              <div className="msg-list">
                {messages.map((msg) => (
                  <div key={msg.id} className="card">
                    <p className="msg-meta">
                      <strong>{msg.name}</strong> · {msg.email}
                      <br />
                      <span className="muted">{new Date(msg.timestamp).toLocaleString()}</span>
                    </p>
                    <p className="card-desc">{msg.message}</p>
                    <div className="card-actions">
                      <button onClick={() => deleteMessage(msg.id)} className="btn-small danger">
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>

      {modalOpen && (
        <div className="overlay" onClick={closeModal} role="dialog" aria-modal="true">
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <h3>{editingItem ? "Edit item" : "Add new item"}</h3>
              <button onClick={closeModal} className="icon-btn" aria-label="Close">
                ✕
              </button>
            </div>

            <form onSubmit={handleSave} noValidate>
              <div className="field">
                <label htmlFor="f-name">Name *</label>
                <input
                  id="f-name"
                  className={`input ${formErrors.name ? "invalid" : ""}`}
                  type="text"
                  placeholder="e.g. Chicken Biryani"
                  value={form.name}
                  onChange={(e) => update("name", e.target.value)}
                  autoFocus
                />
                {formErrors.name && <span className="field-error">{formErrors.name}</span>}
              </div>

              <div className="field-row">
                <div className="field">
                  <label htmlFor="f-price">Price (Rs.) *</label>
                  <input
                    id="f-price"
                    className={`input ${formErrors.price ? "invalid" : ""}`}
                    type="number"
                    min="1"
                    step="1"
                    placeholder="e.g. 350"
                    value={form.price}
                    onChange={(e) => update("price", e.target.value)}
                  />
                  {formErrors.price && <span className="field-error">{formErrors.price}</span>}
                </div>
                <div className="field">
                  <label htmlFor="f-category">Category *</label>
                  <select
                    id="f-category"
                    className={`input select ${formErrors.category ? "invalid" : ""}`}
                    value={categories.includes(form.category) ? form.category : ""}
                    onChange={(e) => update("category", e.target.value)}
                  >
                    <option value="" disabled>
                      Select…
                    </option>
                    {categories.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                  {formErrors.category && (
                    <span className="field-error">{formErrors.category}</span>
                  )}
                </div>
              </div>

              <div className="field">
                <label htmlFor="f-category-custom">
                  Or new category <span className="muted-inline">(optional)</span>
                </label>
                <input
                  id="f-category-custom"
                  className="input"
                  type="text"
                  placeholder="Type to create a new one…"
                  value={categories.includes(form.category) ? "" : form.category}
                  onChange={(e) => update("category", e.target.value)}
                />
              </div>

              <div className="field">
                <label htmlFor="f-desc">Description *</label>
                <textarea
                  id="f-desc"
                  className={`input ${formErrors.description ? "invalid" : ""}`}
                  placeholder="Short tasty description…"
                  rows={3}
                  value={form.description}
                  onChange={(e) => update("description", e.target.value)}
                />
                {formErrors.description && (
                  <span className="field-error">{formErrors.description}</span>
                )}
              </div>

              <details className="advanced">
                <summary>Image (optional)</summary>
                <input
                  className="input"
                  type="text"
                  placeholder={`Defaults to ${DEFAULT_IMAGE}`}
                  value={form.image}
                  onChange={(e) => update("image", e.target.value)}
                />
              </details>

              {(form.name || showPricePreview) && (
                <div className="preview">
                  <span className="pill">{form.category || "Category"}</span>
                  <strong>{form.name || "Dish name"}</strong>
                  <span className="price">
                    {showPricePreview ? `Rs. ${pricePreview.toFixed(2)}` : "Rs. —"}
                  </span>
                </div>
              )}

              <div className="modal-actions">
                <button type="button" onClick={closeModal} className="btn-ghost-dark" disabled={saving}>
                  Cancel
                </button>
                <button type="submit" className="btn" disabled={saving}>
                  {saving ? "Saving…" : editingItem ? "Save changes" : "Add item"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <footer className="admin-footer">
        © {new Date().getFullYear()} FoodFlow Admin
      </footer>

      <style jsx>{`
        .admin-page { min-height: 100vh; background: #f8f5f0; }
        .admin-nav { background: var(--color-dark); color: var(--color-cream); padding: 0.9rem 0; }
        .admin-nav-inner { display: flex; justify-content: space-between; align-items: center; }
        .admin-brand { margin: 0; font-size: 1.25rem; color: var(--color-cream); }
        .admin-main { padding: 1.5rem 1.5rem 3rem; max-width: 1000px; }
        .admin-footer { background: var(--color-dark); color: var(--color-cream); text-align: center; padding: 1.5rem 0; font-size: 0.9rem; }

        .tabs { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; }
        .tab {
          padding: 0.55rem 1.1rem; border-radius: 999px; font-size: 0.9rem; font-weight: 600;
          background: transparent; color: var(--color-dark); border: 1px solid #d8cbb8;
          box-shadow: none; cursor: pointer;
        }
        .tab.active { background: var(--color-dark); color: #fff; border-color: var(--color-dark); }
        .tab:hover { background: #efe6d4; transform: none; color: var(--color-dark); }
        .tab.active:hover { background: var(--color-dark); color: #fff; }

        .error-banner { background: #fdecec; color: #b3261e; border: 1px solid #f5c2c0; padding: 0.7rem 1rem; border-radius: 0.5rem; }

        .menu-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; }
        .menu-header h2 { margin: 0; color: var(--color-dark); }
        .muted { color: #8a7a72; font-size: 0.9rem; margin: 0.25rem 0 0; }
        .muted-inline { color: #8a7a72; font-weight: 400; }

        .toolbar { display: grid; grid-template-columns: 1fr 220px; gap: 0.75rem; margin-bottom: 1.25rem; }
        @media (max-width: 640px) { .toolbar { grid-template-columns: 1fr; } .menu-header { flex-direction: column; } }

        .input {
          width: 100%; padding: 0.65rem 0.8rem; border: 1px solid #d8cbb8; border-radius: 0.5rem;
          font-size: 0.95rem; background: #fff; color: var(--color-dark); box-sizing: border-box;
        }
        .input:focus { outline: 2px solid var(--color-accent); border-color: var(--color-secondary); }
        .input.invalid { border-color: #c00; }
        .select { cursor: pointer; }

        .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
        .msg-list { display: grid; gap: 1rem; }
        .card {
          background: #fff; border: 1px solid #f0e2c8; border-radius: 0.9rem;
          padding: 1rem 1.1rem; box-shadow: 0 2px 8px rgba(62,39,35,0.06);
          display: flex; flex-direction: column; gap: 0.5rem;
        }
        .card-top { display: flex; justify-content: space-between; align-items: center; }
        .pill {
          background: #f5ecdb; color: #6b4f3a; font-size: 0.72rem; font-weight: 700;
          letter-spacing: 0.4px; text-transform: uppercase; padding: 0.25rem 0.65rem; border-radius: 999px;
        }
        .price { color: var(--color-primary); font-weight: 800; }
        .card-name { margin: 0; color: var(--color-dark); font-size: 1.05rem; }
        .card-desc { color: #6d5c55; font-size: 0.9rem; margin: 0; flex: 1;
          display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .card-actions { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
        .msg-meta { margin: 0; font-size: 0.9rem; }

        .btn-small {
          padding: 0.45rem 0.9rem; font-size: 0.85rem; border-radius: 0.5rem; box-shadow: none;
          border: 1px solid transparent; cursor: pointer; font-weight: 600;
        }
        .btn-small.secondary { background: #efe6d4; color: var(--color-dark); }
        .btn-small.secondary:hover { background: #e3d3b8; transform: none; }
        .btn-small.danger { background: transparent; color: #b3261e; border-color: #efb8b5; }
        .btn-small.danger:hover { background: #fdecec; transform: none; color: #b3261e; }

        .btn-ghost {
          background: transparent; color: var(--color-cream); border: 1px solid var(--color-cream);
          box-shadow: none; padding: 0.5rem 1.1rem; font-size: 0.9rem;
        }
        .btn-ghost:hover { background: rgba(255,255,255,0.12); transform: none; }
        .btn-ghost-dark {
          background: transparent; color: var(--color-dark); border: 1px solid #d8cbb8;
          box-shadow: none;
        }
        .btn-ghost-dark:hover { background: #efe6d4; transform: none; color: var(--color-dark); }
        .btn:disabled, .btn-small:disabled { opacity: 0.6; cursor: not-allowed; }

        .empty { background: #fff; border: 1px dashed #d8cbb8; border-radius: 0.9rem; padding: 2.5rem 1.5rem; text-align: center; }
        .empty-title { font-weight: 700; font-size: 1.05rem; margin: 0 0 0.25rem; color: var(--color-dark); }

        .overlay {
          position: fixed; inset: 0; background: rgba(62,39,35,0.55);
          display: flex; align-items: flex-start; justify-content: center;
          padding: 2rem 1rem; z-index: 50; overflow-y: auto;
        }
        .modal {
          background: #fff; border-radius: 1rem; padding: 1.5rem; width: 100%; max-width: 520px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.25);
        }
        .modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .modal-head h3 { margin: 0; color: var(--color-dark); }
        .icon-btn {
          background: transparent; color: #8a7a72; box-shadow: none; padding: 0.4rem 0.6rem; font-size: 1rem;
        }
        .icon-btn:hover { background: #f5ecdb; transform: none; color: var(--color-dark); }

        .field { margin-bottom: 0.9rem; display: flex; flex-direction: column; gap: 0.35rem; }
        .field label { font-size: 0.85rem; font-weight: 600; color: var(--color-dark); }
        .field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
        @media (max-width: 480px) { .field-row { grid-template-columns: 1fr; } }
        .field-error { color: #b3261e; font-size: 0.82rem; }

        .advanced { margin: 0.25rem 0 0.9rem; font-size: 0.9rem; color: #6d5c55; }
        .advanced summary { cursor: pointer; font-weight: 600; margin-bottom: 0.5rem; }

        .preview {
          display: flex; align-items: center; gap: 0.6rem; background: #fff8e1;
          border: 1px solid #f0e2c8; border-radius: 0.6rem; padding: 0.6rem 0.8rem;
          font-size: 0.9rem; margin-bottom: 1rem;
        }
        .preview strong { flex: 1; color: var(--color-dark); font-weight: 700; }

        .modal-actions { display: flex; justify-content: flex-end; gap: 0.6rem; margin-top: 0.5rem; }
      `}</style>
    </div>
  );
};

export default AdminDashboard;
