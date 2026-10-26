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

## Shopping cart

A MongoDB shopping cart schema with carts, orders, and products.
Creates collections with JSON Schema validators on startup.

### Run locally

With Docker running Linux containers, execute from the repository root in PowerShell:

```powershell
docker build --pull -t sandboxer-shopping-cart ./examples/shopping_cart
docker run --name sandboxer-shopping-cart -p 127.0.0.1:27017:27017 -d sandboxer-shopping-cart
docker logs -f sandboxer-shopping-cart
```
