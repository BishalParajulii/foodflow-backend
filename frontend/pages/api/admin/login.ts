import type { NextApiRequest, NextApiResponse } from "next";

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).end(); // Method Not Allowed
  }

  const { username, password } = req.body;

  // Hardcoded credentials for demo (in production use proper auth)
  if (username === "admin" && password === "admin123") {
    // Set httpOnly cookie
    res.setHeader(
      "Set-Cookie",
      "adminToken=secret; Path=/; HttpOnly; SameSite=Strict; MaxAge=3600" // 1 hour
    );
    return res.status(200).json({ success: true });
  }

  return res.status(401).json({ error: "Invalid credentials" });
}