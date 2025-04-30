# Rio Bus Alert API 🚌💨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

API and Web Application for real-time monitoring of Rio de Janeiro city buses, allowing the creation of personalized proximity alerts via email.

**Note:** This project was developed as part of the selection process for **Maravi**.

## Overview

This project consists of a complete Web App (FastAPI Backend + React Frontend) that:

1.  Collects bus positioning data from Rio de Janeiro every minute via public API ([Rio Open Urban Mobility Data](https://dados.mobilidade.rio/)).
2.  Allows users to define a **departure point** (selected on the map) and a **bus line** of interest.
3.  Allows users to configure a **daily time window** and a **start date** to receive email notifications.
4.  Continuously monitors buses on the selected line in relation to the user-defined point.
5.  Uses an external API (e.g., [Travel Time API](https://traveltime.com/)) to calculate the **estimated time of arrival (ETA)** of buses at the point, optimizing calls with distance and approaching filters.
6.  Sends an **email notification** to the user when a monitored bus is approximately **10 minutes** away from arriving at the point, within the defined time window, and after the configured start date.
7.  Presents an interface featuring:
    - An interactive map (Leaflet) for point selection and bus visualization.
    - A table with information about buses on the selected line (Order ID, Speed, ETA, Approaching Status, Distance).
    - A form for configuring the alert.

## Core Features

- Real-time collection of bus geolocation data.
- Departure point selection via interactive map (Leaflet).
- Creation of personalized User Alerts (Line, Point, Daily Time Window, Start Date, Email).
- Haversine distance calculation and approaching status analysis.
- Estimated Time of Arrival (ETA) calculation via external API (Travel Time).
- Background monitoring (Celery) for checking alerts.
- Email notification dispatch (SMTP via Gmail App Password).
- RESTful API (FastAPI) for Frontend-Backend communication.
- Reactive interface (React) with bus table and map.
- Complete containerization with Docker and Docker Compose.

## Tech Stack

- **Backend:**
  - Python 3.11+
  - FastAPI
  - SQLModel (based on SQLAlchemy & Pydantic)
  - Celery (with Redis as Broker/Backend)
  - Uvicorn
  - python-dotenv
  - httpx (or requests)
  - psycopg2-binary (PostgreSQL Driver)
- **Frontend:**
  - React
  - Vite
  - Tailwind CSS
  - Axios
  - react-leaflet (and leaflet)
  - react-hook-form (and yup)
  - date-fns
  - @heroicons/react (or other icon library)
- **Database & Cache:**
  - PostgreSQL (v15+)
  - Redis (v7+)
- **Environment:**
  - Docker
  - Docker Compose

## Project Structure (Simplified)

```

.
├── backend/ \# FastAPI, Celery, Services, Models code
│ ├── app/
│ └── Dockerfile
├── frontend/ \# React (Vite) code
│ ├── public/
│ ├── src/
│ └── Dockerfile
├── markdown/ \# Auxiliary documentation
│ └── configure_gmail.md
├── screenshots/ \# Folder for application screenshots
├── .env \# Local file with environment variables (NOT versioned)
├── .env.example \# Example file for environment variables (Versioned)
├── .gitignore
├── docker-compose.yml \# Container orchestration
└── README.md \# This file

```

## Getting Started

Follow these instructions to set up and run the project locally using Docker.

### Prerequisites

- Git
- Docker ([Installation](https://docs.docker.com/engine/install/))
- Docker Compose ([Usually included with Docker Desktop](https://docs.docker.com/compose/install/))

### Installation

1.  **Clone the Repository:**

    ```bash
    git clone <your-repository-url>
    cd <repository-folder-name>
    ```

2.  **Configure Environment Variables:**

    - Copy the example file (if it exists) or create a new file named `.env` in the project root:
      ```bash
      cp .env.example .env
      ```
      _(If `.env.example` doesn't exist, create the `.env` file manually)_
    - Edit the `.env` file and fill in **ALL** required variables. It should contain something like:

      ```dotenv
      # Database Configuration (PostgreSQL)
      DATABASE_URL=postgresql://postgres:pstudySQL@db:5432/mobility_rio
      # (Adjust user/password/db name if changed in docker-compose.yml)

      # Redis Configuration (for Celery)
      REDIS_URL=redis://redis:6379/0

      # Email Configuration (Gmail SMTP)
      SENDER_EMAIL=your_gmail_address@gmail.com # <<< YOUR GMAIL EMAIL
      GMAIL_APP_PASSWORD=xxxx yyyy zzzz wwww # <<< YOUR GENERATED APP PASSWORD (16 letters, no spaces)

      # Travel Time API Configuration
      TRAVELTIME_APP_ID=YOUR_TRAVELTIME_APP_ID # <<< YOUR TRAVEL TIME CREDENTIAL
      TRAVELTIME_API_KEY=YOUR_TRAVELTIME_API_KEY # <<< YOUR TRAVEL TIME CREDENTIAL

      # Other variables (if any)...
      # SECRET_KEY=...
      ```

    - **IMPORTANT (GMAIL_APP_PASSWORD):** You should **NOT** use your regular Gmail account password. You need to generate a specific **"App Password"** in your Google Account security settings (requires 2-Step Verification to be enabled).
      - ➡️ **Detailed instructions:** [markdown/configure_gmail.md](markdown/configure_gmail.md) _(Assuming this file exists and is translated or understandable)_
    - **IMPORTANT (TRAVELTIME):** You need to register on the [Travel Time](https://traveltime.com/) website to obtain a free `Application Id` and `Api Key` (they have usage limits).

3.  **Ensure `.env` is NOT committed to Git:** Verify that your `.gitignore` file includes the line `.env`.

### Running the Application

1.  **Build and Start Containers:** In your terminal, at the project root (where `docker-compose.yml` is), run:

    ```bash
    docker compose up --build -d
    ```

    - `--build`: Rebuilds images if Dockerfiles or dependencies changed.
    - `-d`: Runs containers in detached mode (background).

2.  **Access the Application:**

    - **Frontend (React):** Open your browser and go to [`http://localhost:5173`](http://localhost:5173)
    - **Backend API Docs (Swagger UI):** Go to [`http://localhost:8000/docs`](http://localhost:8000/docs)
    - **Backend API Docs (ReDoc):** Go to [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

3.  **First Run:** It might take a minute or two after starting the containers for the Celery tasks to begin fetching bus data and populating the Redis cache. If the application seems empty initially, please wait a moment and refresh.

### Stopping the Application

To stop the running containers, run this in your terminal at the project root:

```bash
docker compose down
```

_(Use `docker compose down -v` if you also want to remove volumes, like the PostgreSQL data volume)._

## API Documentation

Interactive API documentation, automatically generated by FastAPI, is available at:

- **Swagger UI:** [`http://localhost:8000/docs`](https://www.google.com/search?q=http://localhost:8000/docs)
- **ReDoc:** [`http://localhost:8000/redoc`](https://www.google.com/search?q=http://localhost:8000/redoc)

## Screenshots

_(Add screenshots of the main application views here. Create a `screenshots/` folder in the root and place the images there)_

**1. Welcome Screen (Location Permission)**

**2. Location Confirmation Screen (Map)**

**3. Main Dashboard (Stop/Line Selection, Form, Bus Table & Map)**

## Contact

Developed by **Lucas [Your Last Name]** - [endereço de e-mail removido]

- [GitHub](https://www.google.com/search?q=https://github.com/%5Byour-username%5D)
- [LinkedIn](https://www.google.com/search?q=https://linkedin.com/in/%5Byour-username%5D) _(Optional)_

## License

Distributed under the MIT License. See `LICENSE` for more information (if a LICENSE file exists).

[MIT License](https://opensource.org/licenses/MIT)

```

---

Escolha a versão que preferir e lembre-se de preencher as informações e adicionar as imagens! Este README deve dar uma ótima visão geral do seu excelente trabalho.
```
