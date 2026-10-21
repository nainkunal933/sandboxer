FROM mcr.microsoft.com/mssql/server:2025-latest

COPY --chown=mssql:mssql data/tables/ /schema/tables/
COPY --chown=mssql:mssql init.sql entrypoint.sh /schema/

ENTRYPOINT ["/bin/bash", "/schema/entrypoint.sh"]
CMD ["/opt/mssql/bin/sqlservr"]
