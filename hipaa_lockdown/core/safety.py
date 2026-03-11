"""
HIPAA-Lockdown-CLI: Backup and Safety Utilities
"""
import os
import shutil
import time
import logging

logger = logging.getLogger(__name__)

def backup_file(filepath: str) -> str:
    """
    Creates a timestamped backup of a file.
    Returns the path to the backup file, or None if the original file doesn't exist.
    """
    if not os.path.exists(filepath):
        logger.warning(f"File {filepath} does not exist. Cannot backup.")
        return None

    timestamp = time.strftime("%Y%m%d%H%M%S")
    backup_path = f"{filepath}.bak_{timestamp}"
    
    try:
        shutil.copy2(filepath, backup_path)
        logger.info(f"Successfully backed up {filepath} to {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to backup {filepath}: {e}")
        raise RuntimeError(f"Safety constraint failed: Could not backup {filepath}") from e

def restore_backup(filepath: str, backup_path: str):
    """
    Restores a file from a specified backup path.
    """
    if not os.path.exists(backup_path):
        logger.error(f"Backup file {backup_path} does not exist. Cannot restore.")
        raise FileNotFoundError(f"Backup file {backup_path} not found.")

    try:
        shutil.copy2(backup_path, filepath)
        logger.info(f"Successfully restored {filepath} from {backup_path}")
    except Exception as e:
         logger.error(f"Failed to restore {filepath} from {backup_path}: {e}")
         raise RuntimeError(f"Rollback failed: Could not restore {filepath}") from e
