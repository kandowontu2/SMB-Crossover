"""Offline co-resident tile-pair packing experiment, not an executable port.

Keep the first 16 KiB unchanged, then allow every old 1 KiB page to remap its
32 8x16 tile-pair slots into a new page. Every pattern on an old page must still
coexist. This does not yet rewrite CPU tile references, mapper publication or
prove the MMC3 background/IRQ timing requirements.
"""
from pathlib import Path
import hashlib, json, random

R = Path(__file__).resolve().parents[2]
O = R/'build/verification/mmc3-full-roster-feasibility-ne'
raw = (R/'build/smb-crossover-mmc5-expanded.nes').read_bytes()
data = raw[16+1048576:]
patterns = sorted({data[i:i+32] for i in range(0, len(data), 32)})
ids = {p:i for i,p in enumerate(patterns)}
pages = [tuple(ids[data[i+j:i+j+32]] for j in range(0, 1024, 32)) for i in range(0, len(data), 1024)]
pin_count = 16
pinned = [set(p) for p in pages[:pin_count]]
sets = sorted(set(frozenset(p) for p in pages), key=lambda p: (-len(p), sorted(p)))
best = None
trials = []
for seed in range(32):
    rng = random.Random(seed)
    groups = {}
    for s in sets:
        groups.setdefault(len(s), []).append(s)
    ordered = []
    for n in sorted(groups, reverse=True):
        group = groups[n][:]
        if seed:
            rng.shuffle(group)
        ordered.extend(group)
    bins = [s.copy() for s in pinned]
    for s in ordered:
        choices = []
        for i, b in enumerate(bins):
            added = len(s-b)
            if not added:
                choices = [(0, 0, i)]
                break
            if i >= pin_count and len(b)+added <= 32:
                choices.append((added, -len(b), i))
        if choices:
            _, _, i = min(choices)
            bins[i].update(s)
        else:
            bins.append(set(s))
    trials.append(dict(seed=seed, pages=len(bins)))
    if best is None or len(bins) < len(best):
        best = bins
packed = list(pages[:pin_count]) + [tuple(sorted(s))+tuple([next(iter(s))])*(32-len(s)) for s in best[pin_count:]]
blob = b''.join(patterns[p] for page in packed for p in page)
assert blob[:pin_count*1024] == data[:pin_count*1024]
mapping = []
for old in pages:
    s = set(old)
    index = next(i for i, new in enumerate(packed) if s.issubset(new))
    remap = [packed[index].index(p) for p in old]
    reconstructed = b''.join(patterns[packed[index][j]] for j in remap)
    assert reconstructed == b''.join(patterns[j] for j in old)
    mapping.append(dict(page=index, pair_slots=remap))
(O/'co-resident-packing.chr').write_bytes(blob)
(O/'co-resident-pair-map.json').write_text(json.dumps(mapping, separators=(',', ':'))+'\n')
report = dict(passed=True, source_ROM_sha256=hashlib.sha256(raw).hexdigest(),
    original_CHR_bytes=len(data), exact_pair_dictionary_bytes=len(patterns)*32,
    pinned_first_16KiB_exact=True, packed_pages=len(packed), packed_bytes=len(blob),
    fits_256KiB_storage=len(blob) <= 262144, required_saving_bytes=max(0,len(blob)-262144),
    old_pages_reconstructed_exactly=len(mapping), every_pair_slot_checked=len(mapping)*32,
    packed_sha256=hashlib.sha256(blob).hexdigest(), trials=trials,
    scope='Offline exact 8x16-pair content/co-residency proof only. No tile flips, pixel changes, animation cuts or input changes. All old 1KiB pages reconstruct exactly. Native background/font/page-pair constraints beyond pinned first16KiB, actual tile-index code/data rewrites and mapper/IRQ timing remain unimplemented; this CHR file is not a working ROM.')
(O/'co-resident-packing-proof.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'trials'}, indent=2))
