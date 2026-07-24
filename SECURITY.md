# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in deuseek, please **do not** open a public issue.

Instead, please report it via one of:

- **Email**: [Report via GitHub Security Advisory](https://github.com/xyva-yuangui/deuseek/security/advisories/new)
- **GitHub Private Vulnerability Reporting**: Go to the [Security tab](https://github.com/xyva-yuangui/deuseek/security) and click "Report a vulnerability"

We aim to respond within 48 hours and will keep you updated on the fix timeline.

## Scope

deuseek is a CLI tool that:
- Makes outbound HTTP requests to search APIs and web pages
- Shells out to upstream binaries (`yt-dlp`, `gh`, `rdt-cli`, `opencli`)
- Reads and writes local files in `~/.deuseek/` (cache, preferences, DomainKB)

Areas of concern:
- **URL handling**: deuseek fetches arbitrary URLs provided by the user or agent. While it uses Scrapling's `Fetcher`/`StealthyFetcher`/`DynamicFetcher` for sandboxed requests, malicious URLs could potentially exploit browser engine vulnerabilities (especially in `patchright`/`playwright` paths).
- **Subprocess arguments**: deuseek passes user-provided query strings and URLs to upstream binaries. All inputs are sanitized, but edge cases in upstream binaries could be a concern.
- **Local file permissions**: `~/.deuseek/secrets.env` should be `chmod 600` (POSIX) — the secrets loader warns on loose permissions.

## Supported versions

| Version | Supported |
|---|---|
| `1.0.0-alpha` (latest) | ✅ |
| Older / unreleased | ❌ |

## Acknowledgments

We appreciate responsible disclosure. Security researchers who report valid vulnerabilities will be acknowledged here (with permission).