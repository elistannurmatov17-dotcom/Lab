# KKM OPTIMA REGISTER

Production-oriented internal workflow for collecting and processing KKM registration applications.

## Architecture

- Public client form: `https://PUBLIC_DOMAIN/`
- Manager portal: `https://ADMIN_DOMAIN/`
- FastAPI backend + PostgreSQL
- Private Docker volume for passport/registration files
- Caddy reverse proxy with automatic HTTPS in production
- Docker Compose, one application stack, no Kubernetes/microservices required

## Client flow

1. Client opens the public link without an account.
2. Client fills all form sections and attaches the registration certificate plus both passport sides.
3. Browser sends multipart form data to the backend.
4. Backend validates the fields and documents, encrypts the `lk.salyk.kg` password and stores the documents privately.
5. Client receives an application number and a private status link.
6. Client can reopen the status link without logging in.

## Manager flow

1. Manager opens the dedicated admin domain and signs in.
2. Manager sees the application queue and status counters.
3. Manager opens an application, views metadata and protected documents, assigns the application and changes its status.
4. Manager can add an internal comment and inspect audit events.
5. Access to `lk.salyk.kg` credentials is a separate audited action.

## Development

```bash
./start.sh
```

The development script creates `.env` with generated secrets and three manager passwords. It is for testing only.

## Production

Create the stack using:

```bash
./start-prod.sh kkm.example.com kkm-admin.example.com
```

Before running it, point both DNS records to the server and open ports 80 and 443. Caddy will request and renew TLS certificates automatically. The generated `.env.production` contains the PostgreSQL password, JWT secret, encryption key, manager passwords and a backup password; keep it private and keep a protected offline copy of the required secrets.

Then create encrypted backups:

```bash
./backup-all.sh
```

Database restore:
```bash
./restore.sh backups/kkm_TIMESTAMP.sql.gz.enc
```

Document restore:
```bash
./restore-documents.sh backups/documents_TIMESTAMP.tar.gz.enc
```

The production database is not exposed to the Internet. Uploaded documents are also not directly exposed through the web server.

## Verification

Run:

```bash
./check.sh
```

The check covers Python compilation, schema tests, shell syntax and Compose YAML parsing. A full Docker build/run should be performed on the target server because this development container does not have a usable Docker daemon.

## Data and security

The project processes identity documents and tax-cabinet credentials. Never put `.env.production`, customer documents, database dumps or encryption keys into Git. Backups created by the included scripts are encrypted. Define retention/deletion rules before production use.

For current KKM rules and classifications, keep the selectable lists in the frontend synchronized with the source actually used by your operational tax workflow rather than assuming a generic economic-activity classifier is identical to the tax portal's internal list.
