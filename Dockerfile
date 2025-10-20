# Minimal base for building/serving docs and running experiments later
FROM python:3.11-slim
WORKDIR /app
COPY docs/ /app/docs/
COPY mkdocs.yml /app/
RUN pip install --no-cache-dir mkdocs mkdocs-material
EXPOSE 8000
CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]
