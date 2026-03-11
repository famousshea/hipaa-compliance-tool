"""
HIPAA-Lockdown-CLI: System Execution Utilities
"""
import subprocess
import logging

logger = logging.getLogger(__name__)

def run_command(command: list[str], check=True, suppress_output=False) -> subprocess.CompletedProcess:
    """
    Safely executes a system command and returns the CompletedProcess object.
    Raises RuntimeError if the command fails and check=True.
    """
    cmd_str = ' '.join(command)
    logger.debug(f"Executing: {cmd_str}")

    try:
        # Use capture_output=True to catch stdout and stderr
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if not suppress_output and result.stdout:
            logger.debug(f"Command stdout: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd_str}")
        logger.error(f"Exit Code: {e.returncode}")
        logger.error(f"Stderr: {e.stderr.strip()}")
        raise RuntimeError(f"System command failed: {cmd_str}") from e
    except Exception as e:
        logger.error(f"Unexpected error executing command: {cmd_str}")
        logger.error(e)
        raise RuntimeError(f"Unexpected execution error: {cmd_str}") from e

def is_service_active(service_name: str) -> bool:
    """
    Checks if a systemd service is active.
    """
    try:
        result = run_command(['systemctl', 'is-active', service_name], check=False, suppress_output=True)
        return result.returncode == 0
    except Exception:
        return False
