FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      wget fontconfig \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/share/fonts/truetype/google-fonts/teko \
 && wget -qO /usr/share/fonts/truetype/google-fonts/teko/Teko-Regular.ttf \
      https://github.com/google/fonts/raw/main/ofl/teko/Teko%5Bwght%5D.ttf \
 && fc-cache -f -v \
 && rm -rf /var/cache/fontconfig/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/frontend ./frontend
COPY app/backend/src ./src

ENV FLASK_APP=src/main.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_ENV=development

EXPOSE 5000

CMD ["flask", "run"]
