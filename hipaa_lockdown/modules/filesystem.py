"""
HIPAA-Lockdown-CLI: Filesystem & Privacy Module
"""
import logging
import os
import re

from hipaa_lockdown.core import safety, system

logger = logging.getLogger(__name__)

def apply_umask_policy():
    """
    Enforces a system-wide UMASK 027.
    """
    profile_path = '/etc/profile.d/hipaa_umask.sh'
    login_defs = '/etc/login.defs'
    
    logger.info(f"Applying system-wide UMASK 027 policy")
    
    # 1. Update /etc/profile.d
    with open(profile_path, 'w') as f:
        f.write("#!/bin/sh\n")
        f.write("# HIPAA-Lockdown: Force umask 027 for all users\n")
        f.write("umask 027\n")
    logger.info(f"Created {profile_path}")
    
    # 2. Update login.defs
    if os.path.exists(login_defs):
        safety.backup_file(login_defs)
        with open(login_defs, 'r') as f:
            config = f.read()
        
        config = re.sub(r'^\s*UMASK\s+\d+', 'UMASK           027', config, flags=re.MULTILINE)
        if 'UMASK           027' not in config:
            config += "\nUMASK           027\n"
            
        with open(login_defs, 'w') as f:
            f.write(config)
        logger.info(f"Updated UMASK in {login_defs}")
    else:
        logger.warning(f"{login_defs} not found. Cannot set default UMASK for new users.")

def apply_compiler_restrictions():
    """
    Restricts execution of compilation tools to the root user.
    """
    compilers = ['/usr/bin/gcc', '/usr/bin/g++', '/usr/bin/make']
    
    logger.info("Applying compiler execution restrictions (chmod 700)")
    for compiler in compilers:
        if os.path.exists(compiler):
            try:
                # We can't backup binaries easily/shouldn't, so we just chmod them
                os.chmod(compiler, 0o700)
                logger.info(f"Restricted access to {compiler}")
            except Exception as e:
                logger.error(f"Failed to restrict access to {compiler}: {e}")
        else:
            logger.debug(f"Compiler {compiler} not found, skipping.")

def audit_filesystem():
    """
    Audits filesystem settings.
    """
    logger.info("Auditing filesystem policies...")
    
    profile_path = '/etc/profile.d/hipaa_umask.sh'
    if os.path.exists(profile_path):
        logger.info("Global umask profile exists.")
    else:
        logger.warning("Global umask profile is missing.")
        
    compilers = ['/usr/bin/gcc', '/usr/bin/g++', '/usr/bin/make']
    for compiler in compilers:
        if os.path.exists(compiler):
            st = os.stat(compiler)
            mode = oct(st.st_mode)[-3:]
            if mode == '700':
                 logger.info(f"Compiler {compiler} is restricted (700).")
            else:
                 logger.warning(f"Compiler {compiler} is NOT restricted (Current: {mode}, Expected: 700).")

# Entry points
def run_apply():
    apply_umask_policy()
    apply_compiler_restrictions()

def run_audit():
    audit_filesystem()

def run_rollback():
    logger.info("Rollback not fully implemented for filesystem module.")
