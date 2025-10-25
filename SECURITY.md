# Security Policy

Security is very important to Confy App. If you discover a security vulnerability, please report it responsibly to us immediately.

## Reporting a Vulnerability

⚠️ **Important**

DO NOT open a public GitHub issue for security vulnerabilities. Public disclosure can put the entire community at risk. Instead, please follow the responsible disclosure process outlined below.

## How to Report a Security Vulnerability

### Step 1: Send a Report

Send an email to: [confy@henriquesebastiao.com](mailto:confy@henriquesebastiao.com)

Include the following information in your report:

**Subject:** `[SECURITY] Vulnerability Report - Confy App`

1. Type of vulnerability (e.g., credential exposure, authentication bypass, network interception)
2. Description of the vulnerability
3. Location in the code (file path, function name, line numbers if possible)
4. Steps to reproduce the issue
5. Proof of concept or sample code (if applicable)
6. Expected vs. actual behavior
7. Potential impact and severity
8. Your contact information (optional, but recommended)

### Step 2: What to Include

To help us understand and address the vulnerability faster, please provide:

- **Detailed description:** What is the vulnerability and how does it manifest?
- **Affected versions:** Which versions of Confy App are affected?
- **Reproduction steps:** Provide clear, step-by-step instructions to reproduce the issue
- **Code sample:** Include sample code or configuration that demonstrates the vulnerability
- **Impact assessment:** Explain what an attacker could do with this vulnerability
- **Suggested fix:** If you have an idea for a patch, please share it
- **Your research:** Include any relevant research or references

### Step 3: Response Timeline

- **24 hours:** We acknowledge receipt of your report
- **72 hours:** We provide an initial assessment and may request clarification
- **7 days:** We confirm the vulnerability status
- **14 days:** We provide an estimated patch timeline
- **Ongoing:** Regular updates on progress

## What Happens After You Report

### Investigation Process

1. **Acknowledgment** - We confirm receipt of your report within 24 hours
2. **Analysis** - Our security team analyzes the vulnerability
3. **Verification** - We verify the vulnerability in our codebase
4. **Development** - We develop and test a fix
5. **Release** - We release a patched version
6. **Disclosure** - We publicly disclose the vulnerability and credit you (if desired)

### Communication

- We will keep you informed throughout the process
- We will discuss the vulnerability details only with those who need to know
- We will not disclose your identity without permission
- We will ask for your consent before crediting you publicly

## Vulnerability Disclosure Timeline

### Embargo Period

After we acknowledge a vulnerability report, we enforce an embargo period:

- **Critical vulnerabilities:** 30 days maximum before public disclosure
- **High severity vulnerabilities:** 45 days maximum before public disclosure
- **Medium severity vulnerabilities:** 60 days maximum before public disclosure
- **Low severity vulnerabilities:** 90 days maximum before public disclosure

During this period, we request that you do not publicly disclose the vulnerability.

### Public Disclosure

After the embargo period or when a patch is released (whichever comes first), we will:

1. Release a security patch
2. Publish a security advisory
3. Credit the reporter (with permission)
4. Provide mitigation guidance for users who cannot update immediately

## Supported Versions

### Version Support Timeline

We provide security updates for:

| Version | Release Date | End of Support | Status |
|---------|--------------|----------------|--------|
| 0.1.x | 2025-11-22 | TBD | Actively supported |

### Dependency Support

We actively maintain security for:

- Python: 3.13+
- PySide6: Latest version
- cryptography: Latest version
- pydantic-settings: Latest version
- confy-addons: Latest version (currently 1.1.0+)

Security updates will be provided for the last 2 minor versions of each major dependency.

## Known Security Considerations

### GUI Security

Confy App uses a modern desktop GUI built with PySide6. Users should be aware:

- ✔️ We use the cryptography library - Actively maintained and regularly audited
- ✔️ We implement best practices - RSA-OAEP and AES-256-CFB encryption
- ⚠️ Server certificates are your responsibility - Use HTTPS/WSS for server connections
- ⚠️ Key management is critical - Securely handle RSA private keys

### Credential Handling

The application handles sensitive cryptographic material:

- Never log cryptographic keys or private data
- Always use secure key storage mechanisms
- Rotate keys regularly
- Use environment variables for configuration (not hardcoded values)

### Network Security

When using Confy App:

- Always connect to trusted servers
- Use HTTPS/WSS for all connections (never unencrypted HTTP/WS)
- Verify server SSL certificates
- Be cautious of man-in-the-middle attacks

### Dependency Security

We actively monitor our dependencies for security vulnerabilities:

- Dependabot - Automated dependency monitoring (daily checks)
- Manual audits - Regular security reviews
- Rapid patching - Quick updates when vulnerabilities are discovered

## Security Best Practices for Users

### When Using Confy App

1. Keep software updated - Run the latest version of Confy App
2. Update dependencies - Keep Python and all packages up to date
3. Use strong identifiers - Choose unique, non-guessable user IDs
4. Secure storage - Store private keys in secure locations
5. Network security - Always use encrypted connections (WSS, not WS)
6. Verify peers - Confirm you're communicating with the right person
7. Monitor activity - Watch for suspicious connection attempts
8. Use backups - Maintain encrypted backups of important keys

### Key Management

```bash
# ✅ Good: Use environment variables for sensitive data
export CONFY_USER_ID="your-secure-id"
```

```bash
# ❌ Bad: Don't hardcode sensitive information
# Avoid storing user IDs and keys directly in the application configuration
```

### Server Configuration

```bash
# ✅ Good: Use secure WSS connections
# Configure the app to connect to: wss://secure-server.com
```

```bash
# ❌ Bad: Use unencrypted connections
# NEVER use: ws://insecure-server.com
```

## Security Features

### What Confy App Provides

- **End-to-end encryption** - Messages encrypted with AES-256
- **Digital signatures** - RSA-based message authentication
- **Key exchange** - Secure RSA key exchange (4096-bit keys)
- **Session isolation** - Separate keys for each conversation
- **Input validation** - Validation of all received messages
- **Error handling** - Secure error messages without leaking information

### What Confy App Does NOT Provide

- ❌ Perfect forward secrecy - Keys are not rotated per message
- ❌ Offline message queuing - Messages are lost if recipient is offline
- ❌ Message timestamps - No cryptographic timestamps
- ❌ Deniability - Messages can be attributed to the sender
- ❌ Metadata encryption - User IDs are visible to the server
- ❌ Multi-device sync - Keys are not synced across devices

For these features, consider using additional tools alongside Confy App.

## Responsible Disclosure Examples

### ✅ Responsible Disclosure

- Email the security team privately
- Provide clear reproduction steps
- Give reasonable time to patch
- Don't share exploit code publicly
- Wait for a patch before public disclosure

### ❌ Irresponsible Disclosure

- Posting vulnerability details on social media
- Opening a public GitHub issue
- Sharing exploit code publicly
- Demanding immediate payment or recognition
- Ignoring the reporting process

## Security Audit Trail

### Changes to Security Policy

| Date | Change | Version |
|------|--------|---------|
| 2025-11-22 | Initial security policy | 0.1.0 |

### Security Updates Released

We will maintain a log of security updates here.

## Dependencies Security

### Direct Dependencies

- PySide6 - GUI framework, actively maintained
- cryptography - Encryption library, security-focused
- websockets - WebSocket protocol, security updates available
- pydantic-settings - Configuration management, regularly updated
- confy-addons - Encryption components, security-focused

### Updating Dependencies

```bash
# Update all dependencies to latest versions
pip install --upgrade -r requirements.txt
```

```bash
# Update a specific package
pip install --upgrade PySide6
```

## Security Testing

### Our Security Testing Process

1. Static Analysis - Bandit for security code analysis
2. Type Checking - MyPy to catch type-related security issues
3. Code Quality - Ruff for code pattern issues
4. Dependency Scanning - Dependabot for vulnerable dependencies
5. Code Review - Manual security review of all changes

### Running Security Tests Locally

```bash
# Run security analysis with Bandit
bandit -r ./confy

# Check types with MyPy
mypy ./confy

# Run all quality checks
ruff check .
```

## Incident Response

### Security Incident Response Plan

If a security vulnerability is found in production:

1. **Immediate Response (0-2 hours)**
   - Assemble the security response team
   - Assess the vulnerability severity
   - Determine immediate mitigation steps

2. **Triage (2-24 hours)**
   - Verify the vulnerability
   - Identify all affected versions
   - Assess real-world impact

3. **Development (24-72 hours)**
   - Develop a fix or workaround
   - Create comprehensive tests
   - Prepare patches for all affected versions

4. **Release (as soon as ready)**
   - Release security patch
   - Notify users immediately
   - Provide upgrade guidance

5. **Post-Incident (1-2 weeks)**
   - Conduct root cause analysis
   - Improve processes to prevent recurrence
   - Publish security advisory

## Contact Information

### Security Team

- Email: [confy@henriquesebastiao.com](mailto:confy@henriquesebastiao.com)
- GitHub: [@confy-security](https://github.com/confy-security)
- Response Time: Within 24 hours for initial acknowledgment

### Vulnerability Disclosure

For responsible disclosure of security vulnerabilities, please follow the guidelines in this document.

## Transparency and Accountability

We are committed to:

- **Transparency** - Being honest about security issues and fixes
- **Accountability** - Taking responsibility for addressing vulnerabilities
- **Timeliness** - Responding promptly to security reports
- **Fairness** - Treating all reporters with respect and fairness
- **Collaboration** - Working with the community to improve security

## Frequently Asked Questions

### Q: Is Confy App suitable for production use?

A: Yes, Confy App is designed for production use. However, like all security-critical software, it should be:

- Regularly updated
- Integrated with other security measures
- Thoroughly tested in your environment
- Deployed with appropriate operational security practices

### Q: How often are security updates released?

A: Security updates are released as needed when vulnerabilities are discovered and fixed. We typically aim to release patches within 30 days of discovering a critical vulnerability.

### Q: Can I audit the code?

A: Yes! The code is open source and available on GitHub. You're welcome to conduct your own security audit. If you find something concerning, please report it responsibly using the process in this document.

### Q: What if I accidentally expose a private key?

A:

1. Contact us immediately at [confy@henriquesebastiao.com](mailto:confy@henriquesebastiao.com)
2. Rotate the key immediately
3. Do not attempt to remove it from version history alone (it may still be accessible)
4. We can help guide you through the remediation process

### Q: Where should I report a vulnerability?

A: Email [confy@henriquesebastiao.com](mailto:confy@henriquesebastiao.com) with details of the vulnerability. Do NOT open a public GitHub issue.

### Q: What if I'm unsure whether something is a security issue?

A: When in doubt, please report it to [confy@henriquesebastiao.com](mailto:confy@henriquesebastiao.com). We'd rather receive false alarms than miss actual security issues. We promise to treat your report confidentially.

## Additional Resources

- [OWASP Security Guidelines](https://owasp.org/)
- [Cryptography Best Practices](https://cryptography.io/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [Responsible Disclosure](https://www.eff.org/deeplinks/2019/10/what-responsible-disclosure)

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-11-24 | Initial security policy |

## Acknowledgments

We thank all security researchers and community members who help make Confy App more secure.

If you've responsibly disclosed a security vulnerability to us and would like to be credited, please let us know, and we'll include you in our security advisory.

---

Last Updated: November 24, 2025

Next Review: November 24, 2026

Built with ❤️ by the Confy Security Team
