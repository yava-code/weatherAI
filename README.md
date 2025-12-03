# MeteoMind API

MeteoMind API is a FastAPI-based application that provides weather predictions using machine learning models. It fetches weather data from external sources, trains models, and exposes endpoints for weather analysis and predictions.

## Features

-   **Weather Data Fetching:** Fetches current and historical weather data from the Open-Meteo API.
-   **Machine Learning Models:** Trains and uses machine learning models (Random Forest Regressor) to predict temperature.
-   **Async Support:** Built with modern asynchronous Python frameworks like FastAPI and httpx.
-   **Background Tasks:** Uses Celery for asynchronous task processing, such as model training and data monitoring.
-   **Dockerized:** Comes with a `docker-compose.yml` for easy setup and deployment.

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/meteomind-api.git
    cd meteomind-api
    ```

2.  **Build and run the services using Docker Compose:**

    ```bash
    docker-compose up -d --build
    ```

    This will start the following services:

    -   `api`: The main FastAPI application.
    -   `worker`: The Celery worker for background tasks.
    -   `beat`: The Celery beat scheduler.
    -   `db`: A PostgreSQL database.
    -   `redis`: A Redis server for caching and message broking.

### Usage

The API will be available at `http://localhost:8000`.

#### Endpoints

-   `GET /`: Returns a welcome message.
-   `GET /health`: Returns the health status of the application.
-   `POST /trigger-train`: Triggers a background task to train the global machine learning model.
-   `GET /metrics`: Retrieves the metrics of the globally trained model.
-   `POST /analyze`: Analyzes weather data for a specific city.

    **Request Body:**

    ```json
    {
        "city_name": "London"
    }
    ```

    **Response:**

    A JSON object containing the city's coordinates, current weather, temperature predictions for the next 24 hours, and model metrics.

## Project Structure

```
.
├── app/                  # Main application source code
│   ├── core/             # Core components (e.g., database)
│   ├── models/           # Data models
│   ├── services/         # Business logic (weather and ML services)
│   ├── main.py           # FastAPI application entrypoint
│   └── worker.py         # Celery worker and task definitions
├── tests/                # Tests
├── weather_models/       # Directory for trained model artifacts
├── docker-compose.yml    # Docker Compose configuration
└── Dockerfile            # Dockerfile for the application
```
