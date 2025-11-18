# Security Policy

## Supported Versions

We take security seriously in DVOACAP-Python. The following versions are currently supported with security updates:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 1.0.x   | :white_check_mark: | Production - Active support |
| < 1.0   | :x:                | Pre-release - No longer supported |

## Reporting a Vulnerability

If you discover a security vulnerability in DVOACAP-Python, please help us maintain the security of this project by reporting it responsibly.

### How to Report

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report security issues privately using one of these methods:

1. **Email:** skyelaird@users.noreply.github.com
   - Subject: "[SECURITY] DVOACAP-Python Vulnerability Report"
   - Include detailed information (see below)

2. **GitHub Private Vulnerability Reporting:**
   - Navigate to the Security tab
   - Click "Report a vulnerability"
   - Fill out the vulnerability report form

### What to Include

When reporting a vulnerability, please include as much information as possible:

- **Description:** Clear description of the vulnerability
- **Impact:** Potential security impact and affected components
- **Steps to Reproduce:** Detailed steps to reproduce the vulnerability
- **Affected Versions:** Which versions of DVOACAP-Python are affected
- **Proof of Concept:** Code samples or test cases demonstrating the issue
- **Suggested Fix:** If you have ideas for how to address the issue (optional)
- **Environment:** Python version, OS, dependencies versions

### Example Report

```markdown
**Vulnerability Type:** Arbitrary Code Execution / Injection / etc.

**Description:**
The prediction engine accepts user input that is passed directly to...

**Steps to Reproduce:**
1. Import dvoacap
2. Call function with malicious input: `...`
3. Observe unexpected behavior

**Impact:**
An attacker could potentially...

**Affected Versions:**
- 1.0.0
- 0.9.0

**Suggested Fix:**
Input validation should be added to...
```

## What to Expect

### Response Timeline

- **Initial Response:** Within 48 hours of report
- **Status Update:** Within 7 days with assessment of the vulnerability
- **Fix Timeline:** Varies based on severity (see below)
- **Public Disclosure:** Coordinated with reporter after fix is released

### Severity Levels

| Severity | Response Time | Examples |
|----------|--------------|----------|
| **Critical** | 1-3 days | Remote code execution, authentication bypass |
| **High** | 7-14 days | Injection vulnerabilities, privilege escalation |
| **Medium** | 30 days | Information disclosure, DoS conditions |
| **Low** | 90 days | Minor issues with minimal security impact |

## Security Best Practices for Users

### Safe Usage

1. **Input Validation:**
   - Always validate user inputs before passing to prediction engine
   - Sanitize geographic coordinates and frequency values
   - Validate file paths if loading custom coefficient data

2. **Dependency Management:**
   - Keep DVOACAP-Python and dependencies up to date
   - Regularly check for security advisories: `pip list --outdated`
   - Use virtual environments to isolate dependencies

3. **Web Integration:**
   - If using in a web application, implement proper input validation
   - Use CSRF protection and rate limiting
   - Sanitize outputs before displaying in HTML
   - Never execute user-provided code

### Example: Safe Input Validation

```python
from dvoacap import GeoPoint

def safe_create_location(lat: float, lon: float) -> GeoPoint:
    """Safely create a GeoPoint with validated inputs."""
    # Validate latitude
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")

    # Validate longitude
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")

    return GeoPoint.from_degrees(lat, lon)
```

## Known Security Considerations

### Current Scope

DVOACAP-Python is a **scientific computation library** for HF propagation prediction. It:

- ✅ Performs mathematical calculations on ionospheric data
- ✅ Reads coefficient data files from trusted sources
- ✅ Generates predictions based on validated algorithms

It does **NOT**:

- ❌ Execute arbitrary code
- ❌ Make network requests (core library)
- ❌ Access system files outside data directory
- ❌ Require elevated privileges

### Dashboard Security

The optional Flask dashboard (`Dashboard/server.py`) provides a web interface:

- **Intended use:** Local development or trusted networks
- **Not recommended:** Direct internet exposure without additional security
- **Suggestions if deploying publicly:**
  - Use authentication (OAuth, API keys, etc.)
  - Implement rate limiting
  - Run behind reverse proxy (nginx, Apache)
  - Use HTTPS
  - Validate and sanitize all inputs
  - Implement CORS policies

## Security Update Process

When a security vulnerability is confirmed:

1. **Assessment:** Evaluate severity and impact
2. **Development:** Create fix in private branch
3. **Testing:** Verify fix resolves issue without breaking functionality
4. **Release:** Publish security update with advisory
5. **Notification:** Notify users through:
   - GitHub Security Advisory
   - Release notes
   - CHANGELOG.md
   - Email to reporter
6. **Disclosure:** Publish details after users have time to update

## Contact

- **Security Issues:** skyelaird@users.noreply.github.com (private)
- **General Issues:** https://github.com/skyelaird/dvoacap-python/issues (public)
- **Maintainer:** Joel Morin

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who report vulnerabilities:

- Your name/handle will be credited in release notes (unless you prefer anonymity)
- We may offer recognition in CHANGELOG.md and security advisories

---

**Last Updated:** November 18, 2025
**Version:** 1.0

Thank you for helping keep DVOACAP-Python and its users safe! 🔒
