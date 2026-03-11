# HIPAA Compliance Tool

A modular CLI and GUI tool designed to autonomously harden Linux workstations (specifically Ubuntu/Debian) for HIPAA-compliant legal data processing.

## Features

- **Authentication & Identity Management**: Enforces password aging, increases hashing strength, and deploys legally binding login banners.
- **Filesystem & Privacy**: Forces system-wide private umask (`027`) and restricts compiler execution to root.
- **Auditing & Accountability**: Ensures `auditd` is active and implements immutable watches on critical system files.
- **Network Security**: Hardens DNS settings, blacklists risky protocols, and applies kernel-level security tweaks.
- **HIPAA Mapping**: Directly maps technical controls to HIPAA Technical Safeguards (§164.312).

## Installation

### Prerequisites

- Ubuntu 24.04 LTS or 25.10 (recommended)
- Python 3.10+
- `sudo` privileges for applying system changes

### Installation from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/famousshea/hipaa-compliance-tool.git
   cd hipaa-compliance-tool
   ```

2. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
   ```

3. Create a virtual environment:
   ```bash
   python3 -m venv --system-site-packages venv
   source venv/bin/activate
   ```

## Usage

### CLI Tool
Run the compliance auditor and hardener:
```bash
sudo ./venv/bin/python3 hipaa_lockdown/main.py
```

### GUI Application
Launch the GTK4-based dashboard:
```bash
./venv/bin/python3 hipaa_lockdown/gui.py
```

## Building Standalone Executables

This project includes scripts to build standalone, USB-runnable executables using PyInstaller.

### Local Build
```bash
./build.sh
```
The binaries will be located in the `dist/` directory.

### Containerized Build (for LTS Compatibility)
To ensure the binaries work on older Ubuntu versions (like 24.04 LTS) regardless of your host system:
```bash
./build_container.sh
```

## HIPAA Context

This tool implements safeguards as defined in the HIPAA Security Rule:
- **Access Control §164.312(a)(1)**: Via Umask and Restricted Permissions.
- **Audit Controls §164.312(b)**: Via `auditd` and critical file monitoring.
- **Integrity §164.312(c)(1)**: Via monitoring of authentication files and restricted compilers.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
