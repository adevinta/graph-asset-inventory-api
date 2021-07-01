# Security Graph - Asset Inventory API

## Security Graph

Security Graph is a data architecture that provides real-time views of assets
and their relationships. Assets to be considered include software, cloud
resources and, in general, any piece of information that a security team needs
to protect.

Security Graph not only stores the catalog of active assets and the assets
assigned to teams. It also keeps a historical log of the multidimensional
relationships among these assets, including their attributes relevant to
security.

## Asset Inventory API

Asset Inventory API is the layer responsible for storing assets and receiving
updates from "recon" services. Assets are persisted on the graph.

This layer hides the low-level details of the graph and implements the graph
queries. Clients can then save and extract inventory data through this common
interface without extra knowledge of vertices or edges.

## Usage

### Local development environment

A local development environment is provided via docker-compose. You can launch
it using the `/script/local` script:

```
script/local
```

This will expose two ports:

- **8000**: Asset Inventory API
- **8888**: Jupyter Notebook

Jupyter Notebook can be accessed via:

```
http://localhost:8888/?token=<token>
```

The required token can be obtained from the docker-compose logs or executing:

```
docker exec graph-asset-inventory-api-local_graph-notebook_1 jupyter notebook list
```

The local development environmet supports hot realoading. This means that you
can modify the code of the service and the changes will be automatically
reloaded without relaunching the environment.

### Test suite

Tests are run inside Docker via docker-compose. You can run the test suite
using the `/script/test` script:

```
script/test
```

The command line arguments passed to this script are passed to pytest. For
instance, you can run a specific test with:

```
script/test tests/test_foo.py::test_foo
```

## Contributing

**This project is in an early stage, we are not accepting external
contributions yet.**

To contribute, please read the contribution guidelines in [CONTRIBUTING.md].


[CONTRIBUTING.md]: CONTRIBUTING.md
