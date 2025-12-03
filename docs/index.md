# MeteoMind: AI Weather Analytics

Добро пожаловать в документацию проекта MeteoMind.

Это система полного цикла для сбора, анализа и предсказания погоды, построенная на микросервисной архитектуре.

## Архитектура

- Backend: FastAPI (Python 3.11)
- Frontend: Streamlit
- ML Engine: Scikit-Learn (RandomForest)
- Database: PostgreSQL
- Async Tasks: Celery + Redis
- Infrastructure: Docker Compose

## Установка

```bash
git clone https://github.com/yava-code/meteo-mind.git
cd meteo-mind
docker-compose up --build
```
