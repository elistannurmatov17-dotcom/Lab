# Security notes

This application handles passport scans, registration documents and credentials for `lk.salyk.kg`.

## Production baseline

- HTTPS is terminated by Caddy with automatic certificate management.
- PostgreSQL and document storage are reachable only through the internal Docker network/volumes.
- Document downloads require manager authentication.
- Uploaded PDF/JPG/PNG files are checked by MIME type, file signature and parser/decoder validation.
- Uploads are stored with generated storage names outside the web root.
- The public application status uses a random token; only its SHA-256 hash is stored in PostgreSQL.
- The `lk.salyk.kg` password is encrypted at rest with Fernet; the encryption key is supplied as a secret environment variable and never committed.
- Manager passwords are stored as Argon2 password hashes.
- Login and public submission/status requests have application-level rate limiting.
- Important manager actions are recorded in the audit log.
- Security-related response headers are set by the reverse proxy.
- Production OpenAPI/Swagger endpoints are disabled.
- Database and document backups created by the included scripts are encrypted with AES-256-CBC using `BACKUP_PASSWORD`.

## Operational requirements

Before real customer data:

- Point both DNS names to the server and allow TCP 80/443.
- Keep `.env.production` at mode 600 and store a protected offline copy of the encryption key and backup password.
- Run `./backup-all.sh` on a schedule and store encrypted backups separately from the production host when possible.
- Test both DB and document restore procedures before relying on the backups.
- Define a retention/deletion period for passport scans and other personal data.
- Restrict SSH/server access and keep Docker, host OS and reverse-proxy images updated.
- Do not use real customer data in development or tests.

## Credential exposure

A manager can explicitly request the decrypted `lk.salyk.kg` password from the manager portal because the business workflow requires it. Such access is authenticated and audited. The password must never appear in application logs, backups exported to public locations, screenshots, issue trackers or Git.

## Form data

The public form stores all submitted business fields, selected object/activity/tax/calculation values, custom UGNS text when used, and all three uploaded documents. The form is intentionally the original seven-section workflow; the only workflow addition is direct submission to the backend.
