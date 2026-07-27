# Operator Guide

## Setup

Open **Cash Flow Settings** and set:

- **Cash Account**: the main current account the forecast tracks (Banca Sella,
  182001). Its current balance is the forecast's opening balance.
- **Amex Account**: the American Express account (182005).
- **Forecast Horizon**: how many days ahead to project (default 120).
- **Amex Charge Day / Cycle Day**: 3 and 16 for the standard Amex cycle (charges
  from the 16th to the 15th settle on the 3rd of the next period).

## Recurring payments

Register each subscription or insurance under **Recurring Payments**: supplier,
amount, category, payment method, frequency (monthly/annual) and next due date.
They are projected forward across the horizon.

## Running the forecast

Click **Rebuild Forecast** on Cash Flow Settings (or via
`fab_cashflow.forecast.rebuild_forecast`). It clears the generated events and
regenerates them from all sources. Then:

- **Cash Flow Forecast** report shows the timeline with a running balance.
- **Cash Flow Event** calendar shows the same events by day.

Events you add by hand (Generated unticked) survive a rebuild, so you can add
one-off expected movements the automatic sources do not know about.

## Payment methods

Payment methods carry the FatturaPA MP code and their default account:

- Bank transfer (Wire Transfer, MP05) and Bancomat (MP08) and RID (MP09): the
  Sella account.
- American Express (MP08): the Amex account, settled monthly against Sella.

## Notes

- The Amex settlement amount is the net charges booked on the Amex account in the
  cycle. Verify the sign against a real Amex statement the first time: a purchase
  paid via Amex should increase what you owe (a credit on the account).
- Overdue invoices are brought onto the first forecast day so the running balance
  reflects money that is already late.
