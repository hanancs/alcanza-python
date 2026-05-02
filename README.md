# alcanza-check 🔍

A fast, beautiful, and comprehensive network connectivity checker CLI (Python version).

`alcanza-check` helps you verify if an application is reachable by running multiple checks in parallel:
- **ICMP Ping**: Checks if the host responds to pings.
- **DNS Lookup**: Verifies if the hostname resolves to an IP.
- **TCP Connection**: Checks if a specific port is open.
- **SSL/TLS Validation**: Verifies the validity of the SSL certificate.

## Installation

You can install it via pip:

```bash
pip install alcanza-check
```

## Usage

```bash
alcanza-check <host> [port]
```

Default port is `443` if not specified.

### Example

```bash
alcanza-check google.com 443
```

## Development

1. Clone the repo
2. Install dependencies: `pip install rich`
3. Install in editable mode: `pip install -e .`
4. Run: `alcanza-check <host> [port]`

## License

MIT
