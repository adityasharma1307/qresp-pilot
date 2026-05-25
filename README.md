# QResP — Quantum-Resilient Provenance Audit

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Models audited](https://img.shields.io/badge/Models%20audited-1%2C000-green.svg)
![PQ-safe](https://img.shields.io/badge/PQ--safe%20models-0%25-red.svg)

> Phase I of *Quantum-Resilient Provenance for Machine Learning Supply Chains*
> CS F376 Design Project, BITS Pilani Dubai Campus, 2025–26.
> Supervisor: Dr. Tamizharasan Periyasamy.

`qresp` is a command-line tool that audits the cryptographic provenance of
public machine learning models on HuggingFace and classifies each by
quantum vulnerability. It produces a reproducible JSON Lines dataset that
forms the empirical foundation of the project.

The accompanying end-semester report is available in [`docs/report.pdf`](docs/report.pdf).

---

## Key Findings (May 2026, n = 1,000)

| Label | Count | Share | 95% Wilson CI |
|---|---|---|---|
| **Unsigned** | 998 | 99.8% | [99.27%, 99.95%] |
| **Vulnerable** (ECDSA P-256) | 2 | 0.2% | [0.05%, 0.73%] |
| **Post-quantum safe** | 0 | 0.0% | [0.00%, 0.38%] |

The two signed models are `ibm-granite/granite-4.0-h-small` and
`openai/privacy-filter`, both using **ECDSA P-256 via Sigstore** — a
classical scheme broken by Shor's algorithm. No model in the top 1,000
uses a post-quantum signature scheme (ML-DSA or SLH-DSA).

A power analysis confirms n = 1,000 exceeds the minimum sample of 615
required to detect even 1% post-quantum adoption at 80% power, establishing
that the null result is not an artefact of insufficient sampling.

---

## What it does

The tool walks the HuggingFace registry, finds signature files attached to
each model (if any), parses them, identifies the underlying signature
algorithm, and tags the model with one of five labels:

| Label | Meaning |
|---|---|
| `safe` | Post-quantum scheme: ML-DSA or SLH-DSA (NIST FIPS 204/205) |
| `vulnerable` | Classical scheme: RSA, ECDSA, Ed25519 — broken by Shor's algorithm |
| `unsigned` | No signature file present |
| `mixed` | Multiple signatures with disagreeing labels |
| `error` | Signature present but could not be parsed |

The tool **never downloads model weights**. It checks only for signature
sidecar files (typically kilobytes), so a 1,000-model scan completes in
under 5 seconds.

---

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/adityasharma1307/qresp
cd qresp
pip install -e .
```

For analysis notebooks:

```bash
pip install -e ".[analysis]"
```

For development (tests, linter):

```bash
pip install -e ".[dev]"
```

> **Windows note:** if `qresp` is not found after install, the Python
> Scripts directory may not be on your PATH. Find it with:
> ```
> python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
> ```
> Then add the printed path to your PATH environment variable.

---

## Usage

### Run a pilot scan (50 models)

```bash
qresp scan --n 50 --out data/pilot.jsonl
```

### Run the full audit (1,000 models)

```bash
qresp scan --n 1000 --out data/full.jsonl
```

Resume is on by default — if interrupted, rerun the same command and it
picks up where it left off.

### With a HuggingFace token (higher rate limits)

```bash
qresp scan --n 1000 --out data/full.jsonl --token $HF_TOKEN
```

Get a free read-only token at https://huggingface.co/settings/tokens.

### Re-audit from scratch (ignore existing output)

```bash
qresp scan --n 1000 --out data/full.jsonl --no-resume
```

---

## Output format

Each line of the JSONL output is one model record:

```json
{
  "model_id": "ibm-granite/granite-4.0-h-small",
  "publisher": "ibm-granite",
  "downloads": 365180,
  "last_modified": "2025-11-03T19:45:37Z",
  "file_count": 26,
  "has_signature": true,
  "candidate_files": ["model.sig"],
  "sig_algorithm": "ecdsa_p256",
  "sig_format": "sigstore",
  "key_size_bits": null,
  "q_label": "vulnerable",
  "audit_ts": "2026-05-21T03:33:05Z",
  "notes": null
}
```

---

## Statistical analysis

Run the included stats script to reproduce the Wilson confidence intervals
and power analysis:

```bash
python stats.py
```

Expected output:

```
n = 1000
Signed:        2 / 1000  (0.2%)   95% CI: [0.05%, 0.73%]
Unsigned:    998 / 1000  (99.8%)  95% CI: [99.27%, 99.95%]
Vulnerable:    2 / 1000  (0.20%)  95% CI: [0.055%, 0.726%]
PQ-safe:       0 / 1000  (0.0%)   95% CI: [0.00%, 0.38%]

Power analysis: to detect 1% PQ adoption (vs 0%) at 80% power,
minimum sample size needed = 615 models
=> Our n=1000 is sufficient to rule out even 1% PQ adoption.
```

For visualisations, open the analysis notebook:

```bash
jupyter lab notebooks/analysis.ipynb
```

---

## Signature detection coverage

Detection is filename-based (no weights are downloaded) and covers:

| Format | Patterns matched |
|---|---|
| Sigstore | `.sigstore`, `.sigstore.json`, `model.sig`, `signature.json` |
| in-toto | `.intoto.jsonl`, `.in-toto.jsonl`, `attestation.json` |
| GPG / OpenPGP | `.asc`, `.gpg`, `.pgp` |
| Generic | `.sig` (fallback) |

Cosign bundle files (`.cosign.bundle`) are not currently covered but were
not observed in the audited corpus.

---

## Project structure

```
qresp/
├── data/               # Audit output (JSONL)
│   ├── pilot.jsonl     # 50-model pilot scan
│   └── full.jsonl      # 1,000-model full audit
├── docs/               # Report and figures
│   └── report.pdf
├── notebooks/          # Jupyter analysis notebooks
│   └── analysis.ipynb
├── scripts/            # Utility scripts
│   └── generate_sample.py
├── src/qresp/          # Package source
│   ├── cli.py          # Typer CLI entry point
│   ├── detect.py       # Filename-based signature detection
│   ├── hf_client.py    # HuggingFace API client
│   ├── model.py        # Pydantic record schema & enums
│   ├── parse.py        # Signature content parser
│   └── scanner.py      # Audit orchestration
├── tests/              # Pytest test suite
├── stats.py            # Statistical inference script
├── LICENSE
└── pyproject.toml
```

---

## Citing this work

```bibtex
@misc{sharma2026qresp,
  author       = {Sharma, Aditya},
  title        = {{QResP}: Quantum-Resilient Provenance Audit for
                  Machine Learning Supply Chains},
  year         = {2026},
  howpublished = {CS F376 Design Project, BITS Pilani Dubai Campus},
  url          = {https://github.com/adityasharma1307/qresp},
}
```

---

## Licence

This project is released under the [MIT License](LICENSE).
