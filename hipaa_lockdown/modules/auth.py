"""
HIPAA-Lockdown-CLI: Authentication & Identity Management Module
"""
import logging
import os
import re

from hipaa_lockdown.core import safety, system

logger = logging.getLogger(__name__)

def apply_login_defs_policy(filepath: str = '/etc/login.defs'):
    """
    Enforces password aging and hashing requirements in login.defs.
    """
    if not os.path.exists(filepath):
        logger.error(f"{filepath} not found.")
        return

    logger.info(f"Applying HIPAA password policy to {filepath}")
    safety.backup_file(filepath)

    with open(filepath, 'r') as f:
        config = f.read()

    # Enforce PASS_MAX_DAYS
    config = re.sub(r'^\s*PASS_MAX_DAYS\s+\d+', 'PASS_MAX_DAYS   365', config, flags=re.MULTILINE)
    if 'PASS_MAX_DAYS' not in config:
        config += "\nPASS_MAX_DAYS   365\n"

    # Enforce SHA_CRYPT_MIN_ROUNDS
    config = re.sub(r'^\s*SHA_CRYPT_MIN_ROUNDS\s+\d+', 'SHA_CRYPT_MIN_ROUNDS 5000', config, flags=re.MULTILINE)
    if 'SHA_CRYPT_MIN_ROUNDS' not in config:
        config += "\nSHA_CRYPT_MIN_ROUNDS 5000\n"

    with open(filepath, 'w') as f:
        f.write(config)

    logger.info("Password policy applied.")

def apply_system_banners(issue_path: str = '/etc/issue', issuenet_path: str = '/etc/issue.net'):
    """
    Deploys a legally binding banner.
    """
    banner_text = (
        "\n*******************************************************************************\n"
        "*                                                                             *\n"
        "*                                 WARNING                                     *\n"
        "*                                                                             *\n"
        "* This system is restricted to authorized personnel for HIPAA-compliant       *\n"
        "* legal data analysis only. All activities on this system are logged and      *\n"
        "* monitored. Extracted Protected Health Information (PHI) must remain         *\n"
        "* encrypted at rest and in transit.                                           *\n"
        "*                                                                             *\n"
        "* Unauthorized access or use is a violation of federal law and company        *\n"
        "* policy, and may result in disciplinary action or criminal prosecution.      *\n"
        "*                                                                             *\n"
        "*******************************************************************************\n"
    )

    logger.info(f"Deploying HIPAA banners to {issue_path} and {issuenet_path}")
    safety.backup_file(issue_path)
    with open(issue_path, 'w') as f:
        f.write(banner_text)
    
    safety.backup_file(issuenet_path)
    with open(issuenet_path, 'w') as f:
        f.write(banner_text)
        
    logger.info("HIPAA banners deployed.")

def apply_ssh_hardening(filepath: str = '/etc/ssh/sshd_config'):
    """
    Enforces SSH hardening (preferring key-based certs over passwords).
    """
    if not os.path.exists(filepath):
        logger.error(f"{filepath} not found.")
        return

    logger.info(f"Applying SSH hardening to {filepath}")
    safety.backup_file(filepath)

    with open(filepath, 'r') as f:
        config = f.read()

    # Disable password authentication
    config = re.sub(r'^\s*#?\s*PasswordAuthentication\s+(yes|no)', 'PasswordAuthentication no', config, flags=re.MULTILINE)
    if 'PasswordAuthentication no' not in config:
         config += "\nPasswordAuthentication no\n"

    with open(filepath, 'w') as f:
        f.write(config)

    # Note: We aren't reloading sshd here automatically to prevent locking the user out immediately.
    # The user should review configs and reload manually, or we can add a prompt.
    logger.info("SSH policy applied (PasswordAuthentication no). Please restart SSHD for changes to take effect.")

def apply_mfa_policy():
    """
    Configures PAM to require google-authenticator for SSH.
    """
    pam_sshd = '/etc/pam.d/sshd'
    if not os.path.exists(pam_sshd):
        logger.error(f"{pam_sshd} not found.")
        return

    logger.info("Applying MFA policy to SSH PAM configuration.")
    safety.backup_file(pam_sshd)
    
    # Add auth required pam_google_authenticator.so to the top of auth stack
    with open(pam_sshd, 'r') as f:
        config = f.read()
    
    if 'pam_google_authenticator.so' not in config:
        config += "\n# HIPAA-Lockdown: Require Google Authenticator MFA\n"
        config += "auth required pam_google_authenticator.so nullok\n"
        with open(pam_sshd, 'w') as f:
            f.write(config)
        logger.info("MFA requirement added to PAM sshd. Remember to run 'google-authenticator' as your user.")
    else:
        logger.info("PAM MFA already configured in sshd.")
        
    # Also update sshd_config for AuthenticationMethods
    sshd_config = '/etc/ssh/sshd_config'
    if os.path.exists(sshd_config):
        safety.backup_file(sshd_config)
        with open(sshd_config, 'r') as f:
            ssh_conf = f.read()
            
        auth_methods = "AuthenticationMethods publickey,keyboard-interactive"
        ssh_conf = re.sub(r'^\s*#?\s*AuthenticationMethods\s+.*', auth_methods, ssh_conf, flags=re.MULTILINE)
        if auth_methods not in ssh_conf:
            ssh_conf += f"\n{auth_methods}\n"
            
        with open(sshd_config, 'w') as f:
            f.write(ssh_conf)
        logger.info(f"Updated {sshd_config} for MFA AuthenticationMethods.")

def apply_session_timeouts():
    """
    Enforces a strict automatic logoff (15 mins idle) via TMOUT in bash.
    """
    profile_path = '/etc/profile.d/autologout.sh'
    logger.info(f"Applying strict session timeouts (TMOUT=900) to {profile_path}")
    
    with open(profile_path, 'w') as f:
        f.write("#!/bin/sh\n")
        f.write("# HIPAA-Lockdown: Strict Auto-logout after 15 minutes of idle time\n")
        f.write("readonly TMOUT=900\n")
        f.write("export TMOUT\n")
        
    logger.info("Strict session timeout script generated. Will take effect on next login.")

def audit_auth_policies(filepath: str = '/etc/login.defs'):
    """
    Audits login.defs against policy, and checks for MFA/TMOUT setup.
    """
    logger.info(f"Auditing {filepath} for HIPAA compliance...")
    if not os.path.exists(filepath):
        logger.error(f"{filepath} not found.")
        return False

    with open(filepath, 'r') as f:
        config = f.read()

    try:
        max_days_match = re.search(r'^\s*PASS_MAX_DAYS\s+(\d+)', config, flags=re.MULTILINE)
        if max_days_match:
            days = int(max_days_match.group(1))
            if days <= 365:
                 logger.info(f"PASS_MAX_DAYS is compliant: {days} (<= 365)")
            else:
                 logger.warning(f"PASS_MAX_DAYS is currently non-compliant: {days} (> 365)")
        else:
             logger.warning("PASS_MAX_DAYS is not explicitly configured.")

        min_rounds_match = re.search(r'^\s*SHA_CRYPT_MIN_ROUNDS\s+(\d+)', config, flags=re.MULTILINE)
        if min_rounds_match:
            rounds = int(min_rounds_match.group(1))
            if rounds >= 5000:
                 logger.info(f"SHA_CRYPT_MIN_ROUNDS is compliant: {rounds} (>= 5000)")
            else:
                 logger.warning(f"SHA_CRYPT_MIN_ROUNDS is currently non-compliant: {rounds} (< 5000)")
        else:
             logger.warning("SHA_CRYPT_MIN_ROUNDS is not explicitly configured.")

    except Exception as e:
         logger.error(f"Error reading configuration values: {e}")
         
    # Check TMOUT
    if os.path.exists('/etc/profile.d/autologout.sh'):
        logger.info("Strict session timeout (TMOUT) profile exists.")
    else:
        logger.warning("Strict session timeout (TMOUT) profile is MISSING.")
        
    # Check PAM MFA
    if os.path.exists('/etc/pam.d/sshd'):
        with open('/etc/pam.d/sshd', 'r') as f:
            if 'pam_google_authenticator.so' in f.read():
                logger.info("PAM Google Authenticator MFA is configured for SSH.")
            else:
                logger.warning("PAM Google Authenticator MFA is NOT configured for SSH.")

# Entry points via argparse
def run_apply():
    apply_login_defs_policy()
    apply_system_banners()
    apply_ssh_hardening()
    apply_mfa_policy()
    apply_session_timeouts()

def run_audit():
    audit_auth_policies()

def run_rollback():
    logger.info("Rollback not fully implemented for auth module yet. Implement looking for .bak files.")
