# KKM OPTIMA REGISTER

Internal workflow for collecting and processing KKM registration applications.

## What is included

- Public client form at `/` without client login.
- Submission of form data plus three required document files.
- PostgreSQL for application metadata and workflow.
- Private Docker volume for uploaded passport/registration documents.
- File validation for PDF/JPG/PNG and per-file size limits.
- Encryption at rest for the `lk.salyk.kg` password.
- Manager login for a small internal team.
- Application queue, details, assignment, status changes and audit events.
- Public status URL based on a random unguessable token.
- Nginx reverse proxy and basic rate limiting/security headers.

## Local/server start

```bash
cp .env.example .env
./start.sh
```

On the first start `start.sh` generates strong secrets and three temporary manager passwords. Save those passwords securely; `.env` must never be committed.

The application is available through Nginx. API documentation is at `/docs`.

## Production

Put the service behind HTTPS with a trusted certificate and real domain. Do not use `ENVIRONMENT=development` in production. Restrict access to the manager portal, protect backups, and define retention/deletion rules for personal documents before real customer data is used.

## Important

The application processes passport images/PDFs and tax-cabinet credentials. Never use real customer data in development or tests. Never commit `.env`, customer documents, backups or encryption keys.
