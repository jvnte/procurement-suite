import { useNavigate } from 'react-router-dom';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActionArea from '@mui/material/CardActionArea';
import Box from '@mui/material/Box';
import DescriptionIcon from '@mui/icons-material/Description';
import ListAltIcon from '@mui/icons-material/ListAlt';

export default function Home() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome!
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Select an option below to get started.
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
          <Card sx={{ height: '100%' }}>
            <CardActionArea onClick={() => navigate('/intake')} sx={{ height: '100%' }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <DescriptionIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Typography variant="h5" component="h2">
                    Intake
                  </Typography>
                </Box>
                <Typography variant="body1" color="text.secondary">
                  Create new procurement requests by uploading PDF documents or filling out the form manually.
                  The system will automatically extract information from uploaded documents and pre-fill the request form.
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>

          <Card sx={{ height: '100%' }}>
            <CardActionArea onClick={() => navigate('/requests')} sx={{ height: '100%' }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ListAltIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Typography variant="h5" component="h2">
                    Requests
                  </Typography>
                </Box>
                <Typography variant="body1" color="text.secondary">
                  View and manage all procurement requests. Browse through submitted requests, view detailed information,
                  and update request statuses (open, in-progress, closed).
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Box>
      </Box>
    </Container>
  );
}
