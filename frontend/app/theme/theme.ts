import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  typography: {
    fontFamily: 'DM Sans',
  },
  components: {
    MuiContainer: {
      styleOverrides: {
        root: {
          maxWidth: 'none !important',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: 'none', 
        },
      },
    },
  },
});

export default theme;