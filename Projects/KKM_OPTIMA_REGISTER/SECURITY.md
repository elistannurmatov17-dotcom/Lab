# Security notes

This project handles passport scans, registration documents and lk.salyk.kg credentials.

Before production:
- use HTTPS with a trusted certificate;
- set strong unique secrets outside Git;
- keep the private document volume outside the web root;
- protect backups;
- configure retention/deletion rules;
- add reverse-proxy rate limiting;
- never use real customer data in development.

The lk.salyk.kg password is encrypted at rest. Manager access to credentials/documents requires authentication and is audit logged.
