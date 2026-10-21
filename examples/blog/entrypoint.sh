#!/bin/bash
set -euo pipefail

# Allow explicit command overrides without initializing the database.
if [[ "${1:-}" != "/opt/mssql/bin/sqlservr" ]]; then
    exec "$@"
fi

: "${MSSQL_SA_PASSWORD:?Set MSSQL_SA_PASSWORD before starting the container.}"
export SQLCMDPASSWORD="$MSSQL_SA_PASSWORD"
sqlcmd=/opt/mssql-tools18/bin/sqlcmd

if [[ ! -x "$sqlcmd" ]]; then
    echo "SQL Server command-line tools are missing: $sqlcmd" >&2
    exit 1
fi

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

"$@" &
server_pid=$!

echo "Waiting for SQL Server before creating the Blog tables..."
deadline=$((SECONDS + 120))
until "$sqlcmd" -S localhost -U sa -C -b -l 2 -t 5 -Q "SELECT 1" >/dev/null 2>&1; do
    if ! kill -0 "$server_pid" 2>/dev/null; then
        echo "SQL Server exited before schema initialization." >&2
        exit 1
    fi
    if (( SECONDS >= deadline )); then
        echo "SQL Server did not become ready within 120 seconds." >&2
        exit 1
    fi
    sleep 2
done

"$sqlcmd" -S localhost -U sa -C -b -r 1 -i /schema/init.sql

# Keep the container running with SQL Server and forward shutdown signals to it.
wait "$server_pid"
