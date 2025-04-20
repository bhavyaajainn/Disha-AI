
import { AuthResponse, UserResponse } from '@/types';
import { createClient, SupabaseClient, AuthError, PostgrestError } from '@supabase/supabase-js';


const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string;


export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);


export const isAuthenticated = async (): Promise<AuthResponse> => {
  const { data, error } = await supabase.auth.getSession();
  return { 
    authenticated: !!data.session, 
    user: data.session?.user || null,
    error
  };
};


export const getCurrentUser = async (): Promise<UserResponse> => {
  const { data, error } = await supabase.auth.getUser();
  return { user: data.user, error };
};


export const signOut = async (): Promise<{ error: AuthError | null }> => {
  const { error } = await supabase.auth.signOut();
  return { error };
};


export interface UserProfile {
  id: string;
  name: string;
  email: string;
  created_at?: string;
  updated_at?: string;
}


export const saveUserProfile = async (profile: Omit<UserProfile, 'created_at' | 'updated_at'>): Promise<{ error: PostgrestError | null }> => {
  const { error } = await supabase
    .from('users')
    .insert([profile]);
  
  return { error };
};

export const getUserProfile = async (userId: string): Promise<{ data: UserProfile | null, error: PostgrestError | null }> => {
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('id', userId)
    .single();
  
  return { data, error };
};