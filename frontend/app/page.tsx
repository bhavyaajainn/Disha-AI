"use client";

import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Tabs,
  Tab,
  InputAdornment,
  IconButton,
  FormControlLabel,
  Checkbox,
  Snackbar,
  Alert,
} from "@mui/material";
import Image from "next/image";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { ThemeProvider } from "@mui/material/styles";
import theme from "./theme/theme";
import "./style/page.scss";
import { supabase } from "./utils/config";
import { FormErrors, ToastState } from "@/types";
import { LandingPageBackground } from "../components/LandingPageBackground";
import CustomErrorBoundary from "../components/ErrorBoundary";
import {
  validateSignUpForm,
  validateSignInForm,
  handleSessionCheck,
  handleUserSignUp,
  handleUserSignIn,
} from "./utils/helper";

/**
 * Home component containing the main landing page UI with authentication forms
 */
function Home() {
  const [displayText, setDisplayText] = useState<string>("");
  const [isTypingComplete, setIsTypingComplete] = useState<boolean>(false);
  const fullTaglineText = "Lead at every step with smart support.";
  const router = useRouter();

  // Auth related states
  const [tabValue, setTabValue] = useState<number>(0);
  const [name, setName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [keepSignedIn, setKeepSignedIn] = useState<boolean>(false);
  const [formErrors, setFormErrors] = useState<FormErrors>({});

  // Toast notification state
  const [toast, setToast] = useState<ToastState>({
    open: false,
    message: "",
    severity: "info",
  });

  // Password visibility states
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState<boolean>(false);
  const [showSignInPassword, setShowSignInPassword] = useState<boolean>(false);

  /**
   * Check for stored session on component mount and redirect if authenticated
   */
  useEffect(() => {
    handleSessionCheck(router, supabase);
  }, [router]);

  /**
   * Typing animation effect for the tagline
   */
  useEffect(() => {
    setDisplayText("");
    let currentIndex = 0;
    const typingInterval = setInterval(() => {
      if (currentIndex < fullTaglineText.length) {
        setDisplayText(() => fullTaglineText.substring(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(typingInterval);
        setIsTypingComplete(true);
      }
    }, 70);

    return () => clearInterval(typingInterval);
  }, []);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setName("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");
    setFormErrors({});
    handleCloseToast();
  };

  const handleCloseToast = () => {
    setToast({ ...toast, open: false });
  };

  const showToast = (
    message: string,
    severity: "success" | "error" | "info" | "warning"
  ) => {
    setToast({
      open: true,
      message,
      severity,
    });
  };

  /**
   * Form submission handlers
   */
  const handleSignUp = async (e: FormEvent) => {
    e.preventDefault();

    if (
      !validateSignUpForm(name, email, password, confirmPassword, setFormErrors)
    ) {
      return;
    }

    setLoading(true);

    try {
      const success = await handleUserSignUp(
        supabase,
        name.trim(),
        email.trim(),
        password.trim()
      );

      if (success) {
        showToast(
          "Signup successful! Please verify your email to proceed.",
          "success"
        );
        setTabValue(0);
        setName("");
        setEmail("");
        setPassword("");
        setConfirmPassword("");
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        showToast(err.message, "error");
      } else {
        showToast("Signup failed. Please try again.", "error");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSignIn = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateSignInForm(email, password, setFormErrors)) {
      return;
    }
    const currentEmail = email.trim();
    const currentPassword = password.trim();
    const currentKeepSignedIn = keepSignedIn;
    setEmail("");
    setPassword("");

    setLoading(true);

    try {
      const result = await handleUserSignIn(
        supabase,
        currentEmail,
        currentPassword,
        currentKeepSignedIn
      );

      if (result.success) {
        showToast("Sign in successful! Redirecting...", "success");
        setTimeout(() => {
          router.push(`/chat?name=${encodeURIComponent(result.displayName)}`);
        }, 1000);
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        showToast(error.message, "error");
      } else {
        showToast("An error occurred during sign in", "error");
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Password visibility toggle handlers
   */
  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleToggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const handleToggleSignInPasswordVisibility = () => {
    setShowSignInPassword(!showSignInPassword);
  };

  return (
    <Container className="landing-page">
      <LandingPageBackground />
      {/* Toast Notification */}
      <Snackbar
        open={toast.open}
        autoHideDuration={6000}
        onClose={handleCloseToast}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseToast}
          severity={toast.severity}
          variant="filled"
          sx={{ width: "100%" }}
        >
          {toast.message}
        </Alert>
      </Snackbar>

      <div className="content-wrapper">
        <Paper elevation={3} className="welcome-card">
          <div className="content-wrapper">
            {/* Text Content */}
            <div className="text-content">
              <Typography variant="h3" component="h1" className="title">
                DISHA AI
              </Typography>
              <div className="tagline-wrapper">
                {/* Hidden full text to establish width */}
                <Typography className="hidden-tagline" aria-hidden="true">
                  {fullTaglineText}
                </Typography>

                {/* Visible animated text */}
                <Typography className="tagline animated-tagline">
                  {displayText}
                  {!isTypingComplete && (
                    <span className="typing-cursor">|</span>
                  )}
                </Typography>
              </div>
            </div>

            {/* Image Content */}
            <div className="image-container">
              <Image
                src="/women-with-wings.png"
                alt="Woman with wings"
                className="responsive-image"
                width={150} // Specify the width
                height={150} // Specify the height
                priority // Ensures the image is loaded quickly
              />
            </div>
          </div>

          {/* Authentication Section - Directly integrated in main page */}
          <Box className="auth-section">
            <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                aria-label="auth tabs"
                sx={{
                  "& .MuiTab-root": { color: "rgba(255, 255, 255, 0.7)" },
                  "& .Mui-selected": { color: "white" },
                  "& .MuiTabs-indicator": { backgroundColor: "white" },
                }}
              >
                <Tab label="Sign In" />
                <Tab label="Sign Up" />
              </Tabs>
            </Box>

            {/* Sign In Form */}
            {tabValue === 0 && (
              <Box component="form" onSubmit={handleSignIn} sx={{ mt: 2 }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email-signin"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={!!formErrors.email}
                  helperText={formErrors.email}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      color: "white",
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" },
                      "&:hover fieldset": { borderColor: "white" },
                      "&.Mui-focused fieldset": { borderColor: "white" },
                    },
                    "& .MuiInputLabel-root": {
                      color: "rgba(255, 255, 255, 0.7)",
                    },
                    "& .MuiInputLabel-root.Mui-focused": { color: "white" },
                    "& .MuiFormHelperText-root": {
                      color: "#f44336",
                    },
                  }}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type={showSignInPassword ? "text" : "password"}
                  id="password-signin"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  error={!!formErrors.password}
                  helperText={formErrors.password}
                  slotProps={{
                    input: {
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label="toggle password visibility"
                            onClick={handleToggleSignInPasswordVisibility}
                            edge="end"
                            sx={{ color: "rgba(255, 255, 255, 0.7)" }}
                          >
                            {showSignInPassword ? (
                              <VisibilityOffIcon />
                            ) : (
                              <VisibilityIcon />
                            )}
                          </IconButton>
                        </InputAdornment>
                      ),
                    },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      color: "white",
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" },
                      "&:hover fieldset": { borderColor: "white" },
                      "&.Mui-focused fieldset": { borderColor: "white" },
                    },
                    "& .MuiInputLabel-root": {
                      color: "rgba(255, 255, 255, 0.7)",
                    },
                    "& .MuiInputLabel-root.Mui-focused": { color: "white" },
                    "& .MuiFormHelperText-root": {
                      color: "#f44336",
                    },
                  }}
                />

                {/* Keep me signed in checkbox - only shown on sign in form */}
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={keepSignedIn}
                      onChange={(e) => setKeepSignedIn(e.target.checked)}
                      sx={{
                        color: "rgba(255, 255, 255, 0.7)",
                        "&.Mui-checked": {
                          color: "white",
                        },
                      }}
                    />
                  }
                  label="Keep me signed in"
                  sx={{
                    mt: 1,
                    color: "rgba(255, 255, 255, 0.9)",
                    "& .MuiFormControlLabel-label": {
                      fontSize: "0.875rem",
                    },
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  sx={{
                    mt: 2,
                    mb: 2,
                    background:
                      "linear-gradient(90deg, #7c3aed 0%, #c026d3 100%)",
                    "&:hover": {
                      background:
                        "linear-gradient(90deg, #6c2aed 0%, #a016b3 100%)",
                    },
                  }}
                  disabled={loading}
                >
                  {loading ? "Signing in..." : "Sign In"}
                </Button>
              </Box>
            )}

            {/* Sign Up Form */}
            {tabValue === 1 && (
              <Box component="form" onSubmit={handleSignUp} sx={{ mt: 2 }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="name-signup"
                  label="Your Name"
                  name="name"
                  autoComplete="name"
                  autoFocus
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  error={!!formErrors.name}
                  helperText={formErrors.name}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      color: "white",
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" },
                      "&:hover fieldset": { borderColor: "white" },
                      "&.Mui-focused fieldset": { borderColor: "white" },
                    },
                    "& .MuiInputLabel-root": {
                      color: "rgba(255, 255, 255, 0.7)",
                    },
                    "& .MuiInputLabel-root.Mui-focused": { color: "white" },
                    "& .MuiFormHelperText-root": {
                      color: "#f44336",
                    },
                  }}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email-signup"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={!!formErrors.email}
                  helperText={formErrors.email}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      color: "white",
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" },
                      "&:hover fieldset": { borderColor: "white" },
                      "&.Mui-focused fieldset": { borderColor: "white" },
                    },
                    "& .MuiInputLabel-root": {
                      color: "rgba(255, 255, 255, 0.7)",
                    },
                    "& .MuiInputLabel-root.Mui-focused": { color: "white" },
                    "& .MuiFormHelperText-root": {
                      color: "#f44336",
                    },
                  }}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type={showPassword ? "text" : "password"}
                  id="password-signup"
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  error={!!formErrors.password}
                  helperText={formErrors.password}
                  slotProps={{
                    input: {
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label="toggle password visibility"
                            onClick={handleTogglePasswordVisibility}
                            edge="end"
                            sx={{ color: "rgba(255, 255, 255, 0.7)" }}
                          >
                            {showPassword ? (
                              <VisibilityOffIcon />
                            ) : (
                              <VisibilityIcon />
                            )}
                          </IconButton>
                        </InputAdornment>
                      ),
                    },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      color: "white",
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" },
                      "&:hover fieldset": { borderColor: "white" },
                      "&.Mui-focused fieldset": { borderColor: "white" },
                    },
                    "& .MuiInputLabel-root": {
                      color: "rgba(255, 255, 255, 0.7)",
                    },
                    "& .MuiInputLabel-root.Mui-focused": { color: "white" },
                    "& .MuiFormHelperText-root": {
                      color: "#f44336",
                    },
                  }}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="confirm-password"
                  label="Confirm Password"
                  type={showConfirmPassword ? "text" : "password"}
                  id="confirm-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  error={!!formErrors.confirmPassword}
                  helperText={formErrors.confirmPassword}
                  slotProps={{
                    input: {
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label="toggle confirm password visibility"
                            onClick={handleToggleConfirmPasswordVisibility}
                            edge="end"
                            sx={{ color: "rgba(255, 255, 255, 0.7)" }}
                          >
                            {showConfirmPassword ? (
                              <VisibilityOffIcon />
                            ) : (
                              <VisibilityIcon />
                            )}
                          </IconButton>
                        </InputAdornment>
                      ),
                    },
                  }}
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      color: "white",
                      "& fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" },
                      "&:hover fieldset": { borderColor: "white" },
                      "&.Mui-focused fieldset": { borderColor: "white" },
                    },
                    "& .MuiInputLabel-root": {
                      color: "rgba(255, 255, 255, 0.7)",
                    },
                    "& .MuiInputLabel-root.Mui-focused": { color: "white" },
                    "& .MuiFormHelperText-root": {
                      color: "#f44336",
                    },
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  color="primary"
                  sx={{
                    mt: 3,
                    mb: 2,
                    background:
                      "linear-gradient(90deg, #7c3aed 0%, #c026d3 100%)",
                    "&:hover": {
                      background:
                        "linear-gradient(90deg, #6c2aed 0%, #a016b3 100%)",
                    },
                  }}
                  disabled={loading}
                >
                  {loading ? "Creating account..." : "Create Account"}
                </Button>
              </Box>
            )}
          </Box>
        </Paper>
      </div>
    </Container>
  );
}

/**
 * Main application component wrapped with theme provider and error boundary
 */
function App() {
  return (
    <CustomErrorBoundary>
      <ThemeProvider theme={theme}>
        <Home />
      </ThemeProvider>
    </CustomErrorBoundary>
  );
}

export default App;
