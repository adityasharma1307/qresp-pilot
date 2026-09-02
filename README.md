# qresp-pilot

CLI that audits Hugging Face model provenance and labels each one by quantum vulnerability. It never downloads weights — only signature sidecars — so 1,000 models take a few seconds.

Student project (CS F376, BITS Pilani Dubai, 2025–26). Supervisor: Dr. Tamizharasan Periyasamy.

## Finding (May 2026, n = 1,000)

| Label | Count | Share |
|---|---|---|
| Unsigned | 998 | 99.8% |
| Vulnerable (ECDSA P-256) | 2 | 0.2% |
| Post-quantum safe | 0 | 0% |

The two signed models (`ibm-granite/granite-4.0-h-small`, `openai/privacy-filter`) use ECDSA P-256 via Sigstore. n = 1,000 is above the 615 needed to detect 1% PQ adoption at 80% power.

Labels: `safe` (ML-DSA / SLH-DSA), `vulnerable` (RSA, ECDSA, Ed25519), `unsigned`, `mixed`, `error`.

## Run

Python 3.10+.

```bash
git clone https://github.com/adityasharma1307/qresp-pilot
cd qresp-pilot
pip install -e .
```

Report: `docs/report.pdf`. The signing tool that followed this audit is [qknot](https://github.com/adityasharma1307/qknot). License: MIT.
