FROM mongodb/mongodb-community-server:9.0-ubi9-slim

USER root
ENV UV_PYTHON_INSTALL_DIR=/opt/python

RUN --mount=from=ghcr.io/astral-sh/uv:0.12.23,source=/uv,target=/uv \
    /uv python install 3.12 \
    && /uv venv --python 3.12 /opt/venv \
    && /uv pip install --no-cache --python /opt/venv/bin/python "pymongo>=4.15,<5"

COPY data/ /schema/
COPY entrypoint.sh /schema/entrypoint.sh
RUN /opt/venv/bin/python -c "from pathlib import Path; path = Path('/schema/entrypoint.sh'); path.write_text(path.read_text())"

USER mongod
EXPOSE 27017

ENTRYPOINT ["/bin/bash", "/schema/entrypoint.sh"]
CMD ["mongod"]
