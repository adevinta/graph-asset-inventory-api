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

## Contributing

**This project is in an early stage, we are not accepting external
contributions yet.**

To contribute, please read the contribution guidelines in
[CONTRIBUTING.md](CONTRIBUTING.md).
