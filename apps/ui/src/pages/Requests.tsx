import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActionArea from '@mui/material/CardActionArea';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Divider from '@mui/material/Divider';

interface OrderLine {
  position_description: string;
  unit_price: number;
  amount: number;
  unit: string;
  total_price: number;
}

interface ProcurementRequest {
  requestor_name: string;
  title: string;
  vendor_name: string;
  vat_id: string;
  commodity_group: string;
  order_lines: OrderLine[];
  total_cost: number;
  department: string;
}

interface RequestData {
  id: string;
  created_at: string;
  status: string;
  request: ProcurementRequest;
}

const statusColors: Record<string, 'default' | 'warning' | 'success'> = {
  open: 'default',
  'in-progress': 'warning',
  closed: 'success',
};

export default function Requests() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [requests, setRequests] = useState<RequestData[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<RequestData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);

  const intakeApiUrl = import.meta.env.VITE_INTAKE_API_URL || 'http://localhost:8081';

  // Fetch all requests
  useEffect(() => {
    if (!id) {
      fetchAllRequests();
    }
  }, [id]);

  // Fetch single request
  useEffect(() => {
    if (id) {
      fetchRequestById(id);
    } else {
      setSelectedRequest(null);
    }
  }, [id]);

  const fetchAllRequests = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${intakeApiUrl}/intake/requests`);
      if (!response.ok) {
        throw new Error(`Failed to fetch requests: ${response.statusText}`);
      }
      const data = await response.json();
      setRequests(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch requests');
    } finally {
      setLoading(false);
    }
  };

  const fetchRequestById = async (requestId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${intakeApiUrl}/intake/requests/${requestId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch request: ${response.statusText}`);
      }
      const data = await response.json();
      setSelectedRequest(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch request');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedRequest) return;

    setStatusLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${intakeApiUrl}/intake/requests/${selectedRequest.id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update status: ${response.statusText}`);
      }

      const updatedData = await response.json();
      setSelectedRequest(updatedData);
      setSuccess('Status updated successfully!');

      // Trigger refresh of sidebar counter
      window.dispatchEvent(new CustomEvent('requestSubmitted'));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update status');
    } finally {
      setStatusLoading(false);
    }
  };

  const handleCardClick = (requestId: string) => {
    navigate(`/requests/${requestId}`);
  };

  const handleBackToList = () => {
    navigate('/requests');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  // List View
  if (!id) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Manage Requests
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            View and manage all procurement requests
          </Typography>

          <Snackbar
            open={!!error}
            autoHideDuration={6000}
            onClose={() => setError(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert severity="error" onClose={() => setError(null)} sx={{ width: '100%' }}>
              {error}
            </Alert>
          </Snackbar>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : requests.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography color="text.secondary">
                No requests found. Create your first request in the Intake page.
              </Typography>
            </Paper>
          ) : (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
              {requests.map((request) => (
                <Card key={request.id}>
                  <CardActionArea onClick={() => handleCardClick(request.id)}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="h6" component="div" sx={{ flex: 1 }}>
                          {request.request.title}
                        </Typography>
                        <Chip
                          label={request.status}
                          color={statusColors[request.status] || 'default'}
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {request.request.requestor_name} • {request.request.department}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Vendor: {request.request.vendor_name}
                      </Typography>
                      <Typography variant="h6" color="primary" sx={{ mt: 2 }}>
                        €{request.request.total_cost.toFixed(2)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                        Created: {formatDate(request.created_at)}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      </Container>
    );
  }

  // Detail View
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBackToList}
          sx={{ mb: 2 }}
        >
          Back to Requests
        </Button>

        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert severity="error" onClose={() => setError(null)} sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!success}
          autoHideDuration={6000}
          onClose={() => setSuccess(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert severity="success" onClose={() => setSuccess(null)} sx={{ width: '100%' }}>
            {success}
          </Alert>
        </Snackbar>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : selectedRequest ? (
          <Paper sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
              <Box>
                <Typography variant="h4" component="h1" gutterBottom>
                  {selectedRequest.request.title}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Request ID: {selectedRequest.id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Created: {formatDate(selectedRequest.created_at)}
                </Typography>
              </Box>
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={selectedRequest.status}
                  label="Status"
                  onChange={(e) => handleStatusChange(e.target.value)}
                  disabled={statusLoading}
                >
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="in-progress">In Progress</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  Requestor Information
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Name
                  </Typography>
                  <Typography variant="body1">
                    {selectedRequest.request.requestor_name}
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Department
                  </Typography>
                  <Typography variant="body1">
                    {selectedRequest.request.department}
                  </Typography>
                </Box>
              </Box>

              <Box>
                <Typography variant="h6" gutterBottom>
                  Vendor Information
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Vendor Name
                  </Typography>
                  <Typography variant="body1">
                    {selectedRequest.request.vendor_name}
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    VAT ID
                  </Typography>
                  <Typography variant="body1">
                    {selectedRequest.request.vat_id}
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Commodity Group
                  </Typography>
                  <Typography variant="body1">
                    {selectedRequest.request.commodity_group}
                  </Typography>
                </Box>
              </Box>
            </Box>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom>
              Order Lines
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Description</TableCell>
                    <TableCell align="right">Unit Price</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell align="right">Total Price</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {selectedRequest.request.order_lines.map((line, index) => (
                    <TableRow key={index}>
                      <TableCell>{line.position_description}</TableCell>
                      <TableCell align="right">€{line.unit_price.toFixed(2)}</TableCell>
                      <TableCell align="right">{line.amount}</TableCell>
                      <TableCell>{line.unit}</TableCell>
                      <TableCell align="right">€{line.total_price.toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
              <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
                <Typography variant="h5">
                  Total Cost: €{selectedRequest.request.total_cost.toFixed(2)}
                </Typography>
              </Paper>
            </Box>
          </Paper>
        ) : (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="text.secondary">
              Request not found
            </Typography>
          </Paper>
        )}
      </Box>
    </Container>
  );
}
