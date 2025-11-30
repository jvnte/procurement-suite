# Procurement Suite

A comprehensive procurement management system with AI-powered document intake, API services, and a modern web interface.

## Installation

### Prerequisites
- Docker and Docker Compose
- OpenAI API Key

### Setup Steps

1. **Configure environment variables**

   Copy all `.env.template` files from the individual apps to `.env`:
   ```bash
   cp apps/agent/.env.template apps/agent/.env
   cp apps/api/.env.template apps/api/.env
   cp apps/ui/.env.template apps/ui/.env
   ```

2. **Set OpenAI API Key**

   Edit `apps/agent/.env` and set your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Build and run the application**

   ```bash
   docker-compose up --build
   ```

4. **Access the application**

   - UI: http://localhost:8080
   - Procurement API: http://localhost:8081
   - Intake Agent API: http://localhost:8082

## Architecture

### System Components

```mermaid
graph TB
    UI[Procurement Suite UI<br/>Port 8080]
    AgentAPI[Agent API<br/>Port 8082]
    ProcAPI[Procurement API<br/>Port 8081]

    UI -->|Upload PDF| AgentAPI
    UI -->|Submit Request| ProcAPI
    UI -->|Fetch Requests| ProcAPI

    AgentAPI -->|AI Processing<br/>OpenAI| AgentAPI
    ProcAPI -->|Store & Retrieve| DB[(In-Memory Repository)]

    style UI fill:#e1f5ff
    style AgentAPI fill:#fff4e1
    style ProcAPI fill:#e8f5e9
    style DB fill:#f3e5f5
```

### HTTP Request Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Procurement Suite UI
    participant Agent as Agent API
    participant API as Procurement API

    Note over User,API: Document Upload & Processing
    User->>UI: Upload PDF document
    UI->>Agent: POST /agent/intake<br/>(PDF file)
    Agent->>Agent: Extract data using AI
    Agent-->>UI: Return ProcurementRequestCreate<br/>(extracted data)
    UI->>UI: Pre-fill form with extracted data

    Note over User,API: Request Submission
    User->>UI: Review & submit form
    UI->>API: POST /intake/request<br/>(JSON payload)
    API->>API: Validate commodity group
    API->>API: Create request with status: OPEN
    API-->>UI: Return request ID
    UI->>UI: Display success message

    Note over User,API: Request Management
    User->>UI: View requests list
    UI->>API: GET /intake/requests
    API-->>UI: Return all requests

    User->>UI: Update request status
    UI->>API: PATCH /intake/requests/{id}/status
    API->>API: Update status<br/>(OPEN → IN_PROGRESS → CLOSED)
    API-->>UI: Return updated request
    UI->>UI: Refresh request list
```

### Key Endpoints

#### Agent API (Port 8082)
- `POST /agent/intake` - Process PDF document using Intake Agent to extract procurement data

#### Procurement API (Port 8081)
- `POST /intake/request` - Create new procurement request
- `GET /intake/requests` - Get all procurement requests
- `GET /intake/requests/{id}` - Get request by ID
- `PATCH /intake/requests/{id}/status` - Update request status
- `GET /intake/commodity_groups` - Get available commodity groups

### Technology Stack

- **Frontend**: React + TypeScript + Material-UI + Vite
- **Backend APIs**: FastAPI + Python
- **AI/ML**: OpenAI API (document processing)
- **Containerization**: Docker + Docker Compose
- **PDF Processing**: react-pdf (frontend), AI extraction (backend)

## Development

### Project Structure

```
procurement-suite/
├── apps/
│   ├── agent/          # AI-powered intake agent service
│   ├── api/            # Procurement management API
│   └── ui/             # React frontend application
├── docker-compose.yaml # Multi-container orchestration
└── README.md
```

### Data Flow

1. **Document Upload**: User uploads PDF → UI sends to Agent API
2. **AI Extraction**: Agent API processes PDF using OpenAI → Returns structured data
3. **Form Pre-fill**: UI populates form fields with extracted data
4. **Request Creation**: User submits → UI sends to Procurement API → Stored with status OPEN
5. **Status Updates**: Requests can be updated through workflow: OPEN → IN_PROCESS → CLOSED 
