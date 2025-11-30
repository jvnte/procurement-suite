import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';

const drawerWidth = 240;

export default function Topbar() {
  return (
    <AppBar
      position="fixed"
      sx={{
        width: { sm: `calc(100% - ${drawerWidth}px)` },
        ml: { sm: `${drawerWidth}px` },
      }}
    >
      <Toolbar>
      </Toolbar>
    </AppBar>
  );
}
