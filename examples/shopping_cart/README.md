# Shopping cart: local development

Run MongoDB in Docker and the Python setup script on your machine to explore the
shopping cart schema and try changes locally.

## Prerequisites

- Python 3.12 or newer and uv 0.12.23 or newer.
- Docker running Linux containers, with local port 27017 available.

Run the following commands in PowerShell. From the repository root, enter this
example's directory:

```powershell
cd examples/shopping_cart
```

## Start MongoDB

Start a database container using the base MongoDB image. The Python script will
initialize its collections separately.

```powershell
docker run --name shopping-cart-local -p 127.0.0.1:27017:27017 -d mongodb/mongodb-community-server:9.0-ubi9-slim
```

Wait for MongoDB to respond before running the script. Retry this command until
it returns `ok: 1`:

```powershell
docker exec shopping-cart-local mongosh --quiet --eval 'db.adminCommand({ ping: 1 })'
```

## Create the collections

```powershell
uv run --locked data/create_collections.py
```

uv creates this example's `.venv` and installs its locked dependencies
automatically. The script connects to `mongodb://127.0.0.1:27017` and creates
`carts`, `orders`, and `products` in the `shopping_cart` database with JSON Schema
validators. It does not insert sample data.

Edit the files in `data/schemas/` and rerun the same command to update validators.
Existing documents are preserved.

To connect to a different MongoDB instance or port, set the connection URI first:

```powershell
$env:MONGODB_URI = 'mongodb://127.0.0.1:27018'
uv run --locked data/create_collections.py
```

To return to the default connection, run `Remove-Item Env:MONGODB_URI`.

## Explore the data

Open a MongoDB shell:

```powershell
docker exec -it shopping-cart-local mongosh shopping_cart
```

Inside that shell, list the collections and insert a sample product:

```javascript
show collections
db.products.insertOne({ name: "Demo product", price: 9.99, stock: 10 })
db.products.find()
```

Run `exit` to leave the shell. Inserts and updates must satisfy the validators.

## Stop and resume

```powershell
docker stop shopping-cart-local
docker start shopping-cart-local
```

The existing container retains its data. On later sessions, use `docker start`
instead of repeating `docker run`, then check readiness again.

If the Python script reports a connection failure, check that Docker and the
container are running, MongoDB is ready, and `MONGODB_URI` points to the correct
port. Use `docker logs shopping-cart-local` to inspect startup failures. If port
27017 is already occupied, use another host port, such as
`-p 127.0.0.1:27018:27017`, when creating the container and set `MONGODB_URI`
accordingly.
