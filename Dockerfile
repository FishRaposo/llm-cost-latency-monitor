FROM python:3.10-slim

WORKDIR /app

COPY shared-core/ /shared-core/
RUN pip install -e /shared-core

COPY llm-cost-latency-monitor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY llm-cost-latency-monitor/src/ ./src/

CMD ["uvicorn", "src.llm_monitor.main:app", "--host", "0.0.0.0", "--port", "8000"]
