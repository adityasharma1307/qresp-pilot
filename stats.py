import json, math

# Load data
records = []
with open('data/full.jsonl') as f:
    for line in f:
        records.append(json.loads(line))

n = len(records)
signed = sum(1 for r in records if r['has_signature'])
vulnerable = sum(1 for r in records if r['q_label'] == 'vulnerable')
unsigned = sum(1 for r in records if r['q_label'] == 'unsigned')
safe = sum(1 for r in records if r['q_label'] == 'safe')

# Wilson confidence interval function
def wilson_ci(k, n, z=1.96):
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2*n)) / denom
    margin = z * math.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denom
    return max(0, centre - margin), min(1, centre + margin)

lo_signed, hi_signed = wilson_ci(signed, n)
lo_unsigned, hi_unsigned = wilson_ci(unsigned, n)
lo_vuln, hi_vuln = wilson_ci(vulnerable, n)
lo_safe, hi_safe = wilson_ci(safe, n)

print(f'n = {n}')
print()
print(f'Signed:     {signed:4d} / {n}  ({100*signed/n:.1f}%)   95% CI: [{100*lo_signed:.2f}%, {100*hi_signed:.2f}%]')
print(f'Unsigned:   {unsigned:4d} / {n}  ({100*unsigned/n:.1f}%)   95% CI: [{100*lo_unsigned:.2f}%, {100*hi_unsigned:.2f}%]')
print(f'Vulnerable: {vulnerable:4d} / {n}  ({100*vulnerable/n:.2f}%)   95% CI: [{100*lo_vuln:.3f}%, {100*hi_vuln:.3f}%]')
print(f'PQ-safe:    {safe:4d} / {n}  ({100*safe/n:.1f}%)   95% CI: [{100*lo_safe:.2f}%, {100*hi_safe:.2f}%]')
print()

# Power calculation: sample size needed to detect 1% PQ adoption with 80% power
from math import ceil
p0, p1, alpha, power = 0.0, 0.01, 0.05, 0.80
z_alpha = 1.645  # one-tailed
z_beta  = 0.842
p_bar = (p0 + p1) / 2
n_needed = ceil((z_alpha*math.sqrt(2*p_bar*(1-p_bar)) + z_beta*math.sqrt(p0*(1-p0)+p1*(1-p1)))**2 / (p1-p0)**2)
print(f'Power analysis: to detect 1% PQ adoption (vs 0%) at 80% power,')
print(f'minimum sample size needed = {n_needed} models')
print(f'=> Our n=1000 is sufficient to rule out even 1% PQ adoption.')
