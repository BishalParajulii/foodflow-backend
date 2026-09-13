// Browser-side client for the Django API via the same-origin proxy
// (pages/api/backend/[...path].ts). Handles JWT + envelope unwrapping.

const TOKEN_KEY = "ff_access";
const REFRESH_KEY = "ff_refresh";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem("ff_user");
}

export class BackendError extends Error {
  status: number;
  code?: string;
  constructor(status: number, message: string, code?: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const headers: Record<string, string> = {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...((init?.headers as Record<string, string>) || {}),
  };
  const token = getAccessToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`/api/backend${normalized}`, { ...init, headers });
  let json: any = null;
  try {
    json = await res.json();
  } catch {
    // non-JSON upstream response
  }
  if (!res.ok) {
    const err = json?.error || {};
    const details = err.details;
    const detailMsg =
      details && typeof details === "object"
        ? Object.entries(details)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
            .join("; ")
        : null;
    throw new BackendError(res.status, detailMsg || err.message || `Request failed: ${res.status}`, err.code);
  }
  // Unwrap { success: true, data } then DRF pagination { results }
  const data = json && typeof json === "object" && "data" in json ? json.data : json;
  if (data && typeof data === "object" && Array.isArray((data as any).results)) {
    return (data as any).results as T;
  }
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body ?? {}) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body ?? {}) }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

// ---- Types matching the Django serializers ----

export type User = {
  id: string;
  email: string;
  phone: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
};

export type MenuItem = {
  id: string;
  category: string;
  category_name: string;
  restaurant_id: string;
  name: string;
  description: string;
  price: string;
  image_url: string;
  is_veg: boolean;
  is_available: boolean;
};

export type CartLine = {
  id: string;
  menu_item: string;
  menu_item_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
  selected_options: string[];
};

export type Cart = {
  id: string;
  restaurant: string | null;
  restaurant_name: string;
  items: CartLine[];
  item_count: number;
  subtotal: string;
};

export type OrderItem = {
  id: string;
  menu_item: string | null;
  menu_item_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
};

export type Order = {
  id: string;
  user: string;
  user_email: string;
  restaurant: string;
  restaurant_name: string;
  status: string;
  items: OrderItem[];
  item_count: number;
  subtotal: string;
  delivery_fee: string;
  total: string;
  delivery_address: string;
  phone: string;
  notes: string;
  created_at: string;
};

export const ORDER_FLOW = [
  "pending",
  "confirmed",
  "preparing",
  "ready",
  "out_for_delivery",
  "delivered",
];

export type Restaurant = {
  id: string;
  name: string;
  description: string;
  phone: string;
  address: string;
  logo_url: string;
  is_active: boolean;
  rating_average: number | null;
  review_count: number;
};

export type Review = {
  id: string;
  user: string;
  user_email: string;
  restaurant: string;
  restaurant_name: string;
  order: string | null;
  rating: number;
  title: string;
  comment: string;
  created_at: string;
};

export type ReviewSummary = {
  restaurant: string;
  restaurant_name: string;
  average_rating: number | null;
  review_count: number;
};
