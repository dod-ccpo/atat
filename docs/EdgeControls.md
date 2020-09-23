# Edge Control
This document describes the expected connections and listening services.

## Transient Connections
| Service | Direction | Ports | Protocol | Encrypted? | Ciphers      |
| --------|-----------|-------|----------|------------|--------------|
| Azure Container Registry  | Egress    | 443   | HTTP | Yes        | MSFT Managed |
| Azure Storage | Egress | 443 | HTTP | Yes | MSFT Managed|
| Redis | Egress | 6380 | HTTP | Yes | MSFT Managed|
| Postgres | Egress | 5432 | HTTP | Yes | MSFT Managed|

# Listening Ports / Services
| Service/App | Port    | Protocol|  Encrypted? | Accessible |
|-------------|---------|---------|------------|--------|
| ATAT App    | 80, 443 | HTTP    | Both | Load Balancer Only
| ATAT Auth   | 80, 443 | HTTP    | Both | Load Balancer Only

# Host List
## Dev
| Service| Host |
|--------|------|
| Redis  | cloudzero-dev-redis.redis.cache.windows.net |
| Postgres| cloudzero-dev-sql.postgres.database.azure.com |
| Docker Container Registry | cloudzerodevregistry.azurecr.io |

## Production
| Service | Host |
|---------|------|
| Redis   |      |
| Postgres|      |
| Docker Container Registry | |
