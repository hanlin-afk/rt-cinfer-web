# Threat Model (Research Infrastructure)

- **Data Integrity**: Validate dataset checksums; signed artifact downloads.
- **Experiment Tampering**: Lock experiment configs; record Git commit hash in plots.
- **Supply Chain**: Pin dependency versions; verify container digests.
- **Reproducibility**: Archive seeds and params in results JSON alongside figures.
