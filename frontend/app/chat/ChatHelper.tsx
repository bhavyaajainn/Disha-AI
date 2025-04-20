import { Dispatch, SetStateAction, RefObject } from "react";
import { supabase } from "../utils/config";
import { sendToDisha } from "@/lib/app";
import { Message } from "@/types";
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";
import ReactMarkdown from "react-markdown";

/**
 * Handles quick response options displayed as chips
 * Provides tailored responses for different support categories
 */
export const handleChipClick = (
  option: string,
  setMessages: Dispatch<SetStateAction<Message[]>>,
  setIsLoading: Dispatch<SetStateAction<boolean>>
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
        aiResponseText = "I see you're interested in exploring job opportunities. Can you tell me more about what you're looking for?\n\n" +
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
  textFieldRef: RefObject<HTMLTextAreaElement>
) => {
  if (input.trim()) {
    const userMessage: Message = {
      sender: "user",
      text: input,
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
      const aiReply = await sendToDisha(input);

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
 * Processes user feedback on AI responses
 * Stores feedback in database and updates UI state
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
}: {
  feedbackText: string;
  currentFeedbackMessage: string | null;
  messages: Message[];
  userId: string | null;
  setMessages: Dispatch<SetStateAction<Message[]>>;
  setFeedbackDialogOpen: Dispatch<SetStateAction<boolean>>;
  setSnackbarMessage: Dispatch<SetStateAction<string>>;
  setSnackbarOpen: Dispatch<SetStateAction<boolean>>;
}) => {
  if (!feedbackText.trim()) return;

  try {
    const feedbackMessage = messages.find(msg => msg.id === currentFeedbackMessage);
    if (!feedbackMessage) {
      throw new Error("Message not found");
    }

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

    const feedbackRecord = {
      user_id: currentUserId, 
      feedback_text: feedbackText,
      message_content: feedbackMessage.text,
    };

    const { error } = await supabase
      .from('feedback')
      .insert(feedbackRecord);

    if (error) {
      throw error;
    }

    setMessages((prevMessages) =>
      prevMessages.map((msg) =>
        msg.id === currentFeedbackMessage
          ? { ...msg, feedback: "negative" }
          : msg
      )
    );

    setFeedbackDialogOpen(false);
    setSnackbarMessage("Your feedback got registered with us");
    setSnackbarOpen(true);
  } catch (error) {
    console.error("Error submitting feedback:", error);
    setSnackbarMessage("Failed to submit feedback. Please try again.");
    setSnackbarOpen(true);
  }
};

/**
 * Utility function to copy text to clipboard
 */
export const copyToClipboard = (
  text: string,
  setSnackbarMessage: Dispatch<SetStateAction<string>>,
  setSnackbarOpen: Dispatch<SetStateAction<boolean>>
) => {
  navigator.clipboard.writeText(text).then(() => {
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
  router: AppRouterInstance
) => {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    
    localStorage.removeItem("dishaKeepSignedIn");
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
            key.includes("sign")
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
  
  /** The renderMessageText function processes and formats a given text string, applying specific replacements to enhance readability (e.g., adding line breaks before bullet points). It then renders the processed text as Markdown using the ReactMarkdown component, with custom styling for list items and paragraphs.**/
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