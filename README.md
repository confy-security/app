<h1 align="center">
  <a href="https://github.com/confy-security/app" target="_blank" rel="noopener noreferrer">
    <picture>
      <img width="80" src="confy/assets/icon.png">
    </picture>
  </a>
  <br>
  Confy Desktop
</h1>

<p align="center">Desktop application for the Confy encrypted communication system.</p>

<div align="center">

[![Build](https://github.com/confy-security/app/actions/workflows/build.yml/badge.svg)](https://github.com/confy-security/app/actions/workflows/build.yml)
[![GitHub Release](https://img.shields.io/github/v/release/confy-security/app)](https://github.com/confy-security/cli/releases)
[![GitHub License](https://img.shields.io/github/license/confy-security/app?color=blue)](/LICENSE)
[![Visitors](https://api.visitorbadge.io/api/visitors?path=confy-security%2Fapp&label=repository%20visits&countColor=%231182c3&style=flat)](https://github.com/confy-security/app)

<img width="722" height="659" alt="image" src="https://github.com/user-attachments/assets/e890fa76-fc71-481e-803d-a87d262a699c" />

</div>

---

A secure desktop application for peer-to-peer encrypted messaging using the Confy communication system. This desktop client provides a user-friendly graphical interface for establishing encrypted connections with other peers, exchanging cryptographic keys, and communicating with end-to-end encryption using industry-standard algorithms.

Learn more about the project at [github.com/confy-security](https://github.com/confy-security)

Made with dedication by students from Brazil 🇧🇷.

## ⚡ Features

- **End-to-End Encryption** - Messages are encrypted using AES-256 in CFB mode
- **Digital Signatures** - Messages are signed using RSA with PSS padding for authenticity
- **Secure Key Exchange** - RSA-4096 key exchange with OAEP padding
- **Modern UI** - Intuitive desktop interface for secure messaging
- **Debug Mode** - Detailed logging for troubleshooting and development
- **Cross-Platform** - Works on Windows, macOS, and Linux
- **WebSocket Support** - Secure peer-to-peer communication over WebSocket (WSS)

## ⚙️ Requirements

- **Python:** 3.13 or higher
- **OS:** Windows, macOS, or Linux
- **RAM:** Minimum 4GB recommended
- **Disk Space:** 200MB for application and dependencies

## 📦 Installation

### From Source

Clone the repository and install dependencies using Poetry:

```bash
git clone https://github.com/confy-security/app.git
cd app
poetry install
```

Then run the application:

```bash
poetry run confy-desktop
```

Or use the task runner:

```bash
task run
```

### Building Executables

To build a standalone executable for your platform:

```bash
task build
```

The executable will be created in the `dist/` directory.

### Packaging as Native Binary

To package the application as a native binary for your operating system:

```bash
task package
```

This creates a platform-specific package that can be distributed independently.

## 🚀 Quick Start

### Setup Development Environment

#### 1. Clone the Repository

```bash
git clone https://github.com/confy-security/app.git
cd app
```

#### 2. Install Required Tools

Ensure you have the following installed:

- [GIT](https://git-scm.com/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Python 3.13.7](https://www.python.org/downloads/)

> [!IMPORTANT]
> Due to application dependencies, we recommend using specifically Python 3.13.7 during development.

#### 3. Configure Poetry

```bash
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
```

This creates the virtual environment in a `.venv` directory within the project.

#### 4. Install Dependencies

```bash
poetry install
```

#### 5. Activate Virtual Environment

On Windows:

```bash
.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

Now you're ready to start developing! 🎉

## 🔒 Security Architecture

### Key Exchange Process

1. **RSA Key Generation** - Each client generates a 4096-bit RSA key pair
2. **Public Key Exchange** - Public keys are exchanged securely over WebSocket
3. **AES Key Generation** - A random 256-bit AES key is generated
4. **Encrypted Key Distribution** - AES key is encrypted with peer's RSA public key
5. **Secure Communication** - All messages are encrypted with the shared AES key and signed

### Encryption Details

- **Message Encryption** - AES-256 in CFB mode
- **Key Encryption** - RSA-4096 with OAEP padding
- **Signatures** - RSA-4096 with PSS padding and SHA-256
- **Cryptography Library** - Uses the `cryptography` library (actively maintained)

## 📚 Environment Variables

Configure the application using environment variables:

```bash
# Enable debug mode for detailed logging
export DEBUG=true

# Or create a .env file
echo "DEBUG=false" > .env
```

Create a `.env` file in your project root:

```env
DEBUG=false
```

## 🔧 Configuration

### Server Connection

Configure the server address in the application settings:

- **Secure WebSocket** - `wss://example.com` (recommended)
- **WebSocket** - `ws://example.com` (use only for testing)
- **HTTPS** - `https://example.com` (automatically converts to WSS)
- **HTTP** - `http://example.com` (automatically converts to WS)

### Connection History

The application stores your connection history for quick access to previously used servers.

## 🛠️ Useful Commands

Once you have the development environment set up, you can use these commands:

| Command | Description |
|---------|-------------|
| `task run` | Run the application |
| `task test` | Execute tests |
| `task build` | Build the application |
| `task package` | Package as native binary |
| `task lint` | Check code quality |
| `task format` | Format code |
| `task mypy` | Run type checking |
| `task radon` | Check code complexity |
| `task bandit` | Security analysis |

> [!NOTE]
> Make sure the virtual environment is activated before running these commands.

## 🛠️ Troubleshooting

### Connection Issues

**"Error connecting to server"**

- Verify the server address is correct
- Ensure the server is running and accessible
- Check your network connectivity
- For WSS connections, verify the SSL certificate is valid

**"Connection refused"**

- Confirm the server is listening on the specified address and port
- Check if a firewall is blocking the connection

### Message Issues

**"AES key has not been established yet"**

- Wait a moment for the key exchange to complete
- Ensure both peers are connected
- Check if the server is properly relaying messages

**"Failed to encrypt/verify message"**

- This indicates an issue with the encryption layer
- Try reconnecting to the server
- Check if both peers are running compatible application versions

### Performance Issues

**Slow response times or freezing**

- Check your network latency to the server
- Consider using a server closer to your location
- Check system resources (RAM, CPU)
- Try restarting the application

## 📖 Usage Guide

### Connecting to a Peer

1. Launch the application
2. Enter your user ID
3. Enter the recipient's user ID
4. Configure the server address
5. Click "Connect"

### Sending Messages

1. Once connected, type your message in the message input field
2. Press Enter or click "Send"
3. Your message will be encrypted and transmitted securely

### Security Considerations

1. **Verify Recipients** - Ensure you're communicating with the intended person
2. **Secure Connections** - Always use WSS (WebSocket Secure) in production
3. **User ID Security** - Store your user ID securely
4. **Session Management** - Disconnect when finished communicating

### Advanced Usage

#### Debug Mode

Enable debug mode to see detailed information:

```bash
DEBUG=true task run
```

This will display:

- Key exchange details
- Message encryption/decryption information
- Connection status changes
- Signature verification steps

#### Custom Server Configuration

Configure a custom server address in the application settings or environment:

```bash
SERVER_URL=wss://custom-server.com:8080 task run
```

## 🤝 Dependencies

Confy Desktop relies on well-maintained and secure libraries:

- **Desktop Framework** - Modern Python UI framework for cross-platform development
- **WebSocket Support** - Secure peer-to-peer communication
- **Encryption** - Industry-standard cryptographic primitives
- **Configuration** - Settings management and environment variables

All dependencies are installed automatically with Poetry.

## 🧪 Testing

Run the test suite:

```bash
task test
```

Run tests with coverage:

```bash
task test --cov
```

## 🐛 Bug Reports

If you encounter any issues, please report them:

1. Check if the issue already exists on [GitHub Issues](https://github.com/confy-security/app/issues)
2. Provide clear reproduction steps
3. Include your Python version and OS
4. Attach relevant logs with `DEBUG=true`

See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## 🔐 Security Policy

For security vulnerabilities, please follow responsible disclosure:

**DO NOT** open a public GitHub issue.

Instead, email: [confy@henriquesebastiao.com](mailto:confy@henriquesebastiao.com)

See [SECURITY.md](SECURITY.md) for detailed information.

## 📝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Setting up the development environment
- Code standards and style guidelines
- Testing requirements
- Pull request process

## 📄 License

Confy Desktop is open source software licensed under the [GPL-3.0](https://github.com/confy-security/app/blob/main/LICENSE) license.

## 📚 Additional Resources

- **Confy Security** - [github.com/confy-security](https://github.com/confy-security)
- **Contributing Guide** - [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security Policy** - [SECURITY.md](SECURITY.md)
- **Code of Conduct** - [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **CLI Client** - [github.com/confy-security/cli](https://github.com/confy-security/cli)

## 🙋 Support

For questions and support:

- Check existing issues and discussions on GitHub
- Review the [CONTRIBUTING.md](CONTRIBUTING.md) guide
- Contact the team at [confy@henriquesebastiao.com](mailto:confy@henriquesebastiao.com)

## Acknowledgments

This project was created with dedication by Brazilian students 🇧🇷 as part of the Confy Security initiative.

**Built with ❤️ by the Confy Security Team**