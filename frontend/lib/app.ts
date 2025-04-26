// frontend/lib/app.ts

import { supabase } from "@/lib/supabaseClient";

/**
 * Scrubs personally identifiable information (PII) from text
 * 
 * @param text Text to be scrubbed of PII
 * @returns Text with PII redacted
 */
export const scrubPII = (text: string): string => {
  // Email pattern
  text = text.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL REDACTED]');
  
  // Phone number patterns (various formats)
  text = text.replace(/\b(\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b/g, '[PHONE REDACTED]');
  
  // Social security / ID number patterns
  text = text.replace(/\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b/g, '[ID REDACTED]');
  
  // URLs with potential user IDs
  text = text.replace(/https?:\/\/[^\s/]+\/(?:user|profile|account|u)\/[a-zA-Z0-9_-]+/g, '[URL REDACTED]');
  
  // Physical addresses (simplified pattern)
  text = text.replace(/\b\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Plaza|Square|Sq|Trail|Tr|Parkway|Pkwy|Circle|Cir)\b/g, '[ADDRESS REDACTED]');
  
  // WhatsApp/Telegram number patterns
  text = text.replace(/\b(?:whatsapp|telegram|signal|viber)(?:\s+at)?\s+[+]?[0-9][0-9\s-]{7,}/g, '[CONTACT REDACTED]');
  
  // LinkedIn profile patterns
  text = text.replace(/linkedin\.com\/in\/[a-zA-Z0-9_-]+/g, '[LINKEDIN REDACTED]');
  
  // Other social media handles
  text = text.replace(/(?:@[a-zA-Z0-9_]{2,})/g, '[SOCIAL MEDIA HANDLE REDACTED]');
  
  return text;
};

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

    // Scrub PII from the message before sending to backend
    // Note: Backend will also scrub PII as a second layer of protection
    const cleanMessage = scrubPII(message);

    // Call FastAPI endpoint with guest flag
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ 
        message: cleanMessage, 
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