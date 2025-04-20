'use client';

import { useEffect, useState} from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/supabaseClient';
import { Box, CircularProgress, Typography } from '@mui/material';
import { ProtectedRouteProps } from '@/types';

/**
 * Protected route component that restricts access to authenticated users only.
 * Redirects unauthenticated users to the home page and displays a loading
 * indicator while authentication check is in progress.
 */
export default function ProtectedRoute({ children }: Readonly<ProtectedRouteProps>) {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(true);

  /**
   * Authentication check effect
   * Verifies user authentication status on component mount and
   * redirects to home page if user is not authenticated
   */
  useEffect(() => {
    const checkAuth = async () => {
      const { authenticated } = await isAuthenticated();
      
      if (!authenticated) {
        router.push('/');
      } else {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  /**
   * Loading state renderer
   * Displays a centered loading spinner while authentication status is being checked
   */
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          background: 'linear-gradient(135deg, #2a0e60 0%, #451d98 50%, #6927c5 100%)',
        }}
      >
        <CircularProgress size={60} sx={{ color: 'white' }} />
        <Typography variant="h6" sx={{ mt: 4, color: 'white' }}>
          Loading...
        </Typography>
      </Box>
    );
  }

  // Render children only when user is authenticated
  return <>{children}</>;
}