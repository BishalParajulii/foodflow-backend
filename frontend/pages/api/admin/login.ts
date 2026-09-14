import type { NextApiRequest, NextApiResponse } from "next";

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).end(); // Method Not Allowed
  }

  const { username, password } = req.body;

  // Admin credentials come from server-side env (never NEXT_PUBLIC_*).
  // Defaults keep local demo working; override in production via
  //   ADMIN_USERNAME / ADMIN_PASSWORD  (see docker-compose.yml).
  const ADMIN_USERNAME = process.env.ADMIN_USERNAME || "admin";
  const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "admin123";

  if (username === ADMIN_USERNAME && password === ADMIN_PASSWORD) {
    // Set httpOnly cookie
    res.setHeader(
      "Set-Cookie",
      "adminToken=secret; Path=/; HttpOnly; SameSite=Strict; MaxAge=3600" // 1 hour
    );
    return res.status(200).json({ success: true });
  }

  return res.status(401).json({ error: "Invalid credentials" });
}