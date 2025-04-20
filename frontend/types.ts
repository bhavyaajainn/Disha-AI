import { AuthError, User } from "@supabase/supabase-js";
import { ReactNode, ErrorInfo } from "react";

export interface ToastState {
  open: boolean;
  message: string;
  severity: "success" | "error" | "info" | "warning";
}

export interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

export interface Message {
  sender: "user" | "ai";
  text: string;
  timestamp: Date;
  id: string;
  feedback?: "negative";
}

export interface CustomErrorBoundaryProps {
  children: ReactNode;
}

export interface CustomErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}
export interface ProtectedRouteProps {
  children: ReactNode;
}

export interface AuthResponse {
  authenticated: boolean;
  user: User | null;
  error: AuthError | null;
}

export interface UserResponse {
  user: User | null;
  error: AuthError | null;
}