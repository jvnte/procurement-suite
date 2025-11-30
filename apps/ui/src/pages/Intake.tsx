import { useState } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import Collapse from '@mui/material/Collapse';
import CircularProgress from '@mui/material/CircularProgress';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SendIcon from '@mui/icons-material/Send';
import ClearIcon from '@mui/icons-material/Clear';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import IconButton from '@mui/material/IconButton';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface OrderLine {
  position_description: string;
  unit_price: number;
  amount: number;
  unit: string;
  total_price: number;
}

interface ProcurementRequestData {
  requestor_name: string;
  title: string;
  vendor_name: string;
  vat_id: string;
  commodity_group: string;
  order_lines: OrderLine[];
  total_cost: number;
  department: string;
}

export default function Intake() {
  const [formData, setFormData] = useState<ProcurementRequestData>({
    requestor_name: '',
    title: '',
    vendor_name: '',
    vat_id: '',
    commodity_group: '',
    order_lines: [{
      position_description: '',
      unit_price: 0,
      amount: 0,
      unit: '',
      total_price: 0,
    }],
    total_cost: 0,
    department: '',
  });
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [numPages, setNumPages] = useState<number>(0);
  const [isPdfExpanded, setIsPdfExpanded] = useState(true);

  const handleInputChange = (field: keyof Omit<ProcurementRequestData, 'order_lines' | 'total_cost'>) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleOrderLineChange = (index: number, field: keyof OrderLine, value: string | number) => {
    const newOrderLines = [...formData.order_lines];
    newOrderLines[index] = {
      ...newOrderLines[index],
      [field]: value,
    };

    // Auto-calculate total_price for this line
    if (field === 'unit_price' || field === 'amount') {
      newOrderLines[index].total_price = newOrderLines[index].unit_price * newOrderLines[index].amount;
    }

    // Calculate total_cost from all order lines
    const total_cost = newOrderLines.reduce((sum, line) => sum + line.total_price, 0);

    setFormData((prev) => ({
      ...prev,
      order_lines: newOrderLines,
      total_cost,
    }));
  };

  const addOrderLine = () => {
    setFormData((prev) => ({
      ...prev,
      order_lines: [
        ...prev.order_lines,
        {
          position_description: '',
          unit_price: 0,
          amount: 0,
          unit: '',
          total_price: 0,
        },
      ],
    }));
  };

  const removeOrderLine = (index: number) => {
    if (formData.order_lines.length === 1) return; // Keep at least one line

    const newOrderLines = formData.order_lines.filter((_, i) => i !== index);
    const total_cost = newOrderLines.reduce((sum, line) => sum + line.total_price, 0);

    setFormData((prev) => ({
      ...prev,
      order_lines: newOrderLines,
      total_cost,
    }));
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);
    setUploadLoading(true);
    setError(null);
    setSuccess(null);

    // Create blob URL for PDF viewer
    const url = URL.createObjectURL(file);
    setPdfUrl(url);

    try {
      const formDataUpload = new FormData();
      formDataUpload.append('file', file);

      const agentApiUrl = import.meta.env.VITE_AGENT_API_URL || 'http://localhost:8082';
      const response = await fetch(`${agentApiUrl}/agent/intake`, {
        method: 'POST',
        body: formDataUpload,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Calculate total_cost from order_lines
      const total_cost = (data.order_lines || []).reduce((sum: number, line: OrderLine) => sum + line.total_price, 0);

      // Prefill form with response data
      setFormData({
        requestor_name: data.requestor_name || '',
        title: data.title || '',
        vendor_name: data.vendor_name || '',
        vat_id: data.vat_id || '',
        commodity_group: data.commodity_group || '',
        order_lines: data.order_lines && data.order_lines.length > 0 ? data.order_lines : [{
          position_description: '',
          unit_price: 0,
          amount: 0,
          unit: '',
          total_price: 0,
        }],
        total_cost: data.total_cost || total_cost || 0,
        department: data.department || '',
      });

      setSuccess('Document processed successfully! Form fields have been pre-filled.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process document');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleRemoveFile = () => {
    // Revoke the blob URL to free memory
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
      setPdfUrl(null);
    }
    setUploadedFile(null);
    setNumPages(0);
    setError(null);
    setSuccess(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const intakeApiUrl = import.meta.env.VITE_INTAKE_API_URL || 'http://localhost:8081';
      const response = await fetch(`${intakeApiUrl}/intake/procurement_request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`Submission failed: ${response.statusText}`);
      }

      await response.json();
      setSuccess('Procurement request submitted successfully!');

      // Reset form
      setFormData({
        requestor_name: '',
        title: '',
        vendor_name: '',
        vat_id: '',
        commodity_group: '',
        order_lines: [{
          position_description: '',
          unit_price: 0,
          amount: 0,
          unit: '',
          total_price: 0,
        }],
        total_cost: 0,
        department: '',
      });

      // Clean up PDF
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
        setPdfUrl(null);
      }
      setUploadedFile(null);
      setNumPages(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit procurement request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Create Procurement Request
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

        <Box sx={{ display: 'flex', gap: 3, mt: 3, flexDirection: { xs: 'column', md: 'row' } }}>
          {/* Left Column - Form */}
          <Paper sx={{ p: 3, flex: 1 }}>
            <Typography variant="h6" gutterBottom>
              Procurement Request Form
            </Typography>

            <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={3}>
              <Typography variant="h6" gutterBottom>
                Requestor Information
              </Typography>

              <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', sm: 'row' } }}>
                <TextField
                  fullWidth
                  label="Requestor Name"
                  value={formData.requestor_name}
                  onChange={handleInputChange('requestor_name')}
                  required
                />
                <TextField
                  fullWidth
                  label="Department"
                  value={formData.department}
                  onChange={handleInputChange('department')}
                  required
                />
              </Box>

              <TextField
                fullWidth
                label="Request Title"
                value={formData.title}
                onChange={handleInputChange('title')}
                required
              />

              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Vendor Information
              </Typography>

              <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', sm: 'row' } }}>
                <TextField
                  fullWidth
                  label="Vendor Name"
                  value={formData.vendor_name}
                  onChange={handleInputChange('vendor_name')}
                  required
                />
                <TextField
                  fullWidth
                  label="VAT ID"
                  value={formData.vat_id}
                  onChange={handleInputChange('vat_id')}
                  required
                />
              </Box>

              <TextField
                fullWidth
                label="Commodity Group"
                value={formData.commodity_group}
                onChange={handleInputChange('commodity_group')}
                required
                placeholder="e.g., IT Services, Office Supplies"
              />

              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Order Lines
              </Typography>

              {formData.order_lines.map((line, index) => (
                <Paper key={index} sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle2">Line {index + 1}</Typography>
                    {formData.order_lines.length > 1 && (
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => removeOrderLine(index)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    )}
                  </Box>

                  <Stack spacing={2}>
                    <TextField
                      fullWidth
                      label="Position Description"
                      value={line.position_description}
                      onChange={(e) => handleOrderLineChange(index, 'position_description', e.target.value)}
                      required
                    />

                    <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
                      <TextField
                        fullWidth
                        label="Unit Price"
                        type="number"
                        value={line.unit_price || ''}
                        onChange={(e) => handleOrderLineChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                        required
                        inputProps={{ min: 0, step: 0.01 }}
                      />
                      <TextField
                        fullWidth
                        label="Amount"
                        type="number"
                        value={line.amount || ''}
                        onChange={(e) => handleOrderLineChange(index, 'amount', parseInt(e.target.value) || 0)}
                        required
                        inputProps={{ min: 0 }}
                      />
                      <TextField
                        fullWidth
                        label="Unit"
                        value={line.unit}
                        onChange={(e) => handleOrderLineChange(index, 'unit', e.target.value)}
                        required
                        placeholder="e.g., pieces, hours"
                      />
                    </Box>

                    <TextField
                      fullWidth
                      label="Total Price"
                      type="number"
                      value={line.total_price.toFixed(2)}
                      InputProps={{ readOnly: true }}
                      helperText="Auto-calculated from Unit Price × Amount"
                    />
                  </Stack>
                </Paper>
              ))}

              <Box>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={addOrderLine}
                >
                  Add Order Line
                </Button>
              </Box>

              <Box sx={{ bgcolor: 'primary.50', p: 2, borderRadius: 1 }}>
                <Typography variant="h6">
                  Total Cost: €{formData.total_cost.toFixed(2)}
                </Typography>
              </Box>

              <Box>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                  disabled={loading}
                >
                  Submit Procurement Request
                </Button>
              </Box>
            </Stack>
            </Box>
          </Paper>

          {/* Right Column - PDF Viewer */}
          <Box sx={{ width: { xs: '100%', md: '45%' }, position: { md: 'sticky' }, top: { md: 20 }, alignSelf: 'flex-start' }}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Document Upload
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload a PDF to auto-fill the form fields.
              </Typography>

              <Box>
                {!uploadedFile ? (
                  <Button
                    component="label"
                    variant="outlined"
                    startIcon={uploadLoading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
                    disabled={uploadLoading}
                    fullWidth
                  >
                    Upload PDF Document
                    <input
                      type="file"
                      hidden
                      accept=".pdf"
                      onChange={handleFileUpload}
                    />
                  </Button>
                ) : (
                  <Stack spacing={2}>
                    <Paper
                      sx={{
                        p: 2,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        bgcolor: 'success.50',
                        border: 1,
                        borderColor: 'success.200',
                        flexWrap: { xs: 'wrap', sm: 'nowrap' }
                      }}
                    >
                      <PictureAsPdfIcon sx={{ fontSize: { xs: 32, sm: 40 }, color: 'error.main', flexShrink: 0 }} />
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          variant="subtitle1"
                          fontWeight="medium"
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {uploadedFile.name}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ fontSize: { xs: '0.75rem', sm: '0.875rem' } }}
                        >
                          {(uploadedFile.size / 1024).toFixed(2)} KB • {numPages > 0 ? `${numPages} pages` : 'PDF'}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5, flexShrink: 0 }}>
                        {pdfUrl && (
                          <IconButton
                            size="small"
                            onClick={() => setIsPdfExpanded(!isPdfExpanded)}
                          >
                            {isPdfExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        )}
                        {!uploadLoading && (
                          <IconButton
                            size="small"
                            color="error"
                            onClick={handleRemoveFile}
                          >
                            <ClearIcon />
                          </IconButton>
                        )}
                        {uploadLoading && <CircularProgress size={24} />}
                      </Box>
                    </Paper>

                    {pdfUrl && (
                      <Collapse in={isPdfExpanded}>
                        <Paper
                          sx={{
                            maxHeight: 'calc(100vh - 300px)',
                            overflow: 'auto',
                            bgcolor: 'grey.100',
                            p: 2,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: 2
                          }}
                        >
                          <Document
                            file={pdfUrl}
                            onLoadSuccess={({ numPages }) => setNumPages(numPages)}
                            onLoadError={(error) => setError(`Failed to load PDF: ${error.message}`)}
                            loading={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <CircularProgress size={24} />
                                <Typography>Loading PDF...</Typography>
                              </Box>
                            }
                          >
                            {Array.from(new Array(numPages), (_, index) => (
                              <Box key={`page_${index + 1}`} sx={{ mb: 2 }}>
                                <Typography variant="caption" sx={{ mb: 1, display: 'block', textAlign: 'center' }}>
                                  Page {index + 1} of {numPages}
                                </Typography>
                                <Page
                                  pageNumber={index + 1}
                                  renderTextLayer={true}
                                  renderAnnotationLayer={true}
                                  width={Math.min(window.innerWidth * 0.35, 500)}
                                />
                              </Box>
                            ))}
                          </Document>
                        </Paper>
                      </Collapse>
                    )}
                  </Stack>
                )}
              </Box>
            </Paper>
          </Box>
        </Box>
      </Box>
    </Container>
  );
}
