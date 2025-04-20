import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
} from '@mui/material';
import Image from 'next/image';
import RefreshIcon from '@mui/icons-material/Refresh';
import { CustomErrorBoundaryProps, CustomErrorBoundaryState } from '@/types';

/**
 * Error boundary component that catches JavaScript errors in child components,
 * logs them, and displays a user-friendly fallback UI instead of crashing
 * the entire application.
 */
class CustomErrorBoundary extends Component<CustomErrorBoundaryProps, CustomErrorBoundaryState> {
  constructor(props: CustomErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<CustomErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Error caught by CustomErrorBoundary:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  handleRefreshPage = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <Container 
          maxWidth={false} 
          disableGutters
          sx={{ 
            height: '100vh', 
            width: '100vw',
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #140d34 0%, #27104c 50%, #1f0e42 100%)',
            overflow: 'hidden',
            position: 'relative'
          }}
        >
          <Box 
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              overflow: 'hidden',
              zIndex: 0,
              opacity: 0.4
            }}
          >
            <Box 
              sx={{
                position: 'absolute',
                top: '10%',
                left: '5%',
                width: '30%',
                height: '30%',
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(194,6,211,0.4) 0%, rgba(255,255,255,0) 70%)',
                filter: 'blur(40px)'
              }}
            />
            <Box 
              sx={{
                position: 'absolute',
                bottom: '15%',
                right: '10%',
                width: '40%',
                height: '40%',
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(124,58,237,0.4) 0%, rgba(255,255,255,0) 70%)',
                filter: 'blur(50px)'
              }}
            />
            <Box 
              sx={{
                position: 'absolute',
                top: '50%',
                left: '60%',
                width: '20%',
                height: '20%',
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(238,130,238,0.2) 0%, rgba(255,255,255,0) 70%)',
                filter: 'blur(30px)'
              }}
            />
          </Box>

          <Paper 
            elevation={24} 
            sx={{ 
              p: 5, 
              textAlign: 'center',
              background: 'rgba(0, 0, 0, 0.5)',
              backdropFilter: 'blur(10px)',
              color: 'white',
              borderRadius: 4,
              width: { xs: '90%', sm: '450px' },
              border: '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
              zIndex: 1,
              position: 'relative'
            }}
          >
            <Box sx={{ mb: 4 }}>
              <Image 
                src="/women-with-wings.png" 
                alt="Disha AI" 
                width={120} 
                height={120} 
                style={{ 
                  marginBottom: '1rem',
                  height: 'auto'
                }} 
              />
            </Box>
            
            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom
              sx={{ 
                fontWeight: 300,
                letterSpacing: '0.5px',
                fontSize: { xs: '1.75rem', sm: '2.25rem' },
                background: 'linear-gradient(90deg, #e5b2ca 0%, #c1bbeb 100%)',
                backgroundClip: 'text',
                textFillColor: 'transparent',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2
              }}
            >
              Oops! Something went wrong
            </Typography>
            
            <Typography 
              variant="body1" 
              sx={{ 
                mb: 5, 
                opacity: 0.9,
                maxWidth: '400px',
                margin: '0 auto 3rem auto',
                fontSize: '1.1rem',
                lineHeight: 1.5
              }}
            >
              Disha AI encountered an unexpected error. Don&apos;t worry, we&apos;ll get you back on track.
            </Typography>
            
            <Button 
              variant="contained" 
              onClick={this.handleRefreshPage}
              startIcon={<RefreshIcon />}
              size="large"
              sx={{
                background: 'linear-gradient(90deg, #c026d3 0%, #7c3aed 100%)',
                '&:hover': {
                  background: 'linear-gradient(90deg, #d136e3 0%, #8c4afd 100%)',
                },
                px: 4,
                py: 1.5,
                fontSize: '1rem',
                borderRadius: '30px',
                textTransform: 'none',
                fontWeight: 500,
                boxShadow: '0 4px 20px rgba(124, 58, 237, 0.5)'
              }}
            >
              Try Again
            </Button>
          </Paper>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default CustomErrorBoundary;