import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CssBaseline, Toolbar } from '@mui/material';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Intake from './pages/Intake';

export default function App() {
  return (
    <BrowserRouter>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <Sidebar />
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<Home />} />
            <Route path="/intake" element={<Intake />} />
          </Routes>
        </Box>
      </Box>
    </BrowserRouter>
  );
}
