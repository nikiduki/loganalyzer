FROM python:3.9.7

WORKDIR /app

RUN pip install --no-cache-dir \
    protobuf==3.20.0 \
    streamlit==1.22.0 \
    st-pages==0.4.1 \
    streamlit_extras \
    python-dotenv \
    pydantic

EXPOSE 8080

COPY src/frontend /app
COPY .env /app/.env

CMD streamlit run --server.port 8080 --server.enableCORS false ui.py
