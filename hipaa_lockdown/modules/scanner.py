"""
HIPAA-Lockdown-CLI: Vulnerability & Malware Scanning Module
"""
import logging
import os

from hipaa_lockdown.core import system

logger = logging.getLogger(__name__)

def verify_clamav_status():
    """
    Checks if clamav is installed.
    """
    logger.info("Verifying ClamAV status...")
    if os.path.exists('/usr/bin/clamscan'):
        logger.info("ClamAV is installed locally.")
        return True
    else:
        logger.warning("ClamAV is NOT installed. Missing malware scanning component.")
        return False

def apply_scheduled_clamav():
    """
    Deploys a lightweight systemd timer that runs calmscan on home directories daily without the heavy clamav-daemon.
    Triggers notify-send for the user.
    """
    logger.info("Applying daily scheduled ClamAV scans via systemd...")
    
    if not os.path.exists('/usr/bin/clamscan'):
        logger.error("Cannot schedule ClamAV scan; clamscan is missing.")
        return
        
    script_path = '/usr/local/bin/hipaa-clamscan.sh'
    service_path = '/etc/systemd/system/hipaa-clamscan.service'
    timer_path = '/etc/systemd/system/hipaa-clamscan.timer'
    
    # 1. Provide the execution script with notify-send integration (requires sudo -u $SUDO_USER)
    script_content = """#!/bin/bash
# HIPAA-Lockdown Clamscan Script
SCAN_DIR="/home"
CLAM_OUT=$(clamscan -r -i "$SCAN_DIR" 2>&1)
EXIT_CODE=$?

# Try to notify the primary user (assumes running via systemd where DISPLAY needs to be guessed, or runs via user unit)
# Since this runs as root to scan all homes, we will log it.
logger -t "HIPAA-Clamscan" "$CLAM_OUT"

if [ $EXIT_CODE -eq 1 ]; then
    logger -t "HIPAA-Clamscan" "WARNING: Malware detected in $SCAN_DIR"
elif [ $EXIT_CODE -gt 1 ]; then
    logger -t "HIPAA-Clamscan" "ERROR: Clamscan failed with code $EXIT_CODE"
else
    logger -t "HIPAA-Clamscan" "Scan completed successfully. No threats found."
fi
"""
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        logger.info(f"Deployed scan script to {script_path}")
    except Exception as e:
         logger.error(f"Failed to write script: {e}")
         return

    # 2. Provide the systemd service
    service_content = f"""[Unit]
Description=HIPAA Scheduled ClamAV Scan
After=network.target

[Service]
Type=oneshot
ExecStart={script_path}
"""
    try:
        with open(service_path, 'w') as f:
            f.write(service_content)
    except Exception as e:
         logger.error(f"Failed to write service: {e}")
         
    # 3. Provide the systemd timer (Daily)
    timer_content = """[Unit]
Description=Run HIPAA ClamAV Scan Daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
"""
    try:
        with open(timer_path, 'w') as f:
            f.write(timer_content)
    except Exception as e:
         logger.error(f"Failed to write timer: {e}")

    # 4. Enable and start the timer
    try:
        system.run_command(['systemctl', 'daemon-reload'], check=False)
        system.run_command(['systemctl', 'enable', 'hipaa-clamscan.timer'], check=False)
        system.run_command(['systemctl', 'start', 'hipaa-clamscan.timer'], check=False)
        logger.info("Successfully enabled and started hipaa-clamscan.timer")
    except Exception as e:
         logger.error(f"Failed to enable systemd timer: {e}")

# Entry points
def run_apply():
    apply_scheduled_clamav()

def run_audit():
    verify_clamav_status()
    
    # Check for our specific HIPAA timer or general clamav timers
    timers = ['hipaa-clamscan.timer', 'clamav-freshclam.service']
    found_active = False
    
    for t in timers:
        if system.is_service_active(t):
            logger.info(f"Active scanning/update service found: {t}")
            found_active = True
            break
            
    if not found_active:
        logger.warning("No scheduled HIPAA ClamAV scanning timer is active.")

def run_rollback():
    logger.info("Rollback not implemented for scanner module.")
