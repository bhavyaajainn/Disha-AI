import { supabase } from "@/lib/supabaseClient";

export const sendToDisha = async (message: string): Promise<string> => {
  // ✅ Get logged-in user's UUID
  const { data } = await supabase.auth.getUser();
  const user_id = data?.user?.id;

  if (!user_id) {
    throw new Error("User is not authenticated.");
  }

  // ✅ Call FastAPI endpoint
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, user_id }),
  });

  if (!res.ok) {
    throw new Error("Failed to fetch response from backend.");
  }

  const dataJson = await res.json();
  console.log("✅ Disha AI Response:", dataJson);

  const reply = dataJson.reply;

  // ✅ Fix: reply is an array of { type, text }
  if (Array.isArray(reply)) {
    const texts = reply
      .filter((r) => r.type === "text" && typeof r.text === "string")
      .map((r) => r.text.trim());

    return texts.join("\n").trim() || "[No reply received]";
  }

  // fallback
  return typeof reply === "string" ? reply : "[No reply received]";
};
