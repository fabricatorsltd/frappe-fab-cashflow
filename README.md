## Fab Cashflow

Forward-looking cash flow forecast for the company's main current account,
merging every expected movement into a running-balance report and a calendar.

### Sources

The forecast (materialized as **Cash Flow Event**) is rebuilt from:

- **Customer invoices**: outstanding Sales Invoices at their due date (inflow).
- **Supplier invoices**: outstanding Purchase Invoices at their due date.
- **Recurring Payment**: subscriptions and insurance (supplier, amount, method,
  monthly/annual, next due), projected forward across the horizon.
- **Amex settlement cycle**: the American Express account is not debited at
  purchase; each cycle (16th to the 15th) settles on the charge day (3rd) of the
  following period. The forecast places one outflow on the charge day equal to
  the Amex account's net charges in that cycle.
- **Tax deadlines**: future Tax Calendar Events (VAT/F24 liquidations).

### Views

- **Cash Flow Forecast** report: chronological events with a running balance from
  the current account balance, so you see when the account would go negative.
- **Cash Flow Event** calendar: the same events on a calendar (inflows green,
  outflows red).

### Configuration

**Cash Flow Settings** (single): the cash account (Banca Sella), the Amex
account, the forecast horizon, and the Amex charge/cycle days. The *Rebuild
Forecast* button regenerates the events; manual events are kept.

### Documentation

`docs/operator-guide.md`.

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/fabricatorsltd/frappe-fab-cashflow.git --branch version-16
bench --site [site] install-app fab_cashflow
```

### License

agpl-3.0
