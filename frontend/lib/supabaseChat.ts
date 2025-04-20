import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function fetchRecentChat(user_id: string, limit = 5) {
  const { data } = await supabase
    .from("chat_history")
    .select("prompt, response")
    .eq("user_id", user_id)
    .order("timestamp", { ascending: true })
    .limit(limit);

  return data ?? [];
}

export async function saveChat(user_id: string, prompt: string, response: string) {
  await supabase.from("chat_history").insert({ user_id, prompt, response });
}
