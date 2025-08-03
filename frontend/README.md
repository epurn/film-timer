# Interval Timer Frontend

A simple React frontend for the Interval Timer application.

## Features

- **Timer List View**: Displays all timers with names and descriptions
- **Timer Detail View**: Shows timer steps and control buttons (UI only)
- **Bootstrap Styling**: Clean, responsive design
- **API Integration**: Fetches real data from FastAPI backend

## Components

- **NavigationBar**: Top navigation with back to list functionality
- **TimerList**: Displays all timers in a card layout
- **TimerDetail**: Shows timer information, steps, and control buttons
- **ApiService**: Handles API communication with the backend

## Getting Started

### Development Mode

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```
   
   The app will run on http://localhost:3000

### Production Mode

The frontend is containerized with Docker and served by nginx:

```bash
# Build and run with docker-compose
cd deployment
docker-compose up --build
```

Access the frontend at http://localhost:3000

## API Integration

The frontend connects to the FastAPI backend at:
- Development: `http://localhost:8000`
- Production: Configured via `REACT_APP_API_URL` environment variable

## UI Structure

### Timer List Page (`/`)
- Displays all timers in a responsive card grid
- Shows timer name, description, and step count
- Click any timer to view details

### Timer Detail Page (`/timer/:id`)
- Timer information at the top
- List of all timer steps with:
  - Step number and title
  - Duration (formatted as MM:SS)
  - Repetitions (if > 1)
  - Notes (if available)
- Control buttons at the bottom:
  - Play (green)
  - Pause (yellow) 
  - Stop (red)
- Back button to return to timer list

## Technologies Used

- **React 18**: Frontend framework
- **React Router**: Client-side routing
- **Bootstrap 5**: CSS framework
- **React Bootstrap**: Bootstrap components for React
- **Nginx**: Production web server (in Docker)

## Current Limitations

- Timer controls are UI-only (no actual timer functionality yet)
- No timer creation/editing interface
- No import/export UI (backend supports it via API)

These features can be added in future iterations as the application evolves.