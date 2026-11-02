"""Compact checkpoint of the qualified, still-gated Bub/Bob frontend proposal."""
from pathlib import Path
import sys,json,zipfile,hashlib
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import audit_bub_menu_frontend_1102_v1 as F
O=F.O

def main():
    receipt_names=['frontend-closure.json','flag-proposal.json','art-proposal.json','controls-proposal.json','art-CPU-closure.json']
    for name in receipt_names:assert json.loads((O/name).read_text())['passed'],name
    sources=[R/'tools/audit'/name for name in ['audit_bub_menu_frontend_1102_v1.py','propose_bub_menu_flags_1102_v1.py','propose_bub_menu_art_1102_v1.py','propose_bub_menu_controls_1102_v1.py','check_bub_menu_art_1102_v1.py',Path(__file__).name]]
    sources.append(R/'docs/qa/bub-menu-readiness-1102-v1.md')
    generated=[O/name for name in receipt_names+['start-flags.s','start-flags.cfg','start-flags.bin','menu-stream.s','menu-stream.cfg','menu-stream.bin','pending-static.s','pending-static.cfg','pending-static.bin','menu-controls.s','menu-controls.cfg','menu-controls.bin']]
    # Each producer/qualification receipt's local bindings must remain exact.
    for name in ['flag-proposal.json','art-proposal.json','controls-proposal.json','art-CPU-closure.json']:
        q=json.loads((O/name).read_text())
        for path,digest in q['bindings'].items():assert F.sha(R/path)==digest,(name,path)
    filelist={p.relative_to(R).as_posix():F.sha(p)for p in sources+generated}
    archive=O/'frontend-source-checkpoint.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sources+generated:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert all(hashlib.sha256(z.read(name)).hexdigest()==digest for name,digest in filelist.items())
    q=dict(passed=True,proposal_only=True,ROM_written=False,menu_admitted=False,native_playable=False,source_base_SHA256=F.PIN,
        checkpoint=archive.relative_to(R).as_posix(),checkpoint_SHA256=F.sha(archive),bindings=filelist,
        source_files_to_stage=[p.relative_to(R).as_posix()for p in sources],
        commands=[f'python -B tools/audit/run_bounded_build_v1.py --resume --output build/bub-menu-integration-1102-v1 --timeout 300 -- python -B tools/audit/{name}'for name in['audit_bub_menu_frontend_1102_v1.py','propose_bub_menu_flags_1102_v1.py','propose_bub_menu_art_1102_v1.py','propose_bub_menu_controls_1102_v1.py','check_bub_menu_art_1102_v1.py',Path(__file__).name]],
        root_review_remaining=['Grant exact static art/data/FmPending entry and49B initializer+same677B rewrite.','Compose only exact approved diffs over formal1cd8 rebase, retaining latest Metal.','Bind final owner retirement and authenticated backend Fresh to bit7; no private cold execution in OperMode0.','Root native UI/BT/CF/backend qualification; confirmation gate remains SEC at physical66 AD64 until approved.'],
        active_output_budget=dict(bytes=16000000,files=128))
    (O/'frontend-source-freeze.json').write_text(json.dumps(q,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in files)<16000000 and len(files)<=128
    print(json.dumps(dict(passed=True,checkpoint=q['checkpoint'],checkpoint_SHA256=q['checkpoint_SHA256'],bytes=sum(p.stat().st_size for p in files),files=len(files),source_files_to_stage=q['source_files_to_stage'])))
if __name__=='__main__':main()
