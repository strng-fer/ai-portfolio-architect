FROM python:3.12-slim

WORKDIR /app
COPY app.py ./
COPY samples ./samples

ENV PORT=7860
EXPOSE 7860

RUN useradd -m appuser && chown -R appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:7860/healthz',timeout=4).status==200 else 1)"

CMD ["python", "app.py"]
