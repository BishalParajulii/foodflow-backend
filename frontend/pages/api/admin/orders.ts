import type { NextApiRequest, NextApiResponse } from "next";

import { isAdmin } from "@/src/lib/auth";
import { adminFetchOrders, adminUpdateOrderStatus } from "@/src/lib/adminBackend";

// Admin-order bridge: /api/admin/orders (GET list, PATCH status).
// The browser only ever has the adminToken cookie; this route swaps it for a
// Django platform-admin JWT server-side and forwards to /api/v1/orders/.

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (!isAdmin(req)) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  try {
    if (req.method === "GET") {
      const { status, restaurant, search, page_size } = req.query;
      const params: Record<string, string> = {};
      if (typeof status === "string" && status) params.status = status;
      if (typeof restaurant === "string" && restaurant) params.restaurant = restaurant;
      if (typeof search === "string" && search) params.search = search;
      if (typeof page_size === "string" && page_size) params.page_size = page_size;
      const data = await adminFetchOrders(params);
      return res.status(200).json(data);
    }

    if (req.method === "PATCH") {
      const { id, status } = req.body || {};
      if (!id || !status) {
        return res.status(400).json({ error: "id and status are required" });
      }
      const data = await adminUpdateOrderStatus(String(id), String(status));
      return res.status(200).json(data);
    }

    return res.status(405).end();
  } catch (e: any) {
    return res
      .status(502)
      .json({ success: false, error: { message: e?.message || "Backend error" } });
  }
}