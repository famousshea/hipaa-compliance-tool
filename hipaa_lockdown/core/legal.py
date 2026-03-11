"""
HIPAA-Lockdown-CLI: Legal Disclaimer & Liability Limitation
"""
import sys

DISCLAIMER_TEXT = """
================================================================================
                                LEGAL DISCLAIMER                                
                         AND LIMITATION OF LIABILITY                            
                                                                                
This software ('HIPAA-Lockdown-CLI') is provided 'as is' and without any        
express or implied warranties, including, without limitation, the implied       
warranties of merchantability and fitness for a particular purpose.             
                                                                                
1. NOT A CERTIFIED AUDIT: This tool is intended strictly as a technical aid     
   to assist in hardening a Linux system. It DOES NOT constitute, replace, or   
   guarantee a certified third-party HIPAA compliance audit.                    
                                                                                
2. NO GUARANTEE OF COMPLIANCE: The creators and maintainers of this tool        
   cannot and do not certify that the execution of this software will result    
   in full compliance with the Health Insurance Portability and Accountability  
   Act (HIPAA) or any other regulatory framework. The ultimate responsibility   
   for ensuring HIPAA compliance rests solely with the Covered Entity or        
   Business Associate utilizing the system.                                     
                                                                                
3. RISK OF DISRUPTION: System hardening involves modifying critical networking, 
   authentication, and filesystem policies. These changes MAY disrupt normal    
   system operations or user workflows. You assume all risks associated with    
   executing these changes on your workstation.                                 
                                                                                
By proceeding, you acknowledge that you have read, understood, and agree to     
these terms.                                                                    
================================================================================
"""

def prompt_cli_acknowledgment():
    """
    Displays the disclaimer and prompts the user to explicitly type 'I AGREE'.
    Exits the program if they do not.
    """
    print(DISCLAIMER_TEXT)
    response = input("Type 'I AGREE' to acknowledge the limited liability terms and proceed: ")
    
    if response.strip() != 'I AGREE':
        print("\nAcknowledgment failed. The tool will now safely exit.")
        sys.exit(1)
    
    print("\nTerms acknowledged. Proceeding...\n")
