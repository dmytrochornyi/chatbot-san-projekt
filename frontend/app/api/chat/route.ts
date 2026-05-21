import { createOpenAI } from "@ai-sdk/openai";
import { streamText, convertToModelMessages, type UIMessage } from "ai";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";
const OLLAMA_URL = process.env.OLLAMA_URL ?? "http://localhost:11434";
const OLLAMA_MODEL = process.env.OLLAMA_MODEL ?? "llama3.2";

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const lastMessage = messages[messages.length - 1];
  const question =
    lastMessage?.parts
      ?.filter((p) => p.type === "text")
      .map((p) => (p as { type: "text"; text: string }).text)
      .join("") ?? "";

  const retrieveRes = await fetch(`${BACKEND_URL}/api/retrieve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const { context } = await retrieveRes.json();

  const ollama = createOpenAI({
    baseURL: `${OLLAMA_URL}/v1`,
    apiKey: "ollama",
    compatibility: "compatible",
  });

  const result = streamText({
    model: ollama(OLLAMA_MODEL),
    system: `You are a helpful academic assistant for Społeczna Akademia Nauk (SAN) university.
Answer the student's question using only the provided context from university documents.
If the context does not contain enough information to answer, say so honestly.
Answer in the same language as the question.

Context:
${context}`,
    messages: await convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
