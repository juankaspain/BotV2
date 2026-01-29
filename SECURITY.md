# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability within BotV2, please send an email to the maintainers. All security vulnerabilities will be promptly addressed.

### How to Report

1. **Email**: Open a private security advisory at [GitHub Security Advisories](https://github.com/juankaspain/BotV2/security/advisories/new)
2. **Include**:
   - Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
   - Full paths of source file(s) related to the issue
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Any special configuration required to reproduce the issue
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Status Update**: Within 7 days with our assessment
- **Resolution Timeline**: We aim to resolve critical issues within 30 days

## Security Best Practices

When using BotV2, please follow these security guidelines:

### API Keys & Secrets

- **Never commit** API keys or secrets to version control
- Use environment variables or `.env` files (excluded from git)
- Rotate API keys regularly
- Use read-only API keys when possible for testing

### Deployment

- Run in isolated environments (Docker recommended)
- Use HTTPS for all external communications
- Enable JWT authentication for dashboard access
- Configure IP whitelisting when possible
- Keep dependencies up to date

### Access Control

- Use strong, unique passwords for dashboard access
- Enable rate limiting (configured by default)
- Review access logs regularly
- Limit API permissions to minimum required

## Security Features

BotV2 includes several built-in security features:

| Feature | Description |
| ------- | ----------- |
| JWT Authentication | Secure token-based auth for dashboard |
| Rate Limiting | 60 requests/minute default limit |
| HTTPS Support | TLS encryption for all communications |
| Input Validation | Sanitization of all user inputs |
| Secrets Encryption | Sensitive data encrypted at rest |
| Access Logging | Comprehensive audit trail |

## Responsible Disclosure

We kindly ask that you:

- Give us reasonable time to address the issue before public disclosure
- Make a good faith effort to avoid privacy violations and data destruction
- Do not access or modify data that does not belong to you

## Recognition

We appreciate the security research community's efforts in helping keep BotV2 secure. Contributors who report valid security issues will be acknowledged in our release notes (unless they prefer to remain anonymous).

---

Thank you for helping keep BotV2 and its users safe!
