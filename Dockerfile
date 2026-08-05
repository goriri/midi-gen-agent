FROM python:3.11-slim

# Install system dependencies (fluidsynth & GM soundfont)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fluidsynth \
    fluid-soundfont-gm \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Ensure default soundfont location link exists
RUN mkdir -p /app/midi-agent-skill/soundfonts && \
    cp /usr/share/sounds/sf2/FluidR3_GM.sf2 /app/midi-agent-skill/soundfonts/A320U.sf2 || true

ENV PORT=8080
EXPOSE 8080

CMD ["python3", "server.py"]
