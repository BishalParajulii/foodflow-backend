// Server-side only bridge to the Django API for the admin area.
// Next.js API routes (pages/api/*) use this to speak to Django with a
// platform-admin JWT obtained from service credentials. The access token is
// cached in-process and refreshed before it expires. Never import from the
// browser (it reads process.env and holds server-side state).

const BACKEND = (
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000"
).replace(/\/$/, "");

const ADMIN_EMAIL = process.env.DJANGO_ADMIN_EMAIL || "admin@foodflow.local";
const ADMIN_PASSWORD = process.env.DJANGO_ADMIN_PASSWORD || "admin123";

// Access tokens live for JWT_ACCESS_MINUTES (default 60); refresh before that.
const TOKEN_TTL_MS = 50 * 60 * 1000;

let cached: { access: string; expiresAt: number } | null = null;

async function getAccessToken(): Promise<string> {
  if (cached && cached.expiresAt > Date.now()) {
    return cached.access;
  }
  const res = await fetch(`${BACKEND}/api/v1/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email: ADMIN_EMAIL, password: ADMIN_PASSWORD }),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Admin backend login failed (${res.status})`);
  }
  const json = await res.json();
  const access: string | undefined = json?.data?.access;
  if (!access) {
    throw new Error("Admin backend login returned no access token");
  }
  cached = { access, expiresAt: Date.now() + TOKEN_TTL_MS };
  return access;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await getAccessToken();
  const res = await fetch(`${BACKEND}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Admin backend request failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

/** Fetch the order list (paginated envelope) with optional filters. */
export async function adminFetchOrders(query: Record<string, string> = {}) {
  const qs = new URLSearchParams(query).toString();
  return request(`/api/v1/orders/${qs ? `?${qs}` : ""}`);
}

/** Advance an order to a new status (PATCH /api/v1/orders/<id>/). */
export async function adminUpdateOrderStatus(id: string, status: string) {
  return request(`/api/v1/orders/${id}/`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}