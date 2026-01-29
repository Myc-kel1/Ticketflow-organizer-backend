# Event Organizer Backend

Backend service for event organizers to create, update, manage events, handle ticket sales, scanning, and analytics using FastAPI and Supabase.

## Features

- 🔐 **Authentication & Authorization**: JWT-based auth with Supabase
- 📅 **Event Management**: Full CRUD operations for events
- 🖼️ **Image Upload**: Upload event images to Supabase Storage
- 🎫 **Ticket Management**: View and manage ticket sales
- 📊 **Dashboard Analytics**: Real-time statistics and insights
- 🔍 **Ticket Scanner**: QR code scanning and check-in system
- 💰 **Sales Reports**: Revenue tracking and analytics
- 👥 **Role-Based Access**: Organizer-only endpoints

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **Database**: Supabase Postgres
- **Authentication**: Supabase Auth (JWT)
- **Storage**: Supabase Storage
- **Server**: Uvicorn

## Project Structure

```
OrganizerSide/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── dashboard.py         # Dashboard analytics
│   │   ├── events.py            # Event CRUD + images
│   │   ├── sales.py             # Sales reports
│   │   ├── scanner.py           # Ticket scanning
│   │   └── tickets.py           # Ticket management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings
│   │   ├── security.py          # Security utilities
│   │   └── supabase.py          # Supabase client
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── auth.py              # JWT validation
│   │   └── permissions.py       # Role enforcement
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── event.py             # Event schemas
│   │   └── image.py             # Image schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dashboard_service.py # Dashboard logic
│   │   ├── event_service.py     # Event logic
│   │   ├── image_service.py     # Storage logic
│   │   ├── sales_service.py     # Sales logic
│   │   ├── scanner_service.py   # Scanner logic
│   │   └── ticket_service.py    # Ticket logic
│   └── utils/
│       └── __init__.py
├── .env
├── .env.example
├── main.py                       # Application entry point
├── requirements.txt
└── README.md
```

## Database Schema

### Events Table

```sql
CREATE TABLE events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  location VARCHAR(300) NOT NULL,
  start_date TIMESTAMP WITH TIME ZONE NOT NULL,
  end_date TIMESTAMP WITH TIME ZONE NOT NULL,
  capacity INTEGER,
  ticket_price DECIMAL(10, 2),
  category VARCHAR(100),
  organizer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_events_organizer_id ON events(organizer_id);
CREATE INDEX idx_events_start_date ON events(start_date);
```

### Tickets Table

```sql
CREATE TABLE tickets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  attendee_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  attendee_email VARCHAR(255) NOT NULL,
  attendee_name VARCHAR(255),
  ticket_code VARCHAR(100) UNIQUE NOT NULL,
  status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'checked_in', 'cancelled')),
  price DECIMAL(10, 2) NOT NULL,
  purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  checked_in_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_tickets_event_id ON tickets(event_id);
CREATE INDEX idx_tickets_attendee_id ON tickets(attendee_id);
CREATE INDEX idx_tickets_ticket_code ON tickets(ticket_code);
CREATE INDEX idx_tickets_status ON tickets(status);
```

### Row Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;

-- Events policies
CREATE POLICY "Organizers can view own events" ON events
  FOR SELECT USING (auth.uid() = organizer_id);

CREATE POLICY "Organizers can create events" ON events
  FOR INSERT WITH CHECK (auth.uid() = organizer_id);

CREATE POLICY "Organizers can update own events" ON events
  FOR UPDATE USING (auth.uid() = organizer_id);

CREATE POLICY "Organizers can delete own events" ON events
  FOR DELETE USING (auth.uid() = organizer_id);

-- Tickets policies
CREATE POLICY "Organizers can view tickets for their events" ON tickets
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM events 
      WHERE events.id = tickets.event_id 
      AND events.organizer_id = auth.uid()
    )
  );

CREATE POLICY "Users can view their own tickets" ON tickets
  FOR SELECT USING (auth.uid() = attendee_id);
```

### Supabase Storage Setup

1. Go to Supabase Dashboard → Storage
2. Create a new bucket named `event-images`
3. Set bucket to **Public** or configure policies

## Setup Instructions

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd OrganizerSide

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your Supabase credentials
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service role key
- `SUPABASE_JWT_SECRET`: Your Supabase JWT secret

### 3. Run Application

```bash
# Development mode
uvicorn main:app --reload --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Login with email/password |
| POST | `/signup` | Register new organizer |
| POST | `/logout` | Logout current user |
| GET | `/me` | Get current user info |

### Events (`/api/events`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/events` | Create new event |
| GET | `/events/me` | List my events |
| GET | `/events/{id}` | Get event details |
| PATCH | `/events/{id}` | Update event |
| DELETE | `/events/{id}` | Delete event |
| POST | `/events/{id}/images` | Upload event images |

### Dashboard (`/api/dashboard`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats` | Get dashboard statistics |
| GET | `/recent-activity` | Get recent activities |
| GET | `/revenue-breakdown` | Get revenue by event |

### Tickets (`/api/tickets`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/event/{id}` | Get all event tickets |
| GET | `/event/{id}/stats` | Get ticket statistics |
| GET | `/{id}` | Get ticket details |
| PATCH | `/{id}/cancel` | Cancel a ticket |

### Scanner (`/api/scanner`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/checkin` | Check in a ticket |
| POST | `/validate` | Validate ticket (no check-in) |
| GET | `/event/{id}/checkins` | Get event check-ins |

### Sales (`/api/sales`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/report` | Get sales reports |
| GET | `/daily` | Get daily sales breakdown |
| GET | `/summary` | Get overall sales summary |

## Example Requests

### Register Organizer

```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "organizer@example.com",
    "password": "SecurePassword123",
    "full_name": "John Doe",
    "role": "organizer"
  }'
```

### Create Event

```bash
curl -X POST "http://localhost:8000/api/events" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "location": "Lagos, Nigeria",
    "start_date": "2024-06-15T09:00:00Z",
    "end_date": "2024-06-17T18:00:00Z",
    "capacity": 500,
    "ticket_price": 50000,
    "category": "Technology"
  }'
```

### Check In Ticket

```bash
curl -X POST "http://localhost:8000/api/scanner/checkin" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_code": "ABC123XYZ"
  }'
```

## Security Features

- **JWT Validation**: Every request validates Supabase JWT
- **Role-Based Access**: Organizer role required for all operations
- **Ownership Verification**: Users can only access their own data
- **Row Level Security**: Database-level security via Supabase RLS

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error description"
}
```

HTTP Status Codes:
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Development

### Code Structure

- **Routers**: Handle HTTP requests (no business logic)
- **Services**: Contain all business logic and database operations
- **Dependencies**: Handle authentication and authorization
- **Schemas**: Pydantic models for validation

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Production Deployment

### Environment Variables

Set in production:
- `DEBUG=False`
- Configure CORS origins
- Use production Supabase project

### Deployment Options

- **Railway**: Git-based deployment
- **Render**: Free tier available
- **AWS**: Elastic Beanstalk or ECS
- **DigitalOcean**: App Platform

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

"# Ticketflow-organizer-backend" 
"# Ticketflow-organizer-backend" 
"# Ticketflow-organizer-backend" 
"# Ticketflow-organizer-backend" 
"# Ticketflow-organizer-backend" 
