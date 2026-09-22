from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from frappe import _dict
from frappe.utils import getdate

from fab_cashflow.forecast import _customer_inflows, _split_payment_inflows


def build_invoice(**overrides):
    defaults = {
        "name": "FATT/2026/00035",
        "customer": "COMUNE DI POMPIANO",
        "due_date": "2026-05-31",
        "outstanding_amount": 3013.40,
    }
    defaults.update(overrides)
    return _dict(defaults)


def italy_tax_stub(invoices):
    """Stand in for the fab_italy_tax lookup of collectability and VAT."""
    return SimpleNamespace(get_all=lambda doctype, **kwargs: invoices)


class TestCustomerInflows(unittest.TestCase):
    def run_inflows(self, documents, invoices):
        cashflow_stub = SimpleNamespace(
            get_all=lambda doctype, **kwargs: documents,
            get_installed_apps=lambda: ["frappe", "erpnext", "fab_italy_tax", "fab_cashflow"],
        )
        with (
            patch("fab_cashflow.forecast.frappe", new=cashflow_stub),
            patch("fab_italy_tax.cashflow.frappe", new=italy_tax_stub(invoices)),
            # flt() rounds through System Settings, unreachable without a site
            patch("frappe.get_system_settings", return_value="Banker's Rounding"),
        ):
            return _customer_inflows("Fabricators", getdate("2026-05-01"), getdate("2026-06-30"))

    def test_fully_outstanding_split_payment_invoice_brings_in_the_net_only(self):
        events = self.run_inflows(
            documents=[build_invoice()],
            invoices=[
                {
                    "name": "FATT/2026/00035",
                    "vat_collectability": "S-Scissione dei Pagamenti",
                    "total_taxes_and_charges": 543.40,
                }
            ],
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["amount"], 2470.0)
        self.assertEqual(events[0]["source_ref"], "FATT/2026/00035")

    def test_partly_paid_split_payment_invoice_brings_in_what_is_left_of_the_net(self):
        events = self.run_inflows(
            documents=[build_invoice(outstanding_amount=1513.40)],
            invoices=[
                {
                    "name": "FATT/2026/00035",
                    "vat_collectability": "S-Scissione dei Pagamenti",
                    "total_taxes_and_charges": 543.40,
                }
            ],
        )

        self.assertEqual(events[0]["amount"], 970.0)

    def test_split_payment_invoice_outstanding_down_to_vat_only_brings_no_event(self):
        events = self.run_inflows(
            documents=[build_invoice(outstanding_amount=543.40)],
            invoices=[
                {
                    "name": "FATT/2026/00035",
                    "vat_collectability": "S-Scissione dei Pagamenti",
                    "total_taxes_and_charges": 543.40,
                }
            ],
        )

        self.assertEqual(events, [])

    def test_ordinary_invoice_still_brings_in_the_gross_outstanding(self):
        events = self.run_inflows(
            documents=[build_invoice(name="FATT/2026/00036", outstanding_amount=122.0)],
            invoices=[
                {
                    "name": "FATT/2026/00036",
                    "vat_collectability": "I-Immediata",
                    "total_taxes_and_charges": 22.0,
                }
            ],
        )

        self.assertEqual(events[0]["amount"], 122.0)

    def test_split_payment_credit_note_gives_back_the_taxable_amount_only(self):
        credit_note = build_invoice(name="NC/2026/00002", outstanding_amount=-3013.40)
        with patch(
            "fab_cashflow.forecast.frappe",
            new=SimpleNamespace(get_installed_apps=lambda: ["fab_italy_tax"]),
        ), patch(
            "fab_italy_tax.cashflow.frappe",
            new=italy_tax_stub(
                [
                    {
                        "name": "NC/2026/00002",
                        "vat_collectability": "S-Scissione dei Pagamenti",
                        "total_taxes_and_charges": -543.40,
                    }
                ]
            ),
        ):
            expected = _split_payment_inflows([credit_note])

        self.assertEqual(expected, {"NC/2026/00002": -2470.0})
