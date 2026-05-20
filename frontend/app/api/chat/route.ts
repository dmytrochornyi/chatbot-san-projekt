const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: Request) {
  const body = await req.json();

  const messages = (body.messages ?? []).map(
    (m: { role: string; content: unknown }) => ({
      role: m.role,
      content:
        typeof m.content === "string"
          ? m.content
          : (m.content as { type: string; text?: string }[])
              .filter((p) => p.type === "text")
              .map((p) => p.text)
              .join(""),
    }),
  );

  const response = await fetch(`${BACKEND_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });

  return new Response(response.body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "X-Vercel-AI-Data-Stream": "v1",
    },
  });
}
