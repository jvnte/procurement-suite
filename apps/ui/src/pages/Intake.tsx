import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';

export default function Intake() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Intake
        </Typography>
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="body1">
            Intake page content goes here.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}
