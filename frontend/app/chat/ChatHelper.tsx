import { Dispatch, SetStateAction, RefObject } from "react";
import { supabase } from "../utils/config";
import { sendToDisha } from "@/lib/app";
import { Message } from "@/types";
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";
import ReactMarkdown from "react-markdown";

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

/**
 * Handles quick response options displayed as chips
 * Provides tailored responses for different support categories
 */
export const handleChipClick = (
  option: string,
  setMessages: Dispatch<SetStateAction<Message[]>>,
  setIsLoading: Dispatch<SetStateAction<boolean>>,
  isGuest: boolean = false
) => {
  let message = "";
  switch (option) {
    case "Jobs":
      message = "Find me jobs";
      break;
    case "Mentorship":
      message = "Connect with a mentor";
      break;
    case "Community":
      message = "Explore communities";
      break;
    default:
      break;
  }

  if (message) {
    const userMessage: Message = {
      sender: "user",
      text: message,
      timestamp: new Date(),
      id: Date.now().toString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);

      let aiResponseText = "";
      
      if (option === "Jobs") {
        aiResponseText = isGuest
          ? "I see you're interested in exploring job opportunities. This feature provides personalized job recommendations based on your profile, skills, and career aspirations.\n\n" +
            "As a guest user, you have access to basic job search assistance. For personalized job recommendations and our smart career path generator:\n\n" +
            "• Create a free account to build your profile\n\n" +
            "• Access AI-powered job matching\n\n" +
            "• Get customized career development plans\n\n" +
            "For now, I can still answer general questions about job searching, resume tips, or interview preparation. What would you like to know?"
          : "I see you're interested in exploring job opportunities. Can you tell me more about what you're looking for?\n\n" +
            "• Are you actively or passively looking for a job?\n\n" +
            "• Would you like me to search for relevant openings?\n\n" +
            "• Or would you prefer help with learning new skills that can improve your job prospects?\n\n" +
            "The more details you provide about your experience, skills, and career goals, the better I can assist you.";
      } 
      else if (option === "Mentorship") {
        aiResponseText = "I'd be happy to help with mentorship resources. Please let me know what you're interested in:\n\n" +
          "• Online courses and learning paths in specific skills or fields\n\n" +
          "• Upcoming workshops or training sessions relevant to your interests\n\n" +
          "• Connection with a personal mentor for one-on-one guidance\n\n" +
          "• Industry-specific learning resources and certification programs\n\n" +
          "What field or skill are you looking to develop, and which type of mentorship support would be most helpful for you right now?";
      } 
      else if (option === "Community") {
        aiResponseText = "Exploring communities is a great way to grow personally and professionally. To help you find the right communities:\n\n" +
          "• What topics or areas are you most interested in?\n\n" +
          "• Are you looking for in-person meetups, online forums, or professional networks?\n\n" +
          "• Would you prefer communities focused on learning, networking, or social support?\n\n" +
          "Let me know your interests, and I can suggest some communities that might be a good fit for you.";
      }

      const aiMessage: Message = {
        sender: "ai",
        text: aiResponseText,
        timestamp: new Date(),
        id: (Date.now() + 1).toString(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 2000);
  }
};

/**
 * Processes user message submission and fetches AI response
 * Handles UI state changes during the process
 */
export const handleSubmitMessage = async (
  input: string,
  setMessages: Dispatch<SetStateAction<Message[]>>,
  setInput: Dispatch<SetStateAction<string>>,
  setIsLoading: Dispatch<SetStateAction<boolean>>,
  textFieldRef: RefObject<HTMLTextAreaElement>,
  isGuest: boolean = false,
  userId: string | null = null
) => {
  if (input.trim()) {
    // Scrub any PII from user input before displaying in UI
    const cleanInput = scrubPII(input);
    
    const userMessage: Message = {
      sender: "user",
      text: cleanInput, // Use clean version for display
      timestamp: new Date(),
      id: Date.now().toString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    if (textFieldRef.current) {
      textFieldRef.current.style.height = "auto";
      textFieldRef.current.style.overflowY = "hidden";
    }

    setIsLoading(true);

    try {
      let aiReply;

      // Check for premium feature requests when in guest mode
      if (isGuest && containsPremiumRequest(input)) {
        aiReply = generateGuestLimitationResponse();
      } else {
        // For non-premium requests or authenticated users, use the regular API
        // Note: We send the original input to the API, which will do its own PII scrubbing
        aiReply = await sendToDisha(input, isGuest, userId);
      }

      // No need to scrub AI reply as it should already be scrubbed by the backend
      const aiMessage: Message = {
        sender: "ai",
        text: aiReply,
        timestamp: new Date(),
        id: (Date.now() + 1).toString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error fetching AI response:", error);
      const errorMessage: Message = {
        sender: "ai",
        text: "⚠️ Sorry, something went wrong. Please try again later.",
        timestamp: new Date(),
        id: (Date.now() + 1).toString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }
};

/**
 * Checks if the user input contains requests for premium features
 */
const containsPremiumRequest = (input: string): boolean => {
  const premiumKeywords = [
    "career path generator",
    "career path",
    "generate my career path",
    "personalized career",
    "custom roadmap",
    "career roadmap",
    "career progression",
    "build my career",
    "my career journey",
    "personalized job match",
    "skill assessment"
  ];
  
  const lowercaseInput = input.toLowerCase();
  return premiumKeywords.some(keyword => lowercaseInput.includes(keyword));
};

/**
 * Generates a response for guest users trying to access premium features
 */
const generateGuestLimitationResponse = (): string => {
  return "I see you're interested in our advanced career planning features. The Smart Career Path Generator and personalized career roadmap are premium features available only to registered users.\n\n" +
    "To unlock these features:\n\n" +
    "• Create a free account to access all of Disha AI's capabilities\n\n" +
    "• Build your profile to receive tailored career guidance\n\n" +
    "• Get personalized job recommendations and industry insights\n\n" +
    "Would you like to know more about other ways I can help you with your career or professional development as a guest user?";
};

/**
 * Processes user feedback on AI responses
 * For guest users, doesn't store feedback in the database
 * Scrubs any PII from feedback content
 */
export const handleFeedbackSubmission = async ({
  feedbackText,
  currentFeedbackMessage,
  messages,
  userId,
  setMessages,
  setFeedbackDialogOpen,
  setSnackbarMessage,
  setSnackbarOpen,
  isGuest = false
}: {
  feedbackText: string;
  currentFeedbackMessage: string | null;
  messages: Message[];
  userId: string | null;
  setMessages: Dispatch<SetStateAction<Message[]>>;
  setFeedbackDialogOpen: Dispatch<SetStateAction<boolean>>;
  setSnackbarMessage: Dispatch<SetStateAction<string>>;
  setSnackbarOpen: Dispatch<SetStateAction<boolean>>;
  isGuest?: boolean;
}) => {
  if (!feedbackText.trim()) return;

  try {
    const feedbackMessage = messages.find(msg => msg.id === currentFeedbackMessage);
    if (!feedbackMessage) {
      throw new Error("Message not found");
    }

    // Scrub any PII from the feedback text
    const cleanFeedbackText = scrubPII(feedbackText);
    
    // Also scrub message content just to be safe
    const cleanMessageContent = scrubPII(feedbackMessage.text);

    // Only store feedback in the database for authenticated users
    if (!isGuest) {
      let currentUserId: string | null = userId;
      
      if (!currentUserId) {
        try {
          const { data: { user } } = await supabase.auth.getUser();
          currentUserId = user?.id ?? null; 
        } catch (authError) {
          console.warn("Could not get authenticated user:", authError);
          currentUserId = null; 
        }
      }

      // Only store in database if we have a valid user ID and not a guest
      if (currentUserId) {
        const feedbackRecord = {
          user_id: currentUserId, 
          feedback_text: cleanFeedbackText,
          message_content: cleanMessageContent
        };

        const { error } = await supabase
          .from('feedback')
          .insert(feedbackRecord);

        if (error) {
          throw error;
        }
      }
    } else {
      // For guest users, just log feedback to console but don't store in database
      console.log("Guest user feedback received (not stored):", {
        feedback_text: cleanFeedbackText,
        message_content: cleanMessageContent
      });
    }

    // Update UI state for both guest and authenticated users
    setMessages((prevMessages) =>
      prevMessages.map((msg) =>
        msg.id === currentFeedbackMessage
          ? { ...msg, feedback: "negative" }
          : msg
      )
    );

    setFeedbackDialogOpen(false);
    setSnackbarMessage(isGuest 
      ? "Thank you for your feedback" 
      : "Your feedback got registered with us");
    setSnackbarOpen(true);
  } catch (error) {
    console.error("Error submitting feedback:", error);
    setSnackbarMessage("Failed to submit feedback. Please try again.");
    setSnackbarOpen(true);
  }
};

/**
 * Utility function to copy text to clipboard
 * Ensures no PII data is copied
 */
export const copyToClipboard = (
  text: string,
  setSnackbarMessage: Dispatch<SetStateAction<string>>,
  setSnackbarOpen: Dispatch<SetStateAction<boolean>>
) => {
  // Scrub any PII before copying to clipboard
  const cleanText = scrubPII(text);
  
  navigator.clipboard.writeText(cleanText).then(() => {
    setSnackbarMessage("Text copied to clipboard");
    setSnackbarOpen(true);
  });
};

/**
 * Handles user logout process
 * Clears authentication tokens and redirects user
 */
export const handleLogout = async (
  setLogoutDialogOpen: Dispatch<SetStateAction<boolean>>,
  setSnackbarMessage: Dispatch<SetStateAction<string>>,
  setSnackbarOpen: Dispatch<SetStateAction<boolean>>,
  router: AppRouterInstance,
  isGuest: boolean = false
) => {
  try {
    if (!isGuest) {
      // Regular user logout
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    }
    
    // Clear all relevant storage for both guest and regular users
    localStorage.removeItem("dishaKeepSignedIn");
    localStorage.removeItem("dishaGuestSession");
    localStorage.removeItem("sb-fictrvuyjpkcpwlbfvbd-auth-token");
    
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (
            key.includes("token") || 
            key.includes("auth") || 
            key.includes("user") || 
            key.includes("session") ||
            key.includes("logged") ||
            key.includes("sign") || 
            key.includes("guest")
          )) {
          localStorage.removeItem(key);
        }
      }
    } catch (error) {
      console.error("Error clearing localStorage:", error);
    }
    
    router.push("/");
  } catch (error) {
    console.error("Error during logout:", error);
    setSnackbarMessage("Failed to logout. Please try again.");
    setSnackbarOpen(true);
  } finally {
    setLogoutDialogOpen(false);
  }
};

/**
 * Utility function to get a random loading message
 * Used to enhance user experience during loading states
 */
export const getRandomLoadingMessage = () => {
    const loadingMessages = [
      "Finding insights to help you lead at every step",
      "Connecting the dots on your path to growth",
      "Let's see what I can find for you",
      "Crafting something meaningful just for you",
    ];
    
    const randomIndex = Math.floor(Math.random() * loadingMessages.length);
    return loadingMessages[randomIndex];
  };
  
  /** 
   * The renderMessageText function processes and formats a given text string, 
   * applying specific replacements to enhance readability (e.g., adding line breaks before bullet points). 
   * It then renders the processed text as Markdown using the ReactMarkdown component, 
   * with custom styling for list items and paragraphs.
   */
  export const renderMessageText = (text: string) => {
    let processedText = text;
    processedText = processedText.replace(/([.!?])\s+•\s+/g, '$1\n\n• '); 
    processedText = processedText.replace(/:\s+•\s+/g, ':\n\n• ');
    processedText = processedText.replace(/•\s+/g, '\n• ');
    processedText = processedText.replace(/\n•\s+/g, '\n\n• ');
    
    return (
      <div className="markdown-body">
        <ReactMarkdown
          components={{
            li: ({ children }) => <li className="list-item">{children}</li>,
            ul: ({ children }) => <ul className="list-container">{children}</ul>,
            ol: ({ children }) => <ol className="list-container">{children}</ol>,
            p: ({ node, children }) => {
              
              
              interface ParentNode {
                type?: string;
                tagName?: string;
              }
              
              
              const parent = (node as { parent?: ParentNode })?.parent;
              const isInsideListItem = 
                parent?.type === 'element' && 
                parent?.tagName === 'li';
              
              
              return isInsideListItem ? <>{children}</> : <p>{children}</p>;
            }
          }}
        >
          {processedText}
        </ReactMarkdown>
      </div>
    );
  };