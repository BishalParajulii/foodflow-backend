import type { NextApiRequest } from "next";

export function isAdmin(req: NextApiRequest): boolean {
  const cookie = req.headers.cookie;
  if (!cookie) return false;
  const match = cookie.match(/adminToken=([^;]+)/);
  return match !== null && match[1] === "secret";
}