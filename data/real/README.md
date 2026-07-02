# Real public data directory

This directory is reserved for downloaded public field data.

Recommended workflow:

```bash
python scripts/fetch_pagespeed_crux.py \
  --origins configs/us_ecommerce_origins.csv \
  --out data/real/public_crux_pagespeed.csv \
  --raw-dir data/real/raw_pagespeed

python scripts/run_real_public_observational.py \
  --input data/real/public_crux_pagespeed.csv \
  --report results/real_public_observational/report.md
```

Raw API JSON responses should be preserved under `data/real/raw_*` for auditability.
Do not commit private RUM logs, customer identifiers, IP addresses, session IDs, or internal deployment logs.
