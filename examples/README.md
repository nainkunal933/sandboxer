# Examples

## Blog

A SQL Server blog schema with users, posts, comments, and interactions.
Includes CRUD stored procedures for each table.

### Run locally

With Docker running Linux containers, execute from the repository root in PowerShell:

```powershell
docker build --pull -t sandboxer-blog ./examples/blog
$env:MSSQL_SA_PASSWORD = 'BlogExample!2025'
docker run --name sandboxer-blog -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD -p 127.0.0.1:1433:1433 -d sandboxer-blog
docker logs -f sandboxer-blog
```