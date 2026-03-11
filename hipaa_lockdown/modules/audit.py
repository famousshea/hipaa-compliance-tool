"""
HIPAA-Lockdown-CLI: Auditing & Accountability Module
"""
import logging
import os

from hipaa_lockdown.core import system

logger = logging.getLogger(__name__)

def verify_auditd_status():
    """
    Checks if auditd is running and enabled.
    """
    logger.info("Verifying auditd status...")
    if system.is_service_active('auditd'):
        logger.info("auditd is active and running.")
        return True
    else:
        logger.warning("auditd is NOT active.")
        return False

def verify_aide_status():
    """
    Checks if AIDE (File Integrity Monitoring) is installed.
    """
    logger.info("Verifying AIDE status...")
    if os.path.exists('/usr/sbin/aide'):
        logger.info("AIDE is installed.")
        return True
    else:
        logger.warning("AIDE is NOT installed. File Integrity Monitoring may be compromised.")
        return False

def apply_auditd_rules():
    """
    Applies immutable watches to critical authentication paths.
    """
    rules_path = '/etc/audit/rules.d/hipaa.rules'
    logger.info(f"Deploying auditd rules to {rules_path}")
    
    # We do not backup the rules file if it doesn't exist, we just create it
    # If it exists, we could back it up, but usually we just overwrite our specific custom file
    
    rules = """
# HIPAA-Lockdown: Audit Rules
# Monitoring Authentication Logs
-w /var/log/lastlog -p wa -k logins
-w /var/log/faillog -p wa -k logins

# Monitoring Identity Files
-w /etc/passwd -p wa -k auth_changes
-w /etc/shadow -p wa -k auth_changes
-w /etc/sudoers -p wa -k auth_changes

# Make the configuration immutable (requires reboot to change)
-e 2
"""
    try:
        with open(rules_path, 'w') as f:
            f.write(rules.strip() + '\n')
        logger.info(f"Successfully wrote {rules_path}")
        
        # Reload auditd rules
        logger.info("Reloading auditd rules using augenrules...")
        system.run_command(['augenrules', '--load'], check=False)
        
    except Exception as e:
        logger.error(f"Failed to apply auditd rules: {e}")

def initialize_aide():
    """
    Initializes the AIDE database if it doesn't exist, which is a slow process.
    """
    logger.info("Checking AIDE database initialization...")
    if not os.path.exists('/usr/sbin/aide'):
        logger.error("Cannot initialize AIDE; aide is not installed.")
        return
        
    db_path = '/var/lib/aide/aide.db'
    new_db_path = '/var/lib/aide/aide.db.new'
    
    if os.path.exists(db_path):
        logger.info("AIDE database already exists. Initialization skipped. Run aide --update manually to refresh.")
    else:
        logger.info("AIDE database not found. Starting aideinit. This may take a long time...")
        # Since this takes time, we should run it and let the user know.
        try:
            # Note: Debian/Ubuntu specific command
            system.run_command(['aideinit'], check=True, suppress_output=False)
            logger.info("AIDE database initialization complete.")
            # aideinit usually copies .new to .db in ubuntu automatically or via prompt,
            # but standard aide requires copying. On Ubuntu, aideinit does it.
            if os.path.exists(new_db_path) and not os.path.exists(db_path):
                 os.rename(new_db_path, db_path)
                 logger.info("Copied aide.db.new to aide.db.")
        except Exception as e:
            logger.error(f"Failed to initialize AIDE database: {e}")


# Entry points
def run_apply():
    if verify_auditd_status():
        apply_auditd_rules()
    else:
        logger.error("auditd is not running. Cannot apply rules. Please install and start auditd.")
        
    initialize_aide()

def run_audit():
    verify_auditd_status()
    verify_aide_status()
    
    logger.info("Auditing current rules...")
    # This requires sudo to run correctly, assume user running this script is root or in sudo group
    system.run_command(['auditctl', '-l'], check=False, suppress_output=False)

def run_rollback():
    logger.info("Rollback not fully implemented for audit module.")
