# Project: HIPAA-Lockdown-CLI
**Status:** Initial Specification / Design Phase
**Target Platform:** Ubuntu/Debian Linux (GNOME/Wayland Native)
**Objective:** Create a modular CLI tool to autonomously harden a Linux workstation for HIPAA-compliant legal data processing.

---

## 1. Core Functional Requirements
The tool must automate the following security domains, which have been verified on the primary development machine (Ubuntu 25.10):

### A. Authentication & Identity Management
- **Password Aging:** Enforce a maximum password age of 365 days (`PASS_MAX_DAYS`).
- **Hashing Strength:** Increase `SHA_CRYPT_MIN_ROUNDS` to 5000 in `/etc/login.defs`.
- **System Banners:** Deploy a legally binding login banner to `/etc/issue` and `/etc/issue.net` stating the system is for HIPAA-compliant legal data analysis.

### B. Filesystem & Privacy
- **Default Umask:** Force a system-wide `UMASK 027` to ensure new files are private by default (Owner: RWX, Group: R-X, Others: ---).
- **Compiler Restriction:** Restrict execution of `gcc`, `g++`, and `make` to the root user (`chmod 700`) to prevent local exploit compilation.

### C. Auditing & Accountability (The "Audit Trail")
- **Service:** Ensure `auditd` is installed and active.
- **Monitoring Rules:** Implement immutable watches (`-e 2`) on critical files:
    - `/etc/passwd`, `/etc/shadow`, `/etc/sudoers`
    - Login logs (`/var/log/lastlog`, `/var/log/faillog`)
- **Keying:** Tag all audit events with specific keys (e.g., `auth_changes`, `logins`) for easy filtering via `ausearch`.

### D. Network Security
- **DNS Hardening:** Detect and remove non-responding or "dead" nameservers from Netplan and `systemd-resolved`.
- **Protocol Blacklisting:** Disable unused/risky protocols (DCCP, SCTP, RDS, TIPC) via `modprobe` blacklisting.
- **Kernel Tweaks:** Enable IP Spoofing protection (`rp_filter`) and disable ICMP redirects.

---

## 2. Technical Implementation Strategy for the Agent
- **Verification First:** The program must use `grep` and `resolvectl` to check current states before applying changes.
- **Non-Destructive Editing:** Use `sed` or targeted line replacement instead of overwriting entire config files to preserve user settings.
- **Validation Loop:** After every change, the tool must run a validation check (e.g., `auditctl -l` or `sysctl -p`) to confirm the setting "stuck."
- **Rollback Capability:** The tool should create timestamped backups (e.g., `.bak`) of any file in `/etc/` before modification.

---

## 3. HIPAA Context for the Agent
- **Technical Safeguard §164.312(a)(1):** Access Control (Implemented via Umask/Permissions).
- **Technical Safeguard §164.312(b):** Audit Controls (Implemented via Auditd).
- **Technical Safeguard §164.312(c)(1):** Integrity (Implemented via restricted compilers and monitoring of auth files).

---

## 4. Design Philosophy
- **Lightweight-First:** Favor native system tools (`systemd`, `netplan`, `auditd`) over heavy third-party agents.
- **Professional but Human:** Maintain a serious security posture but allow for customized, human-readable banners.
- **Autonomy:** The tool should be capable of running "Quick Audits" (similar to Lynis) to report on compliance status without making changes unless directed.
