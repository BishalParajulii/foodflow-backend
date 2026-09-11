import { promises as fs } from "fs";
import path from "path";

export async function readJSON<T>(filePath: string): Promise<T> {
  const fullPath = path.join(process.cwd(), filePath);
  const data = await fs.readFile(fullPath, "utf-8");
  return JSON.parse(data);
}

export async function writeJSON<T>(filePath: string, data: T): Promise<void> {
  const fullPath = path.join(process.cwd(), filePath);
  await fs.writeFile(fullPath, JSON.stringify(data, null, 2), "utf-8");
}