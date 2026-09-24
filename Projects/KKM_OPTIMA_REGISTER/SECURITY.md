# Security notes

This project handles passport scans, registration documents and `lk.salyk.kg` credentials.

## Required before production

- Put the service behind HTTPS with a trusted certificate.
- Use strong unique `POSTGRES_PASSWORD` and `JWT_SECRET` values.
- Generate a Fernet key for `CREDENTIAL_ENCRYPTION_KEY` and keep it outside Git.
- Use strong passwords for the three manager accounts.
- Keep the document volume private; never mount it into the web root.
- Configure backups with access control and encryption.
- Review retention/deletion requirements for personal data.
- Add rate limiting at the reverse proxy before public exposure.
- Do not send real customer data to development environments.

## Sensitive data

The application stores the `lk.salyk.kg` password encrypted at rest. Manager access to credentials and documents is authenticated and written to the audit log. Normal application list/detail responses do not return the password.
