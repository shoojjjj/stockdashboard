import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  if (!/^[a-f0-9]{12}$/.test(id)) {
    return NextResponse.json({ error: "Invalid article id" }, { status: 400 });
  }

  const filePath = path.join(process.cwd(), "public", "data", "columns", `${id}.json`);
  try {
    const raw = await readFile(filePath, "utf-8");
    return NextResponse.json(JSON.parse(raw));
  } catch {
    return NextResponse.json(
      { error: "Article not found. Run npm run build:data on PC." },
      { status: 404 }
    );
  }
}
