# LOGWIN Tracking System Demo

A simple HTML/CSS/JavaScript demo simulating a shipment tracking system.

## Features

- **Login Screen**: Simple authentication (any non-empty username/password works)
- **Dashboard**: Professional tracking interface with sidebar navigation
- **Search Form**: Search shipments by number, status, MOT, and dates
- **Results Table**: Display shipment details with horizontal scroll
- **Dummy Data**: No backend, all data is hardcoded in JavaScript

## Project Structure

```
├── assets/
│   ├── logo.png          # Logo for login page
│   └── logo2.png         # Logo for dashboard header
├── css/
│   ├── login.css         # Styles for login page
│   └── dashboard.css     # Styles for dashboard
├── login.html            # Login page
├── dashboard.html        # Main tracking dashboard
└── README.md
```

## How to Run

### Option 1: Double-click (Simplest)
1. Navigate to your project folder
2. Double-click on `login.html`
3. It will open in your default browser

### Option 2: From Command Line (Windows)
```cmd
start login.html
```

### Option 3: With a Local Server (Recommended for development)
Using Python:
```bash
python -m http.server 8000
```
Then open your browser and go to: `http://localhost:8000/login.html`

## Usage

1. **Login Page**:
   - Enter any username and password (both fields required)
   - Click "Anmelden" to log in
   - You'll be redirected to the dashboard

2. **Dashboard**:
   - Use the sidebar to navigate (Dashboard, Track shipments, Track containers)
   - Click the blue circle button (‹) to hide/show the sidebar
   - Fill in the search form with shipment details
   - Try these shipment numbers: **SHIP001**, **SHIP002**, **SHIP003**
   - Click the green "Search" button to see results
   - Scroll horizontally in the results table to see all columns

## Test Data

- **SHIP001**: In Transit - Hamburg to New York (Sea)
- **SHIP002**: Arrived - Tokyo to Frankfurt (Air)
- **SHIP003**: Customs Hold - Shanghai to Rotterdam (Sea)

## Technologies Used

- Pure HTML5
- CSS3 (with Flexbox and Grid)
- Vanilla JavaScript (no frameworks)
- SVG icons

## Notes

- No backend or database required
- All data is stored in JavaScript objects
- Fully responsive design
- Works in all modern browsers
