from datetime import datetime

CUSTOMERS = {
    "priya": {
        "name": "Priya Nair",
        "profile": "Priya Nair is the operations lead at Brightlane Logistics. Plan: Pro (25 seats). Uses Chrome on Windows and the CloudDesk REST API. Prefers short, technical answers and dislikes generic troubleshooting steps.",
        "tickets": [
            (datetime(2026, 1, 12), "Ticket: CSV export of about 50,000 rows failed with ERR_EXPORT_504 (timeout). Resolution: switched Settings > Data > Export mode to 'chunked', which worked. Priya was frustrated and said this was the second time this quarter."),
            (datetime(2026, 2, 3), "Ticket: nightly API sync hit HTTP 429 rate limit errors. Resolution: moved the sync job to 02:00 UTC and added retry with exponential backoff. Priya confirmed it worked."),
            (datetime(2026, 3, 18), "Ticket: duplicate charge for Pro seats on the March invoice. Resolution: billing refunded the duplicate. Priya asked to always get an email confirmation for billing fixes."),
        ],
        "demo_message": "My export is failing again with a timeout error.",
    },
    "rahul": {
        "name": "Rahul Mehta",
        "profile": "Rahul Mehta runs Sunrise Retail. Plan: Starter (3 seats). Uses the CloudDesk iOS app v4.2 on iPhone. New to the product and prefers step-by-step instructions with exact menu names.",
        "tickets": [
            (datetime(2026, 2, 9), "Ticket: login loop in the iOS app after a password reset. Resolution: deleted the saved CloudDesk entry in iOS Keychain, reinstalled the app, then logged in with the new password. That fixed it."),
            (datetime(2026, 3, 2), "Ticket: push notifications stopped arriving. Resolution: after an iOS update, Settings > Notifications > CloudDesk > Allow Notifications was switched off. Re-enabled it and it worked."),
        ],
        "demo_message": "I can't log in on my phone again, it just keeps looping.",
    },
    "ananya": {
        "name": "Ananya Rao",
        "profile": "Ananya Rao is the IT admin at Vantage Finance. Plan: Enterprise with 4-hour response SLA. Uses Okta SSO. Wants proactive status updates during any outage.",
        "tickets": [
            (datetime(2026, 1, 28), "Ticket: SAML login failed for all users after an Okta certificate rotation. Resolution: uploaded the new IdP certificate under Admin > Security > SSO. Took 3 hours, close to the 4-hour SLA. Ananya asked for status updates every 30 minutes during outages."),
            (datetime(2026, 3, 9), "Ticket: SCIM provisioning delayed about 2 hours for new hires. Resolution: engineering raised the SCIM sync frequency for her tenant after escalation to Tier 2."),
        ],
        "demo_message": "New hires aren't showing up in CloudDesk after we add them in Okta.",
    },
}