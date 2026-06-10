FROM python:3.13-slim

# git is required for romajitable git+https:// dependency
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure runtime directories exist (bind-mounts will overlay these if provided)
RUN mkdir -p logs cache output guild_setting user_dict/audio_data

CMD ["python", "main.py"]
