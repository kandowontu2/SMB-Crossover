"""Preserve composed Rogue/current backends and the complete native menu sweep."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/rogue-current-menu-v5'
D=R/'docs/qa/checkpoints/2026-10-30/rogue-current-menu'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    bp=O/'build-proof.json';cp=O/'controls.json'
    b=json.loads(bp.read_text());c=json.loads(cp.read_text())
    expected='f23af095d2b8ed865c7447d2b8ad5ac6cedd02780dedde9d95ab10c80fd7f134'
    assert b['ROM_sha256']==c['ROM_sha256']==sha(O/'candidate.nes')==expected and c['passed']
    assert c['ready']==48 and c['pending']==32
    menu=O/'native/menu';native=json.loads((menu/'result.json').read_text())
    binding=json.loads((menu/'binding.json').read_text())
    assert native['passed']and native['ROM_sha256']==binding['ROM_sha256']==expected
    assert native['slots']==32 and native['alternates']==80 and native['screenshots']==8
    assert native['late_enables']==native['visible_ppu_writes']==binding['exit_code']==0
    inputs=dict(b['source_bindings']);inputs.update(c['source_bindings']);inputs.update(binding['inputs'])
    for p in [bp,cp,Path(__file__).resolve(),O/'native-menu-review.png']:
        inputs[str(p)]=sha(p)
    for p in menu.iterdir():
        if p.is_file():inputs[str(p)]=sha(p)
    for path,h in inputs.items():assert sha(path)==h,path
    D.mkdir(parents=True)
    archive=D/'frozen-source-and-menu-evidence.zip';members={}
    excluded={'.nes','.dbg','.lbl','.map','.exe','.dll','.o','.zip','.mp4','.wav','.nesppuv1'}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,h in inputs.items():
            p=Path(path).resolve()
            if not p.is_relative_to(R)or p.suffix.lower()in excluded or p.name=='screens.bin':continue
            name=p.relative_to(R).as_posix();zi=zipfile.ZipInfo(name,(2026,10,30,0,0,0))
            zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,p.read_bytes());members[name]=h
    with zipfile.ZipFile(archive)as z:
        assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    report=dict(passed=True,status='PRIVATE_CURRENT_BACKENDS_COMPOSED_CPU_AND_NATIVE_MENU_PASS_GAMEPLAY_ROUTE_PENDING',
        ROM_sha256=expected,shared_installation=False,source_build_exact_backend_reproduction=True,
        menu=dict(slots=32,profiles=80,private_ready=48,private_pending=32,native=native),
        restored_backends=['Kamikaze Mario authentic full pose renderer and NMI skin publisher','Game Boy Pit pose/menu/CHR component'],
        native_new_entry='Rogue Dawn raw2/variant1; genuine native backend and victory handling retained.',
        source_checks=list(c['checks']),
        visual_review='Root visually checked all eight saved menu views as a contact sheet, including all four rows and late alternates. No exhaustive per-frame visual claim.',
        sentinel_correction=c['checks']['actual_existing_backend_entrypoints'],
        limitations=['Native Rogue1-1 replay is separate and not yet qualified by this checkpoint.',
                     'No every-powerup/all-character campaign or 60Hz claim.',
                     'Bill native performance comparison still required before shared installation.',
                     'Independent four-host/Quick/Arthur source branches are not included.'],
        archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,members=len(members)),
        members=members,runtime_references=inputs)
    (D/'root-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,members=len(members),archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
