"""Freeze only the compact reviewed loader source/proof; no ROM or objects."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-loader-funding-1101-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    receipt=O/'funding.json';q=json.loads(receipt.read_text());assert q['passed']
    for p,h in q['bindings'].items():assert sha(p)==h,p
    assert q['cold_Main_ISR']['minimum_ISR_SP']==138
    assert q['optimized_Main']['reserve_above_SMC']>=12 and q['extended_Main']['reserve_above_SMC']>=12
    own=[R/'tools/audit'/n for n in ['prepare_karnov_loader_funding_1101_v6.py','check_karnov_loader_funding_1101_v6.py','freeze_karnov_loader_funding_1101_v6.py']]
    own+=[R/'tools/reference/karnov_loader_funding_1101_v6.md',R/'tools/reference/karnov_combat_carrier_loader_1101_v3.inc']
    generated=[p for p in O.iterdir()if p.suffix in ['.s','.cfg','.inc','.bin','.lbl','.dbg']]
    files=own+[receipt]+generated
    handoff=dict(passed=True,component_only=True,root_modified=False,native=False,installed=False,
        base_ROM_sha256=q['expected_base'],carrier_ownership_granted=False,carrier_code_executed=False,
        pure_transformer='tools/audit/prepare_karnov_loader_funding_1101_v6.py:transform_sources',
        contract='tools/reference/karnov_loader_funding_1101_v6.md',resident_bytes=2430,resident_capacity=2432,
        water_address=0xbb8e,hot_dispatch_source_unchanged=True,new_scratch=[],cold_Main_ISR_reserve=15,
        gameplay_Main_ISR_reserve=12,actual_cold_ISR_cases=49,actual_gameplay_ISR_cases=36,
        source_Main_updates=1238,actual_cold_warm_differentials=12,actual_failure_differentials=12,
        full_header_cases=66,typed_child_ABI_cases=288,full_pickup_cases=48,
        limits=['Source-assembled in-memory model with exact declared native relocation sites; root full object/source relink still required.',
                'CHR1019/1020 remains ungranted. Complete source consumer closure and actual native final candidate are separate gates.',
                'Copied1040-byte original combat component is readback-tested but never executed in this component.'],
        files={p.relative_to(R).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size)for p in files})
    (O/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n');files.append(O/'handoff.json')
    with zipfile.ZipFile(O/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    print(json.dumps(dict(passed=True,packet=str(O/'source-proof.zip'),sha256=sha(O/'source-proof.zip'),bytes=(O/'source-proof.zip').stat().st_size,members=len(files))))
if __name__=='__main__':main()
