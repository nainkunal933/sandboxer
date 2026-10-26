#!/bin/bash
set -euo pipefail

# Allow explicit command overrides without initializing the database.
if [[ "${1:-}" != "mongod" ]]; then
    exec "$@"
fi
for argument in "$@"; do
    case "$argument" in
        -h|--help|--version)
            exec /usr/local/bin/docker-entrypoint "$@"
            ;;
    esac
done

server_pid=""
stop_server() {
    if [[ -n "$server_pid" ]]; then
        kill -TERM "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
}
trap stop_server EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

/usr/local/bin/docker-entrypoint "$@" &
server_pid=$!

echo "Waiting for MongoDB before creating the shopping cart collections..."
deadline=$((SECONDS + 120))
until timeout 5 mongosh "${MONGODB_URI:-mongodb://127.0.0.1:27017}" \
    --quiet --eval 'db.adminCommand({ ping: 1 })' >/dev/null 2>&1; do
    if ! kill -0 "$server_pid" 2>/dev/null; then
        echo "MongoDB exited before schema initialization." >&2
        exit 1
    fi
    if (( SECONDS >= deadline )); then
        echo "MongoDB did not become ready within 120 seconds." >&2
        exit 1
    fi
    sleep 2
done

/opt/venv/bin/python -u /schema/create_collections.py
echo "Shopping cart collections are ready."

# Keep the container running and forward shutdown signals to MongoDB.
wait "$server_pid"
