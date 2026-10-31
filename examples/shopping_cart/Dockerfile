FROM mongodb/mongodb-community-server:9.0-ubi9-slim

USER root
ENV UV_PYTHON_INSTALL_DIR=/opt/python
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock /opt/shopping-cart/

RUN --mount=from=ghcr.io/astral-sh/uv:0.12.23,source=/uv,target=/uv \
    /uv python install 3.12 \
    && /uv sync --locked --no-dev --no-cache --python 3.12 --project /opt/shopping-cart

COPY data/ /schema/
COPY entrypoint.sh /schema/entrypoint.sh
RUN /opt/venv/bin/python -c "from pathlib import Path; path = Path('/schema/entrypoint.sh'); path.write_text(path.read_text())"

USER mongod
EXPOSE 27017

ENTRYPOINT ["/bin/bash", "/schema/entrypoint.sh"]
CMD ["mongod"]
