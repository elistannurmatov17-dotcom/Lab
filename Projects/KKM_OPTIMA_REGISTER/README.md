# KKM_OPTIMA_REGISTER

Internal application for collecting and processing KKM registration applications.

## Architecture

- Public client form: no login required.
- Manager portal: authenticated access for up to 3 managers.
- Backend API: FastAPI/Python.
- Database: PostgreSQL for application metadata and workflow.
- Private document storage for passport scans, registration documents and PDF files.
- Nginx reverse proxy with HTTPS in deployment.
- Docker Compose for local/server deployment.

## Client flow

1. Open the public application link.
2. Fill in company/IE, director, contact, contract, trading point, tax and settlement data.
3. Attach registration certificate and both sides of the director's passport.
4. Submit the application to the backend.
5. Receive an application number and initial status.

## Manager flow

1. Sign in to the manager portal.
2. View the incoming application queue.
3. Open an application and review all submitted data and documents.
4. Assign the application to a manager.
5. Change status and add internal comments.
6. Keep an audit history of important actions.

## Security baseline

Because the application handles identity documents and other sensitive data:

- HTTPS/TLS for transmission.
- No credentials or sensitive documents in application logs.
- Uploaded files are validated and stored outside the public web root.
- Documents are accessed through authorized backend endpoints, not direct public URLs.
- Secrets are supplied through environment/secret management and never committed to Git.
- File size and type limits are enforced.
- Backups of sensitive data are protected.
- Retention/deletion rules for documents are defined before production use.

## Planned repository layout

```text
KKM_OPTIMA_REGISTER/
├── frontend/
├── backend/
├── nginx/
├── storage/
├── docker-compose.yml
├── .env.example
├── start.sh
├── stop.sh
├── SECURITY.md
└── README.md
```

## Status

Initial project specification created. Implementation will start with the backend API contract and the client form integration.
