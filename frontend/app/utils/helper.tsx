import { Dispatch, SetStateAction } from "react";
import { SupabaseClient } from "@supabase/supabase-js";
import { FormErrors } from "@/types";
import { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";

/**
 * Validates email format using regex
 */
export const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

/**
 * Validates password strength - requires at least 8 chars, 1 letter, and 1 number
 */
export const validatePassword = (password: string): boolean => {
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  return password.length >= 8 && hasLetter && hasNumber;
};

/**
 * Validates sign up form and sets appropriate error messages
 */
export const validateSignUpForm = (
  name: string,
  email: string,
  password: string,
  confirmPassword: string,
  setFormErrors: Dispatch<SetStateAction<FormErrors>>
): boolean => {
  const errors: FormErrors = {};

  if (!name.trim()) {
    errors.name = "Name is required";
  }

  if (!email.trim()) {
    errors.email = "Email is required";
  } else if (!validateEmail(email)) {
    errors.email = "Please enter a valid email address";
  }

  if (!password) {
    errors.password = "Password is required";
  } else if (!validatePassword(password)) {
    errors.password = "Password must be at least 8 characters with a number and a letter";
  }

  if (password !== confirmPassword) {
    errors.confirmPassword = "Passwords don't match";
  }

  setFormErrors(errors);
  return Object.keys(errors).length === 0;
};

/**
 * Validates sign in form and sets appropriate error messages
 */
export const validateSignInForm = (
  email: string,
  password: string,
  setFormErrors: Dispatch<SetStateAction<FormErrors>>
): boolean => {
  const errors: FormErrors = {};

  if (!email.trim()) {
    errors.email = "Email is required";
  } else if (!validateEmail(email)) {
    errors.email = "Please enter a valid email address";
  }

  if (!password) {
    errors.password = "Password is required";
  }

  setFormErrors(errors);
  return Object.keys(errors).length === 0;
};

/**
 * Checks for stored session and redirects if authenticated
 */
export const handleSessionCheck = async (
  router: AppRouterInstance,
  supabase: SupabaseClient
): Promise<void> => {
  try {
    const keepSignedInPref = localStorage.getItem("dishaKeepSignedIn");
    if (keepSignedInPref === "true") {
      const { data: { session }, error } = await supabase.auth.getSession();
      if (session && !error) {
        const displayName = session.user.user_metadata?.display_name;
        if (!displayName) {
          const { data: userData } = await supabase
            .from("users")
            .select("name")
            .eq("id", session.user.id)
            .maybeSingle();
          const userName = userData?.name ?? "User";
          router.push(`/chat?name=${encodeURIComponent(userName)}`);
        } else {
          router.push(`/chat?name=${encodeURIComponent(displayName)}`);
        }
      } else if (error) {
        localStorage.removeItem("dishaKeepSignedIn");
        console.error("Session error:", error);
      }
    }
  } catch (error) {
    console.error("Error checking stored session:", error);
    localStorage.removeItem("dishaKeepSignedIn");
  }
};

/**
 * Handles user signup process
 */
export const handleUserSignUp = async (
  supabase: SupabaseClient,
  name: string,
  email: string,
  password: string
): Promise<boolean> => {
  const { error } = await supabase.auth.signUp({
    email: email,
    password: password,
    options: {
      emailRedirectTo: `${window.location.origin}/chat`,
      data: { display_name: name },
    },
  });

  if (error) throw error;
  return true;
};

/**
 * Handles user signin process and returns display name for redirect
 */
export const handleUserSignIn = async (
  supabase: SupabaseClient,
  email: string,
  password: string,
  keepSignedIn: boolean
): Promise<{ success: boolean; displayName: string }> => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email,
    password: password,
  });

  if (error) throw error;

  if (keepSignedIn) {
    localStorage.setItem("dishaKeepSignedIn", "true");
  } else {
    localStorage.removeItem("dishaKeepSignedIn");
  }

  let displayName = "User";
  
  if (data.user) {
    if (data.user.user_metadata?.display_name) {
      displayName = data.user.user_metadata.display_name;
    } else {
      const { data: userData, error: userError } = await supabase
        .from("users")
        .select("name")
        .eq("id", data.user.id)
        .maybeSingle();

      if (!userError || userError.code === "PGRST116") {
        displayName = userData?.name ?? "User";
      }
    }
  }

  return { success: true, displayName };
};