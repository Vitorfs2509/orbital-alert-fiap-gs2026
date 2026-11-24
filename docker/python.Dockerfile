FROM python:3.12-slim-bookworm AS tools
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY iot-simulator/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && mkdir /lake && touch /lake/.orbital-volume && chown -R 10001:10001 /lake
COPY etl ./etl
COPY iot-simulator/sensor_simulator.py ./iot-simulator/
COPY scripts/demo_fase7.py ./scripts/
USER 10001:10001

FROM tools AS oracle
USER root
RUN pip install --no-cache-dir -r /app/etl/requirements-oracle-db.txt
USER 10001:10001
