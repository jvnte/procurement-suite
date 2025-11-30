import { useState, useEffect, useCallback } from 'react';
import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Typography, Chip } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import DescriptionIcon from '@mui/icons-material/Description';
import ListAltIcon from '@mui/icons-material/ListAlt';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const menuItems = [
  { text: 'Home', icon: <HomeIcon />, path: '/home' },
  { text: 'Intake', icon: <DescriptionIcon />, path: '/intake' },
  { text: 'Requests', icon: <ListAltIcon />, path: '/requests' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [openRequestsCount, setOpenRequestsCount] = useState<number>(0);

  const fetchOpenRequests = useCallback(async () => {
    try {
      const intakeApiUrl = import.meta.env.VITE_INTAKE_API_URL || 'http://localhost:8081';
      const response = await fetch(`${intakeApiUrl}/intake/requests`);
      if (response.ok) {
        const data = await response.json();
        const openCount = data.filter((req: any) => req.status === 'open').length;
        setOpenRequestsCount(openCount);
      }
    } catch (error) {
      // Silently fail - counter will show 0
      console.error('Failed to fetch open requests count:', error);
    }
  }, []);

  useEffect(() => {
    fetchOpenRequests();
    // Refresh count every 30 seconds
    const interval = setInterval(fetchOpenRequests, 30000);

    // Listen for request submission events
    const handleRequestSubmitted = () => {
      fetchOpenRequests();
    };
    window.addEventListener('requestSubmitted', handleRequestSubmitted);

    return () => {
      clearInterval(interval);
      window.removeEventListener('requestSubmitted', handleRequestSubmitted);
    };
  }, [fetchOpenRequests]);

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar
        sx={{
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          boxShadow: 4
        }}
      >
        <Typography variant="h6" noWrap component="div">
          Procurement Suite
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
              {item.text === 'Requests' && (
                <Chip
                  label={openRequestsCount}
                  size="small"
                  sx={{
                    bgcolor: openRequestsCount > 0 ? 'error.main' : 'grey.400',
                    color: 'white',
                    fontWeight: 'bold',
                    minWidth: 32,
                  }}
                />
              )}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}
