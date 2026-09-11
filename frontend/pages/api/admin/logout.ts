import type { NextApiRequest, NextApiResponse } from "next";

export default function handler(
  _req: NextApiRequest,
  res: NextApiResponse
) {
  // Clear the cookie by setting it to expire in the past
  res.setHeader(
    "Set-Cookie",
    "adminToken=; Path=/; HttpOnly; SameSite=Strict; MaxAge=0"
  );
  return res.status(200).json({ success: true });
}