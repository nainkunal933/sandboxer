FROM mcr.microsoft.com/mssql/server:2025-latest

COPY --chown=mssql:mssql data/tables/ /schema/tables/
COPY --chown=mssql:mssql init.sql /mssql-server-setup-scripts.d/01_blog.sql
