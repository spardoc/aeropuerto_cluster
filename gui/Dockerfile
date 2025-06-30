FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y python3-tk tk x11-apps libx11-6 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install pillow

WORKDIR /app

COPY gui/gui.py .
COPY images ./images

ENV DISPLAY=:0

CMD ["python", "gui.py"]