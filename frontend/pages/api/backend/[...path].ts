import type { NextApiRequest, NextApiResponse } from "next";

// Generic server-side proxy to the Django API.
// Why: the backend has no CORS package installed, so browsers on :3000
// cannot call :8000 directly. All browser traffic goes to this same-origin
// route, which forwards to Django and returns the response as-is.
//
//   /api/backend/api/v1/menu/items/  ->  http://localhost:8000/api/v1/menu/items/
// Auth: pass `Authorization: Bearer <access>` through from the client.

const BACKEND =
  (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
    /\/$/,
    ""
  );

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { path, ...query } = req.query;
  const parts = Array.isArray(path) ? path : [path].filter(Boolean);
  const target = `${BACKEND}/${parts.join("/")}`;

  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(query)) {
    if (Array.isArray(v)) v.forEach((x) => qs.append(k, x));
    else if (v !== undefined) qs.append(k, v as string);
  }
  const url = qs.toString() ? `${target}?${qs}` : target;

  const headers: Record<string, string> = { Accept: "application/json" };
  const contentType = req.headers["content-type"];
  if (contentType) headers["Content-Type"] = contentType;
  const auth = req.headers.authorization;
  if (auth) headers["Authorization"] = auth;

  const init: RequestInit = { method: req.method, headers };
  if (req.method && !["GET", "HEAD"].includes(req.method)) {
    init.body = typeof req.body === "string" ? req.body : JSON.stringify(req.body ?? {});
    if (!headers["Content-Type"]) headers["Content-Type"] = "application/json";
  }

  try {
    const upstream = await fetch(url, init);
    const text = await upstream.text();
    res.status(upstream.status);
    try {
      res.json(JSON.parse(text));
    } catch {
      res.send(text);
    }
  } catch (e: any) {
    res.status(502).json({ success: false, error: { message: `Backend unreachable: ${e?.message}` } });
  }
}
