#!/usr/bin/env python3
"""
HIPAA-Lockdown-CLI: Main Entry Point
"""
import argparse
import sys
import logging

from hipaa_lockdown.modules import auth, filesystem, audit, network, scanner
from hipaa_lockdown.core.legal import prompt_cli_acknowledgment

# Standardize logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="HIPAA-Lockdown-CLI: Autonomously harden an Ubuntu 25.10 workstation for HIPAA compliance.")
    
    # Modes
    parser.add_argument('--audit-only', action='store_true', help="Run a non-destructive dry-run audit.")
    parser.add_argument('--apply', action='store_true', help="Apply harddening configurations.")
    parser.add_argument('--rollback', action='store_true', help="Rollback configurations using backups.")
    
    # Domains
    parser.add_argument('--domain', choices=['all', 'auth', 'filesystem', 'audit', 'network', 'scanner'], default='all', help="Specific domain to target (default: all)")
    
    args = parser.parse_args()

    # Determine execution mode
    mode = 'audit' if args.audit_only else ('apply' if args.apply else ('rollback' if args.rollback else None))
    
    if mode is None:
        parser.print_help()
        sys.exit(1)

    if mode == 'apply':
        prompt_cli_acknowledgment()

    logger.info(f"Starting HIPAA-Lockdown-CLI in {mode.upper()} mode for domain: {args.domain.upper()}")

    domains_to_run = [args.domain] if args.domain != 'all' else ['auth', 'filesystem', 'audit', 'network', 'scanner']
    
    # Module Mapping
    modules = {
        'auth': auth,
        'filesystem': filesystem,
        'audit': audit,
        'network': network,
        'scanner': scanner
    }

    for domain in domains_to_run:
        module = modules.get(domain)
        if hasattr(module, f"run_{mode}"):
             logger.info(f"--- Running {domain.upper()} module [{mode.upper()}] ---")
             getattr(module, f"run_{mode}")()
        else:
             logger.warning(f"Module {domain} does not have a run_{mode} function implemented yet.")

if __name__ == '__main__':
    main()
