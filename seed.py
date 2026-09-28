from agent import hs, bank_for, ensure_bank
from seed_data import CUSTOMERS

for cid, c in CUSTOMERS.items():
    ensure_bank(cid, c["name"])
    hs.retain(bank_id=bank_for(cid), content=c["profile"], context="customer profile", retain_async=False)
    for date, text in c["tickets"]:
        hs.retain(bank_id=bank_for(cid), content=text, context="past support ticket", timestamp=date, retain_async=False)
    print("seeded", c["name"])