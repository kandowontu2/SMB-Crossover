"""Extend the verified publisher tests to the proposed Shinobi CHR pages."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
O=R/'build/shinobi-chr-closure-1101-v1'
V=R/'build/metal-storm-chr-closure-1101-v10'
TARGETS=set(range(503,511))|{513,515,516,517}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    O.mkdir(exist_ok=True)
    domains=json.loads((V/'source-domains.json').read_text())
    assert domains['passed']
    collisions={name:sorted(TARGETS&set(d['physical_pages'])) for name,d in domains['exact_source_domains'].items() if TARGETS&set(d['physical_pages'])}
    # The historical WWF all-byte superset wraps into upper2. Retain that
    # unresolved collision explicitly; this CPU publication test cannot grant
    # resources or prove the legal selector domain.
    for name in ['current-consumer-inputs.json','source-domains.json']:
        shutil.copyfile(V/name,O/name)
    current=R/'build/kirby-approach-owner-1101-v3/candidate.nes'
    raw=current.read_bytes()
    inputs=json.loads((O/'current-consumer-inputs.json').read_text())
    for span in inputs['native_spans']:
        assert raw[span['offset']:span['offset']+span['size']]==bytes.fromhex(span['hex']),span['name']
    inputs['current_ROM_sha256']=sha(current)
    (O/'current-consumer-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
    source=R/'tools/audit/check_metal_storm_chr_publication_1101_v10.py'
    text=source.read_text()
    old="OUT=ROOT/'build/metal-storm-chr-closure-1101-v10'"
    assert text.count(old)==1
    text=text.replace(old,"OUT=ROOT/'build/shinobi-chr-closure-1101-v1'")
    text=text.replace("ROOT/'build/kirby-owner-main-1101-v2/candidate.nes'", "ROOT/'build/kirby-approach-owner-1101-v3/candidate.nes'")
    old='TARGETS=set([247,248,249,250]+list(range(494,503))+list(range(827,832)))'
    assert text.count(old)==1
    text=text.replace(old,'TARGETS=set(range(503,511))|{513,515,516,517}')
    old='lowtests=list(range(238,247))+list(range(59,64))'
    assert text.count(old)==1
    text=text.replace(old,'lowtests=list(range(247,255))+[1,3,4,5]')
    old='assert {500,501,502,827,828,829,830,831}<=set(transient_targets),transient_targets'
    assert text.count(old)==1
    text=text.replace(old,'assert set(range(503,511))<=set(transient_targets),transient_targets')
    # Execute the installed successor after checking every imported native span.
    (O/'publication-check.py').write_text(text)
    (O/'preparation.json').write_text(json.dumps(dict(
        passed=True,proposed_pages=sorted(TARGETS),resource_granted=False,
        historical_conservative_collisions=collisions,publication_execution_baseline=sha(current),
        pending=['Expanded publication test','Full legacy low-page and current367266 writer preservation closure'],
        bindings={str(p):sha(p) for p in [Path(__file__),source,V/'source-domains.json',V/'consumer-closure.json',O/'publication-check.py']}
    ),indent=2)+'\n')

if __name__=='__main__':main()
