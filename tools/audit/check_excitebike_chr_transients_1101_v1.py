"""Rebind actual native publication/lag-NMI instruction cuts to Excitebike pages.

Reuses the existing source test, not its previous result. No ROM mutation.
"""
from pathlib import Path
import hashlib, json, sys
R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
O = R/'build/excitebike-pose-1101-v3'
ROM = R/'build/shinobi-camera-1101-v20/candidate.nes'


def main():
    original = R/'tools/audit/check_metal_storm_chr_publication_1101_v10.py'
    curpath = R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
    domains_path = R/'build/metal-storm-chr-closure-1101-v10/source-domains.json'
    raw = ROM.read_bytes()
    cur = json.loads(curpath.read_text())
    changed = []
    for span in cur['native_spans']:
        actual = raw[span['offset']:span['offset']+span['size']]
        if actual != bytes.fromhex(span['hex']):
            assert span['name']=='MaaLagChrGuard'
            assert actual.hex()=='ad0260d006ad0a73c902603860eaeaea'
            changed.append(dict(name=span['name'], old=span['hex'], new=actual.hex()))
            span['hex']=actual.hex()
    cur['current_ROM_sha256']=hashlib.sha256(raw).hexdigest()
    source = original.read_text()
    replacements = {
        "OUT=ROOT/'build/metal-storm-chr-closure-1101-v10'": "OUT=ROOT/'build/excitebike-pose-1101-v3'",
        'TARGETS=set([247,248,249,250]+list(range(494,503))+list(range(827,832)))': 'TARGETS=set(range(728,740))',
        "cp=OUT/'current-consumer-inputs.json';cur=json.loads(cp.read_text());domains=json.loads((OUT/'source-domains.json').read_text());assert domains['passed'];raw=(ROOT/'build/kirby-owner-main-1101-v2/candidate.nes').read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256']":
            "cp=CURPATH;cur=CUR;domains=json.loads(DOMAINPATH.read_text());assert domains['passed'];raw=ROM.read_bytes();assert hashlib.sha256(raw).hexdigest()==cur['current_ROM_sha256']",
        'lowtests=list(range(238,247))+list(range(59,64))': 'lowtests=list(range(216,228))',
        'for oldpage in[493,832]:': 'for oldpage in[493,724,832]:',
        'for rawchar in range(1,36):': 'for rawchar in range(1,37):',
        'assert {500,501,502,827,828,829,830,831}<=set(transient_targets),transient_targets': 'assert TARGETS<=set(transient_targets),transient_targets',
        "OUT/'source-domains.json'": 'DOMAINPATH',
    }
    for old,new in replacements.items():
        assert old in source,old
        source=source.replace(old,new)
    env=dict(__file__=str(original), __name__='excitebike_publication_check',
        CUR=cur, CURPATH=curpath, DOMAINPATH=domains_path, ROM=ROM)
    exec(compile(source,str(original),'exec'),env)
    env['main']()
    result=json.loads((O/'publication-CPU-controls.json').read_text())
    result['test_source_SHA256']=hashlib.sha256(source.encode()).hexdigest()
    result['wrapper_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['current_native_span_changes']=changed
    result['scope']='Actual current setter, publisher, native menu restore and lag NMI instruction cuts. All candidate pages occur as unpublished transient pairs. This is not complete gameplay publisher closure or a resource grant.'
    (O/'publication-CPU-controls.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
