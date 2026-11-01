"""Freeze compact Bomb/Ladder source/proof, without donor ROM/PRG or objects."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-equipment-component-1101-v8';V7=R/'build/karnov-options-component-1101-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    a=json.loads((O/'assembly.json').read_text());q=json.loads((O/'CPU-controls.json').read_text())
    assert a['passed']and q['passed']and not q['native']
    for x in[a,q]:
        for p,h in x['bindings'].items():assert sha(p)==h,p
    own=[R/'tools/audit'/n for n in['prepare_karnov_equipment_1101_v8.py','check_karnov_equipment_1101_v8.py','freeze_karnov_equipment_1101_v8.py']]
    own+=[R/'tools/reference'/n for n in['karnov_equipment_1101_v8.inc','karnov_equipment_1101_v8.md']]
    fixture=[V7/'component.bin',V7/'assembly.json']
    fixture+=[R/'build/karnov-original-source-1101-v1/source'/n for n in['portable_dispatch.inc','original_dispatch.inc']]
    generated=[p for p in O.iterdir()if p.is_file()and p.suffix in['.s','.cfg','.inc','.bin','.dbg','.lbl','.json']and p.name!='handoff.json']
    files=own+fixture+generated
    handoff=dict(passed=True,component_only=True,native=False,installed=False,code_lease_granted=False,
        donor_sha256=a['donor_sha256'],source_component_bytes=a['source_component_bytes'],test_read_backend_bytes=a['test_read_backend_bytes'],
        original_island_bytes=a['original_island_bytes'],source_pairs=q['source_pairs'],engine_executions=q['engine_executions'],
        minimum_standalone_SP=q['minimum_standalone_SP'],source_trace_sha256=q['source_trace_sha256'],
        contract='tools/reference/karnov_equipment_1101_v8.md',imports=a['imports'],new_persistent_RAM=[],borrowed_ZP=[3,4],
        host_equipment_whitelist_unchanged=[0,3,7],limits=q['limits'],
        options_fixture_source_packet=dict(path='build/karnov-options-component-1101-v7/source-proof.zip',sha256=sha(V7/'source-proof.zip')),
        files={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in files})
    (O/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n');files.append(O/'handoff.json')
    with zipfile.ZipFile(O/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    print(json.dumps(dict(passed=True,packet=str(O/'source-proof.zip'),sha256=sha(O/'source-proof.zip'),bytes=(O/'source-proof.zip').stat().st_size,members=len(files))))
if __name__=='__main__':main()
