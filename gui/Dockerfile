FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y python3-tk tk x11-apps libx11-6 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY aeropuerto_gui.py .

ENV DISPLAY=:0

CMD ["python", "aeropuerto_gui.py"]