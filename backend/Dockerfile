FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy pyproject first so we can install editable package (and deps) before copying source
COPY pyproject.toml ./

RUN python -m pip install --upgrade pip setuptools wheel

ARG DEV=false
# Install package in editable mode; include dev extras when DEV=true
RUN if [ "$DEV" = "true" ] ; then \
            python -m pip install -e .[dev]; \
        else \
            python -m pip install -e .; \
        fi

# Copy application source into the container (preserve layout used by repo)
COPY ./app/ ./

ENV PYTHONPATH="/app:${PYTHONPATH}"

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]