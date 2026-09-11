import type { NextApiRequest, NextApiResponse } from "next";
import { writeJSON, readJSON } from "@/src/lib/file";
import { isAdmin } from "@/src/lib/auth";

interface ContactMessage {
  id: string;
  name: string;
  email: string;
  message: string;
  timestamp: string; // ISO string
}

const DATA_FILE = "src/data/messages.json";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "POST") {
    const { name, email, message } = req.body;
    if (!name || !email || !message) {
      return res.status(400).json({ error: "Missing fields" });
    }

    // Read existing messages
    let messages: ContactMessage[] = [];
    try {
      messages = await readJSON<ContactMessage[]>(DATA_FILE);
    } catch (e) {
      // file may not exist yet
      messages = [];
    }

    const newMessage: ContactMessage = {
      id: `${Date.now()}-${Math.random()
        .toString(36)
        .substr(2, 9)}`,
      name,
      email,
      message,
      timestamp: new Date().toISOString(),
    };

    messages.push(newMessage);
    await writeJSON(DATA_FILE, messages);

    return res.status(201).json({ success: true });
  } else if (req.method === "GET") {
    // Protect GET with admin auth
    if (!isAdmin(req)) {
      return res.status(401).json({ error: "Unauthorized" });
    }

    try {
      const messages = await readJSON<ContactMessage[]>(DATA_FILE);
      return res.status(200).json(messages);
    } catch (e) {
      return res.status(200).json([]); // empty if no file
    }
  } else if (req.method === "DELETE") {
    // Protect DELETE with admin auth
    if (!isAdmin(req)) {
      return res.status(401).json({ error: "Unauthorized" });
    }
    const { id } = req.body;
    if (!id) {
      return res.status(400).json({ error: "Missing id" });
    }

    let messages: ContactMessage[] = [];
    try {
      messages = await readJSON<ContactMessage[]>(DATA_FILE);
    } catch (e) {
      return res.status(400).json({ error: "Failed to read messages" });
    }

    const initialLength = messages.length;
    messages = messages.filter(m => m.id !== id);
    if (messages.length === initialLength) {
      return res.status(404).json({ error: "Message not found" });
    }

    await writeJSON(DATA_FILE, messages);
    return res.status(200).json({ success: true });
  } else {
    return res.status(405).end(); // Method Not Allowed
  }
}