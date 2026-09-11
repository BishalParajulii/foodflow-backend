// `fetcher` is for Next.js INTERNAL API routes (pages/api/*).
// These are served by the frontend itself (port 3000), so the URL must stay
// relative. Prefixing with NEXT_PUBLIC_API_URL (Django, port 8000) sends
// e.g. "/api/menu" to Django as "http://localhost:8000/api/menu" which does
// not exist -> Django logs "Not Found: /api/menu" + 404.
export async function fetcher<T>(endpoint: string): Promise<T> {
  const res = await fetch(endpoint, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch ${endpoint}: ${res.status}`);
  }
  return res.json();
}

// `backendFetcher` is for the Django API (http://localhost:8000).
// Correct Django menu endpoints (see backend/config/urls.py):
//   GET /api/v1/menu/items/
//   GET /api/v1/menu/categories/
//   GET /api/v1/menu/modifier-groups/
// Django wraps success payloads as { success: true, message, data } and
// paginates lists as { count, next, previous, results }. This helper unwraps
// to the raw list/object. No CORS package is installed on the backend, so
// prefer calling this from getServerSideProps / API routes (server-side),
// not directly from the browser cross-origin (3000 -> 8000).
export async function backendFetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const base = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const res = await fetch(`${base}${normalizedPath}`, {
    headers: { Accept: "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`Backend fetch ${normalizedPath} failed: ${res.status}`);
  }
  const json = await res.json();
  // Unwrap { success: true, data: <paginated|list|object> }
  const data = json && typeof json === "object" && "data" in json ? (json as any).data : json;
  // Unwrap DRF pagination { results: [...] }
  if (data && typeof data === "object" && Array.isArray((data as any).results)) {
    return (data as any).results as T;
  }
  return data as T;
}