import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, BackendError, Cart } from "../lib/backend";
import { useAuth } from "./AuthContext";

type CartState = {
  cart: Cart | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  addItem: (menuItemId: string, quantity?: number) => Promise<void>;
  updateLine: (lineId: string, quantity: number) => Promise<void>;
  removeLine: (lineId: string) => Promise<void>;
  clear: () => Promise<void>;
};

const CartContext = createContext<CartState | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    if (!user) {
      setCart(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setCart(await api.get<Cart>("/api/v1/cart/"));
    } catch (e: any) {
      setError(e?.message ?? "Failed to load cart");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  async function addItem(menuItemId: string, quantity = 1) {
    setError(null);
    try {
      setCart(
        await api.post<Cart>("/api/v1/cart/items/", {
          menu_item: menuItemId,
          quantity,
          selected_options: [],
        })
      );
    } catch (e: any) {
      const msg = e?.message ?? "Failed to add item";
      setError(msg);
      throw e instanceof BackendError ? e : new Error(msg);
    }
  }

  async function updateLine(lineId: string, quantity: number) {
    setError(null);
    await api.patch(`/api/v1/cart/items/${lineId}/`, { quantity });
    await refresh();
  }

  async function removeLine(lineId: string) {
    setError(null);
    setCart(await api.del<Cart>(`/api/v1/cart/items/${lineId}/`));
  }

  async function clear() {
    setError(null);
    setCart(await api.del<Cart>("/api/v1/cart/clear/"));
  }

  return (
    <CartContext.Provider
      value={{ cart, loading, error, refresh, addItem, updateLine, removeLine, clear }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartState {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used inside CartProvider");
  return ctx;
}
