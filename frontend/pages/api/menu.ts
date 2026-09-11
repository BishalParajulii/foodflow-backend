import type { NextApiRequest, NextApiResponse } from "next";
import { readJSON, writeJSON } from "@/src/lib/file";
import { isAdmin } from "@/src/lib/auth";

const MENU_FILE = "src/data/menu.json";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "GET") {
    // Public endpoint: anyone can view the menu
    try {
      const menu = await readJSON<MenuItem[]>(MENU_FILE);
      return res.status(200).json(menu);
    } catch (e) {
      // If file doesn't exist, return empty array
      return res.status(200).json([]);
    }
  }

  // For write operations, require admin
  if (!isAdmin(req)) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  if (req.method === "POST") {
    const { name, description, price, image, category } = req.body;
    if (!name || !description || price === undefined || !image || !category) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    let menu: MenuItem[] = [];
    try {
      menu = await readJSON<MenuItem[]>(MENU_FILE);
    } catch (e) {
      menu = [];
    }

    const newItem: MenuItem = {
      id: Date.now() + Math.random(), // simple id, not perfect but fine for demo
      name,
      description,
      price: Number(price),
      image,
      category,
    };

    menu.push(newItem);
    await writeJSON(MENU_FILE, menu);
    return res.status(201).json(newItem);
  }

  if (req.method === "PUT") {
    const { id, name, description, price, image, category } = req.body;
    if (!id || name === undefined || description === undefined || price === undefined || image === undefined || category === undefined) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    let menu: MenuItem[] = [];
    try {
      menu = await readJSON<MenuItem[]>(MENU_FILE);
    } catch (e) {
      return res.status(404).json({ error: "Menu not found" });
    }

    const index = menu.findIndex(item => item.id === id);
    if (index === -1) {
      return res.status(404).json({ error: "Menu item not found" });
    }

    menu[index] = {
      ...menu[index],
      name,
      description,
      price: Number(price),
      image,
      category,
    };

    await writeJSON(MENU_FILE, menu);
    return res.status(200).json(menu[index]);
  }

  if (req.method === "DELETE") {
    const { id } = req.body;
    if (!id) {
      return res.status(400).json({ error: "Missing id" });
    }

    let menu: MenuItem[] = [];
    try {
      menu = await readJSON<MenuItem[]>(MENU_FILE);
    } catch (e) {
      return res.status(404).json({ error: "Menu not found" });
    }

    const index = menu.findIndex(item => item.id === id);
    if (index === -1) {
      return res.status(404).json({ error: "Menu item not found" });
    }

    const deleted = menu.splice(index, 1);
    await writeJSON(MENU_FILE, menu);
    return res.status(200).json(deleted[0]);
  }

  return res.status(405).end(); // Method Not Allowed
}

// Type for menu item
interface MenuItem {
  id: number | string;
  name: string;
  description: string;
  price: number;
  image: string;
  category: string;
}