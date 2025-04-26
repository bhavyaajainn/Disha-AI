// frontend/lib/app.ts

import { supabase } from "@/lib/supabaseClient";

export const sendToDisha = async (
  message: string, 
  isGuest: boolean = false,
  userId: string | null = null
): Promise<string> => {
  try {
    // For guest users, use a temporary guest ID but don't store it
    let user_id = userId;
    
    if (!isGuest) {
      // Regular user flow - get authenticated user ID
      if (!userId) {
        const { data } = await supabase.auth.getUser();
        user_id = data?.user?.id || null;
        
        if (!user_id) {
          throw new Error("User is not authenticated.");
        }
      }
    } else {
      // Guest user flow - use a temporary ID that's not stored persistently
      // Generate a random temporary ID prefixed with 'temp_' to indicate it's not for storage
      user_id = `temp_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
    }

    // Call FastAPI endpoint with guest flag
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        message, 
        user_id,
        is_guest: isGuest 
      }),
    });

    if (!res.ok) {
      throw new Error("Failed to fetch response from backend.");
    }

    const dataJson = await res.json();
    console.log("✅ Disha AI Response:", dataJson);

    const reply = dataJson.reply;

    // Handle reply formats
    if (Array.isArray(reply)) {
      const texts = reply
        .filter((r) => r.type === "text" && typeof r.text === "string")
        .map((r) => r.text.trim());

      return texts.join("\n").trim() || "[No reply received]";
    }

    // Fallback
    return typeof reply === "string" ? reply : "[No reply received]";
  } catch (error) {
    console.error("Error in sendToDisha:", error);
    
    // For guest users with connection issues, provide a fallback response
    if (isGuest) {
      return "I'm having trouble connecting to the server. As a guest user, you might experience occasional limitations. Please try again or consider creating an account for a more reliable experience.";
    }
    
    throw error;
  }
};