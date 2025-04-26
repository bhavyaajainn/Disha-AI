"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  AppBar,
  Toolbar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
  Tooltip,
  Chip,
  CircularProgress,
} from "@mui/material";
import Image from "next/image";
import SendIcon from "@mui/icons-material/Send";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline'; // Import for guest icon
import LockIcon from '@mui/icons-material/Lock'; // Import for premium feature icon
import { Message } from "@/types";
import { supabase } from "../utils/config";
import { 
  handleChipClick, 
  handleSubmitMessage, 
  handleFeedbackSubmission, 
  copyToClipboard,
  handleLogout,
  renderMessageText,
  getRandomLoadingMessage
} from "./ChatHelper";
import '../style/chat.scss';

/**
 * Main Chat Page component with embedded Suspense boundary
 * for hooks that require it (like useSearchParams)
 */
export default function ChatPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <ChatContent />
    </Suspense>
  );
}

/**
 * Loading state component displayed during suspense
 */
function LoadingState() {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        background: "linear-gradient(135deg, #2a0e60 0%, #451d98 50%, #6927c5 100%)",
      }}
    >
      <CircularProgress size={60} sx={{ color: "white" }} />
      <Typography variant="h6" sx={{ mt: 4, color: "white" }}>
        Loading...
      </Typography>
    </Box>
  );
}

/**
 * Main content component for the chat interface
 * Uses hooks that require Suspense boundary provided by the parent
 */
function ChatContent() {
  /**
   * Main state variables for the chat interface
   * messages: Array of chat messages between user and AI
   * input: Current text in the input field
   * loading state: Tracks when AI is generating a response
   */
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [isGuest, setIsGuest] = useState(false); // New state to track guest mode
  
  /**
   * Type definition for SpeechRecognition API
   */
  interface SpeechRecognitionEvent extends Event {
    results: SpeechRecognitionResultList;
    resultIndex: number;
    interpretation: unknown; // Replace 'any' with 'unknown' or a more specific type if known
  }

  interface SpeechRecognitionResult {
    isFinal: boolean;
    [index: number]: SpeechRecognitionAlternative;
  }

  interface SpeechRecognitionResultList {
    length: number;
    item(index: number): SpeechRecognitionResult;
    [index: number]: SpeechRecognitionResult;
  }

  interface SpeechRecognitionAlternative {
    transcript: string;
    confidence: number;
  }

  interface SpeechRecognitionError extends Event {
    error: string;
    message: string;
  }

  interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    maxAlternatives: number;
    start(): void;
    stop(): void;
    abort(): void;
    onerror: ((this: SpeechRecognition, ev: SpeechRecognitionError) => void) | null;
    onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => void) | null;
    onstart: ((this: SpeechRecognition, ev: Event) => void) | null;
    onend: ((this: SpeechRecognition, ev: Event) => void) | null;
  }

  interface SpeechRecognitionConstructor {
    new (): SpeechRecognition;
    prototype: SpeechRecognition;
  }

  /**
   * Speech recognition states
   */
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  
  /**
   * Dialog control states
   * Manage dialog visibility and related state
   */
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);
  const [signupDialogOpen, setSignupDialogOpen] = useState(false); // New dialog for upgrade prompt
  const [currentFeedbackMessage, setCurrentFeedbackMessage] = useState<string | null>(null);
  const [feedbackText, setFeedbackText] = useState("");
  
  /**
   * Notification state
   * Controls the visibility and message of the snackbar
   */
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  
  /**
   * References and router
   * Used for DOM manipulation and navigation
   */
  const router = useRouter();
  const searchParams = useSearchParams();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textFieldRef = useRef<HTMLTextAreaElement>(null) as React.RefObject<HTMLTextAreaElement>;

  /**
   * Initialize speech recognition on component mount
   */
  useEffect(() => {
    // Check if browser supports speech recognition
    if (typeof window !== 'undefined') {
      // Properly declare the window interfaces for TypeScript
      interface WindowWithSpeechRecognition extends Window {
        SpeechRecognition?: SpeechRecognitionConstructor;
        webkitSpeechRecognition?: SpeechRecognitionConstructor;
      }
      
      const windowWithSpeech = window as WindowWithSpeechRecognition;
      const SpeechRecognitionAPI = windowWithSpeech.SpeechRecognition || windowWithSpeech.webkitSpeechRecognition;
      
      if (SpeechRecognitionAPI) {
        recognitionRef.current = new SpeechRecognitionAPI();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        
        recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
          const transcript = Array.from(event.results)
            .map((result) => result[0])
            .map((result) => result.transcript)
            .join('');
          
          setInput(transcript);
        };
        
        recognitionRef.current.onerror = (event: SpeechRecognitionError) => {
          console.error('Speech recognition error', event.error);
          setIsListening(false);
          setSnackbarMessage(`Speech recognition error: ${event.error}`);
          setSnackbarOpen(true);
        };
        
        recognitionRef.current.onend = () => {
          if (isListening && recognitionRef.current) {
            recognitionRef.current.start();
          }
        };
      } else {
        setSpeechSupported(false);
      }
    }
    
    // Cleanup
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  /**
   * Handle listening state changes
   */
  useEffect(() => {
    if (!recognitionRef.current) return;
    
    try {
      if (isListening) {
        recognitionRef.current.start();
      } else {
        recognitionRef.current.stop();
      }
    } catch (error) {
      console.error('Speech recognition control error:', error);
      setIsListening(false);
    }
  }, [isListening]);

  /**
   * Initial setup
   * Get user ID and set welcome message
   */
  useEffect(() => {
    const getUserId = async () => {
      try {
        // Check if user is in guest mode
        const isGuestMode = searchParams.get("guest") === "true";
        setIsGuest(isGuestMode);
        
        if (isGuestMode) {
          // Get guest info from localStorage if available
          const guestSession = localStorage.getItem("dishaGuestSession");
          if (guestSession) {
            const guestData = JSON.parse(guestSession);
            setUserId(`guest_${guestData.id}`);
          } else {
            // Create a new guest session if none exists
            const guestId = `guest_${Date.now()}`;
            setUserId(guestId);
            const randomGuestName = searchParams.get("name") || "Guest User";
            localStorage.setItem("dishaGuestSession", JSON.stringify({
              id: guestId,
              name: randomGuestName,
              timestamp: new Date().toISOString(),
              isGuest: true
            }));
          }
        } else {
          // Regular user authentication check
          const { data: { user } } = await supabase.auth.getUser();
          if (user) {
            setUserId(user.id);
          } else {
            // Redirect to login if not authenticated and not in guest mode
            router.push("/");
          }
        }
      } catch (error) {
        console.error("Error getting user:", error);
        if (!isGuest) {
          router.push("/");
        }
      }
    };
    getUserId();  
    
    const name = searchParams.get("name");
    if (name?.trim()) {
      // Different welcome message for guest users
      if (searchParams.get("guest") === "true") {
        setMessages([
          {
            sender: "ai",
            text: `Welcome ${name}! I'm Disha AI, your career guidance assistant. You're currently using guest mode with access to our basic features.\n\n` +
                  `• Ask me questions about career advice, interview tips, or resume help\n\n` +
                  `• For personalized job matching and career path planning, you'll need to create an account\n\n` +
                  `How can I help you today?`,
            timestamp: new Date(),
            id: Date.now().toString(),
          },
        ]);
      } else {
        setMessages([
          {
            sender: "ai",
            text: `Hi ${name}, welcome! I'm Disha AI, here to guide your journey. How can I support you today?`,
            timestamp: new Date(),
            id: Date.now().toString(),
          },
        ]);
      }
    } else {
      router.push("/");
    }
  }, [searchParams, router]);

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /**
   * Dynamic textarea height adjustment
   */
  useEffect(() => {
    const textarea = textFieldRef.current;
    if (!textarea) return;
    
    textarea.style.height = "auto";
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 24), 150);
    textarea.style.height = `${newHeight}px`;
    textarea.style.overflowY = textarea.scrollHeight > 150 ? "auto" : "hidden";
  }, [input]);

  /**
   * Toggle speech recognition
   */
  const toggleListening = () => {
    if (!speechSupported) {
      setSnackbarMessage("Speech recognition is not supported in your browser.");
      setSnackbarOpen(true);
      return;
    }
    
    setIsListening((prevState) => !prevState);
    
    if (!isListening) {
      setSnackbarMessage("Listening...");
      setSnackbarOpen(true);
    } else {
      setSnackbarMessage("Stopped listening.");
      setSnackbarOpen(true);
    }
  };

  /**
   * Show upgrade dialog for guest users
   */
  const handleShowUpgradeDialog = () => {
    setSignupDialogOpen(true);
  };

  /**
   * Navigate to signup page
   */
  const handleUpgradeAccount = () => {
    setSignupDialogOpen(false);
    localStorage.removeItem("dishaGuestSession");
    router.push("/");
  };

  /**
   * Event handlers for user interactions
   */
  const handleQuickOptionClick = (option: string) => {
    handleChipClick(
      option,
      setMessages,
      setIsLoading,
      isGuest
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    // Stop listening if active
    if (isListening) {
      setIsListening(false);
    }
    
    await handleSubmitMessage(
      input,
      setMessages,
      setInput,
      setIsLoading,
      textFieldRef,
      isGuest,
      userId
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  const handleFeedback = (messageId: string) => {
    setCurrentFeedbackMessage(messageId);
    setFeedbackText("");
    setFeedbackDialogOpen(true);
  };

  const submitFeedback = async () => {
    await handleFeedbackSubmission({
      feedbackText,
      currentFeedbackMessage,
      messages,
      userId,
      setMessages,
      setFeedbackDialogOpen,
      setSnackbarMessage,
      setSnackbarOpen,
      isGuest
    });
  };

  const copyMessage = (text: string) => {
    copyToClipboard(
      text,
      setSnackbarMessage,
      setSnackbarOpen
    );
  };
  
  const handleLogoutClick = () => {
    setLogoutDialogOpen(true);
  };
  
  const handleLogoutConfirm = async () => {
    await handleLogout(
      setLogoutDialogOpen,
      setSnackbarMessage,
      setSnackbarOpen,
      router,
      isGuest
    );
  };
  
  const handleLogoutCancel = () => {
    setLogoutDialogOpen(false);
  };

  return (
    <Box className="chat-container">
      {/* Header */}
      <AppBar position="static" className="gradient-header">
        <Toolbar>
          <div className="logo-container">
            <Image
              src="/women-with-wings.png"
              alt="Disha AI Logo"
              className="header-logo"
              width={50}
              height={50}
            />
            <Typography variant="h6" component="div" className="app-title">
              DISHA AI
            </Typography>
          </div>
          
          {/* Guest Mode Indicator */}
          {isGuest && (
            <Tooltip title="You're using guest mode. Some features are limited.">
              <Chip
                icon={<PersonOutlineIcon />}
                label="Guest Mode"
                size="small"
                onClick={handleShowUpgradeDialog}
                sx={{
                  ml: 2,
                  bgcolor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.3)' },
                  borderRadius: '16px',
                  cursor: 'pointer'
                }}
              />
            </Tooltip>
          )}
          
          <Box sx={{ flexGrow: 1 }} />
          
          {/* Upgrade button for guest users */}
          {isGuest && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<LockIcon />}
              onClick={handleShowUpgradeDialog}
              sx={{ 
                mr: 2, 
                color: 'white', 
                borderColor: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'white'
                }
              }}
            >
              Upgrade
            </Button>
          )}
          
          <Tooltip title="Logout">
            <IconButton
              edge="end"
              color="inherit"
              aria-label="logout"
              onClick={handleLogoutClick}
              className="logout-button"
              sx={{ mr: 1 }}
            >
              <PowerSettingsNewIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Chat Messages */}
      <Box className="messages-container">
        {messages.map((message) => (
          <Box
            key={message.id}
            className={`message-wrapper ${
              message.sender === "user" ? "user-message" : "ai-message"
            }`}
          >
            {message.sender === "user" ? (
              <Paper
                className="message user-bubble no-shadow"
                elevation={1}
                sx={{
                  boxShadow: "none",
                }}
              >
                <Typography variant="body1">{message.text}</Typography>
              </Paper>
            ) : (
              <Box className="ai-message-content">
                {renderMessageText(message.text)}

                {/* Add chips for the welcome message */}
                {message.id === messages[0]?.id && (
                  <Box
                    className="chips-container"
                    sx={{ mt: 2, display: "flex", gap: 1 }}
                  >
                    <Chip
                      label="Jobs"
                      onClick={() => handleQuickOptionClick("Jobs")}
                      className="option-chip"
                    />
                    <Chip
                      label="Mentorship"
                      onClick={() => handleQuickOptionClick("Mentorship")}
                      className="option-chip"
                    />
                    <Chip
                      label="Community"
                      onClick={() => handleQuickOptionClick("Community")}
                      className="option-chip"
                    />
                  </Box>
                )}

                <Box className="message-footer">
                  <Box className="action-buttons">
                    <Tooltip title="Copy message">
                      <IconButton
                        size="small"
                        onClick={() => copyMessage(message.text)}
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Report issue">
                      <IconButton
                        size="small"
                        onClick={() => handleFeedback(message.id)}
                        className={
                          message.feedback === "negative" ? "active" : ""
                        }
                      >
                        <ThumbDownIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </Box>
            )}
          </Box>
        ))}

        {/* Loading message */}
        {isLoading && (
          <Box className="message-wrapper ai-message">
            <Box className="ai-message-content loading-message">
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <CircularProgress size={20} />
                <Typography variant="body1" className="loading-text">
                  <i>{getRandomLoadingMessage()}</i>
                  <span className="dots-loader">...</span>
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Message Input */}
      <Paper
        component="form"
        onSubmit={handleSubmit}
        className="input-container"
      >
        <TextField
          fullWidth
          value={input}
          onChange={handleInputChange}
          placeholder="How can I help with your goals today?"
          variant="outlined"
          multiline
          onKeyDown={handleKeyDown}
          inputRef={textFieldRef}
          slotProps={{
            input: {
              className: "rounded-input",
              style: {
                padding: "12px 16px",
                lineHeight: 1.5,
                resize: "none",
                minHeight: "24px",
                maxHeight: "150px",
                overflowY: "hidden", 
              },
            },
          }}
          disabled={isLoading}
        />
        
        {/* Speech-to-text button */}
        <Tooltip title={isListening ? "Stop listening" : "Speak your message"}>
          <IconButton
            onClick={toggleListening}
            disabled={isLoading || !speechSupported}
            className={`mic-button ${isListening ? 'listening' : ''}`}
            sx={{
              mr: 1,
              color: isListening ? '#e91e63' : 'grey.600',
              '&.listening': {
                animation: 'pulse 1.5s infinite'
              }
            }}
          >
            {isListening ? <MicIcon /> : <MicOffIcon />}
          </IconButton>
        </Tooltip>
        
        <Button
          type="submit"
          variant="contained"
          className="gradient-button rounded-button"
          disabled={!input.trim() || isLoading}
        >
          <SendIcon />
        </Button>
      </Paper>

      {/* Feedback Dialog */}
      <Dialog
        open={feedbackDialogOpen}
        onClose={() => setFeedbackDialogOpen(false)}
        aria-labelledby="feedback-dialog-title"
        maxWidth="md"
        fullWidth
        classes={{
          paper: "feedback-dialog",
        }}
      >
        <DialogTitle id="feedback-dialog-title">What went wrong?</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="feedback"
            label="Your feedback"
            type="text"
            fullWidth
            multiline
            rows={6}
            variant="outlined"
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            helperText={
              feedbackText.trim() === ""
                ? "Please provide some feedback before submitting"
                : ""
            }
            slotProps={{
              formHelperText: {
                sx: { color: 'text.secondary' }
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={submitFeedback}
            variant="contained"
            color="primary"
            disabled={!feedbackText.trim()}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>

      {/* Logout Confirmation Dialog */}
      <Dialog
        open={logoutDialogOpen}
        onClose={handleLogoutCancel}
        aria-labelledby="logout-dialog-title"
        maxWidth="sm"
      >
        <DialogTitle id="logout-dialog-title">Confirm Logout</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to logout? Your session will end and you will be redirected to the sign-in page.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleLogoutCancel}>Cancel</Button>
          <Button 
            onClick={handleLogoutConfirm} 
            variant="contained" 
            color="primary"
          >
            Logout
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upgrade Account Dialog for Guest Users */}
      <Dialog
        open={signupDialogOpen}
        onClose={() => setSignupDialogOpen(false)}
        aria-labelledby="upgrade-dialog-title"
        maxWidth="sm"
      >
        <DialogTitle id="upgrade-dialog-title" sx={{ 
          background: 'linear-gradient(90deg, #7c3aed 0%, #c026d3 100%)',
          color: 'white',
          pb: 3
        }}>
          Unlock Full Access to Disha AI
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>
              Create an account to access premium features:
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LockIcon color="primary" />
              <Typography>
                <strong>Smart Career Path Generator:</strong> Get a personalized career roadmap based on your skills and goals
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LockIcon color="primary" />
              <Typography>
                <strong>Personalized Job Matching:</strong> AI-powered job recommendations tailored to your profile
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LockIcon color="primary" />
              <Typography>
                <strong>Skill Gap Analysis:</strong> Identify key skills to develop for your dream role
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LockIcon color="primary" />
              <Typography>
                <strong>Progress Tracking:</strong> Save your career journey and track improvements
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setSignupDialogOpen(false)}>
            Continue as Guest
          </Button>
          <Button 
            onClick={handleUpgradeAccount} 
            variant="contained"
            sx={{
              background: 'linear-gradient(90deg, #7c3aed 0%, #c026d3 100%)',
              '&:hover': {
                background: 'linear-gradient(90deg, #6c2aed 0%, #a016b3 100%)',
              },
            }}
          >
            Create Account
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
}