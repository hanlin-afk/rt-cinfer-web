# Carbon Accounting

- Use **grid carbon intensity** (gCO₂e/kWh) over time and region.
- Carbon per task: `C_task = E_task(kWh) * CI_region(time)` aggregated by execution window.
- For multi-cloud or geo-distributed settings, use **location-dependent** intensity; consider **time-shifting** batch workloads.
