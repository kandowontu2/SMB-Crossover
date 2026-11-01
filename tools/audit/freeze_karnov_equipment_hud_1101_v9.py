"""Freeze compact unallocated equipment HUD source, atlas and aggregate proof."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-equipment-hud-1101-v9';V7=R/'build/karnov-options-component-1101-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    a=json.loads((O/'assembly.json').read_text());q=json.loads((O/'CPU-controls.json').read_text())
    assert a['passed']and q['passed']and not q['native']
    for x in[a,q]:
        for p,h in x['bindings'].items():assert sha(p)==h,p
    own=[R/'tools/audit'/n for n in['prepare_karnov_equipment_hud_1101_v9.py','check_karnov_equipment_hud_1101_v9.py','freeze_karnov_equipment_hud_1101_v9.py']]
    own+=[R/'tools/reference'/n for n in['karnov_equipment_hud_1101_v9.inc','karnov_equipment_hud_1101_v9.md']]
    fixture=[V7/'component.bin',V7/'assembly.json',R/'inc/charmap.inc',R/'tools/audit/check_karnov_options_1101_v7.py']
    generated=[p for p in O.iterdir()if p.is_file()and p.suffix in['.s','.cfg','.inc','.bin','.dbg','.lbl','.chr','.txt','.png','.json']and p.name!='handoff.json']
    files=own+fixture+generated
    h=dict(passed=True,component_only=True,native=False,installed=False,host_modified=False,code_lease_granted=False,
        source_component_bytes=440,split=dict(KR_OPTIONS_ROM=361,KR_COMBAT_ROM=79),font_pages=1,font_proposal=1023,font_granted=False,
        cache_proposal=[0xc87a,0xc880],cache_granted=False,worker_executions=q['worker_executions'],source_pairs=q['source'],
        exact_consumer=q['consumer'],cache_ownership=q['cache_ownership'],contract='tools/reference/karnov_equipment_hud_1101_v9.md',
        transformer='tools/audit/prepare_karnov_equipment_hud_1101_v9.py:split_source',limits=q['limits'],
        files={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in files})
    (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n');files.append(O/'handoff.json')
    with zipfile.ZipFile(O/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    print(json.dumps(dict(passed=True,packet=str(O/'source-proof.zip'),sha256=sha(O/'source-proof.zip'),bytes=(O/'source-proof.zip').stat().st_size,members=len(files))))
if __name__=='__main__':main()
