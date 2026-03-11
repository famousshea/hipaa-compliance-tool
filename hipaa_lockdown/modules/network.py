"""
HIPAA-Lockdown-CLI: Network Security Module
"""
import logging
import os

from hipaa_lockdown.core import system

logger = logging.getLogger(__name__)

def verify_ufw_status():
    """
    Checks if UFW (Uncomplicated Firewall) is active and running.
    """
    logger.info("Verifying UFW status...")
    
    # Try systemctl first
    if system.is_service_active('ufw'):
        logger.info("UFW service is active.")
        return True
        
    # Fallback to ufw status (handles cases where service is active but doesn't report via systemctl)
    try:
        # Note: Non-root users might get an error here, but we check for the string
        result = system.run_command(['ufw', 'status'], check=False, suppress_output=True)
        if 'Status: active' in result.stdout or 'Status: active' in result.stderr:
            logger.info("UFW is reported as active via status command.")
            return True
    except:
        pass

    logger.warning("UFW is NOT active. Network segmentation may be compromised.")
    return False

def apply_sysctl_tweaks():
    """
    Applies kernel parameters to enable IP Spoofing protection and disable ICMP redirects.
    """
    conf_path = '/etc/sysctl.d/99-hipaa.conf'
    
    logger.info(f"Deploying sysctl tweaks to {conf_path}")
    
    # We do not backup the rules file if it doesn't exist, we just create it
    
    rules = """
# HIPAA-Lockdown: Network Tweaks
# Enable IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Disable ICMP redirects (prevents routing table manipulation)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0
"""
    try:
        with open(conf_path, 'w') as f:
            f.write(rules.strip() + '\n')
        logger.info(f"Successfully wrote {conf_path}")
        
        # Reload sysctl
        logger.info("Reloading sysctl configuration...")
        system.run_command(['sysctl', '--system'], check=False)
        
    except Exception as e:
        logger.error(f"Failed to apply sysctl rules: {e}")

def apply_kernel_module_blacklisting():
    """
    Generates `/etc/modprobe.d/hipaa-blacklist.conf` to disable RISKY/unused protocols (dccp, sctp, rds, tipc).
    """
    conf_path = '/etc/modprobe.d/hipaa-blacklist.conf'
    
    logger.info(f"Deploying kernel module blacklists to {conf_path}")
    
    rules = """
# HIPAA-Lockdown: Protocol Blacklisting
# Disable uncommon and historically vulnerable network protocols
install dccp /bin/true
install sctp /bin/true
install rds /bin/true
install tipc /bin/true
"""
    try:
        with open(conf_path, 'w') as f:
            f.write(rules.strip() + '\n')
        logger.info(f"Successfully wrote {conf_path}")
        
    except Exception as e:
        logger.error(f"Failed to apply modprobe rules: {e}")

def apply_ufw_default_deny():
    """
    Enforces a default deny incoming posture via UFW and ensures SSH is allowed.
    """
    logger.info("Applying UFW default deny policy...")
    
    if not os.path.exists('/usr/sbin/ufw'):
         logger.error("UFW is not installed. Cannot apply firewall rules.")
         return
         
    try:
        system.run_command(['ufw', '--force', 'reset'], check=True)
        system.run_command(['ufw', 'default', 'deny', 'incoming'], check=True)
        system.run_command(['ufw', 'default', 'allow', 'outgoing'], check=True)
        system.run_command(['ufw', 'allow', 'ssh'], check=True)
        system.run_command(['ufw', '--force', 'enable'], check=True)
        logger.info("UFW default deny incoming and allow SSH has been enabled.")
    except Exception as e:
        logger.error(f"Failed to configure UFW: {e}")

def audit_luks_encryption():
    """
    Audits block devices to check if crypto_LUKS is in use for HIPAA data-at-rest encryption.
    """
    logger.info("Auditing LUKS Full Disk Encryption status...")
    try:
        result = system.run_command(['lsblk', '-f'], check=True, suppress_output=True)
        if 'crypto_LUKS' in result.stdout:
            logger.info("LUKS Encryption is actively utilized on this system.")
        else:
            logger.warning("LUKS Encryption (crypto_LUKS) NOT found. Data at rest may be unencrypted!")
    except Exception as e:
        logger.error(f"Failed to check LUKS status: {e}")

# Entry points
def run_apply():
    apply_ufw_default_deny()
    apply_sysctl_tweaks()
    apply_kernel_module_blacklisting()

def run_audit():
    verify_ufw_status()
    audit_luks_encryption()
    
    logger.info("Auditing sysctl network tweaks...")
    # This just reads values directly via sysctl
    system.run_command(['sysctl', 'net.ipv4.conf.all.rp_filter'], check=False, suppress_output=False)
    system.run_command(['sysctl', 'net.ipv4.conf.all.accept_redirects'], check=False, suppress_output=False)

def run_rollback():
    logger.info("Rollback not fully implemented for network module.")
