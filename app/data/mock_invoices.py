import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import os

def generate_mock_invoices(count: int = 50) -> List[Dict]:
    vendors = ["TechCorp", "SupplyCo", "MaterialsInc", "ServicePro", "EquipmentLtd"]
    invoices = []
    for i in range(count):
        invoice_id = f"INV-{1000 + i}"
        po_number = f"PO-{2000 + i}" if random.random() > 0.1 else None
        is_flagged = random.random() < 0.3
        base_amount = random.uniform(100, 10000)
        invoice_amount = base_amount * random.uniform(0.8, 1.2) if is_flagged else base_amount
        invoice = {
            "invoice_id": invoice_id,
            "po_number": po_number,
            "vendor": random.choice(vendors),
            "invoice_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "due_date": (datetime.now() + timedelta(days=random.randint(15, 45))).isoformat(),
            "total_amount": round(invoice_amount, 2),
            "currency": "USD",
            "status": "flagged" if is_flagged else random.choice(["pending", "approved"]),
            "line_items": [
                {
                    "description": f"Item {j+1}",
                    "quantity": random.randint(1, 10),
                    "unit_price": round(random.uniform(10, 500), 2),
                    "total": round(random.uniform(50, 2000), 2),
                } for j in range(random.randint(1, 5))
            ],
            "flagged_reasons": [
                "Amount mismatch with PO",
                "Missing goods receipt",
                "Vendor not in approved list"
            ] if is_flagged else []
        }
        invoices.append(invoice)
    return invoices

def generate_mock_pos(count: int = 50) -> List[Dict]:
    departments = ["IT", "Operations", "Finance", "HR", "Marketing"]
    vendors = ["TechCorp", "SupplyCo", "MaterialsInc", "ServicePro"]
    pos = []
    for i in range(count):
        po_number = f"PO-{2000 + i}"
        po = {
            "po_number": po_number,
            "department": random.choice(departments),
            "created_date": (datetime.now() - timedelta(days=random.randint(30, 120))).isoformat(),
            "vendor": random.choice(vendors),
            "total_amount": round(random.uniform(100, 10000), 2),
            "currency": "USD",
            "status": random.choice(["open", "partially_received", "closed"]),
            "line_items": [
                {
                    "item_code": f"ITEM-{random.randint(1000, 9999)}",
                    "description": f"Product {j+1}",
                    "quantity_ordered": random.randint(1, 10),
                    "quantity_received": random.randint(0, 10),
                    "unit_price": round(random.uniform(10, 500), 2)
                } for j in range(random.randint(1, 5))
            ],
            "delivery_date": (datetime.now() + timedelta(days=random.randint(5, 30))).isoformat(),
            "approver": f"manager{random.randint(1, 5)}@company.com"
        }
        pos.append(po)
    return pos

if __name__ == "__main__":
    # Ensure directories always exist relative to project root
    os.makedirs("data/invoices", exist_ok=True)
    os.makedirs("data/pos", exist_ok=True)

    invoices = generate_mock_invoices(50)
    pos = generate_mock_pos(50)
    with open("data/invoices/mock_invoices.json", "w") as f:
        json.dump(invoices, f, indent=2)
    with open("data/pos/mock_pos.json", "w") as f:
        json.dump(pos, f, indent=2)
    print("✅ Mock data generated successfully!")
