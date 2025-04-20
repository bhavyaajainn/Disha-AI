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
  
  /**
   * Dialog control states
   * Manage dialog visibility and related state
   */
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);
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
   * Initial setup
   * Get user ID and set welcome message
   */
  useEffect(() => {
    const getUserId = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          setUserId(user.id);
        }
      } catch (error) {
        console.error("Error getting user:", error);
      }
    };
    getUserId();  
    
    const name = searchParams.get("name");
    if (name?.trim()) {
      setMessages([
        {
          sender: "ai",
          text: `Hi ${name}, welcome! I'm Disha AI, here to guide your journey. How can I support you today?`,
          timestamp: new Date(),
          id: Date.now().toString(),
        },
      ]);
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
   * Event handlers for user interactions
   */
  const handleQuickOptionClick = (option: string) => {
    handleChipClick(
      option,
      setMessages,
      setIsLoading
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    await handleSubmitMessage(
      input,
      setMessages,
      setInput,
      setIsLoading,
      textFieldRef
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
      router
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
          <Box sx={{ flexGrow: 1 }} />
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