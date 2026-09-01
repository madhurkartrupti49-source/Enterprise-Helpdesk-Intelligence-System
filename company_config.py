"""
Company configuration for AI Enterprise Helpdesk
"""

COMPANY_NAME = "Your Company Name"


# ============================================================
# TEAM EMAIL CONFIGURATION
# ============================================================

TEAM_EMAILS = {

    "Network Team": "network-team@company.com",

    "Email/Collab Team": "email-team@company.com",

    "Desktop Support": "desktop-support@company.com",

    "Security Team": "security-team@company.com",

    "Application Support": "application-support@company.com",

}


# ============================================================
# GET TEAM EMAIL
# ============================================================

def get_team_email(team_name):

    return TEAM_EMAILS.get(
        team_name,
        "support@company.com"
    )