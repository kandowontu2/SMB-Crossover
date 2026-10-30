"""Freeze the dense PN graphics layout and conditional private Arthur budget."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
O=R/'build/parodius-chr-compact-v1'
D=R/'docs/qa/checkpoints/2026-10-30/parodius-dense-chr'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    bp=O/'build-proof.json';cp=O/'controls.json'
    build=json.loads(bp.read_text());controls=json.loads(cp.read_text())
    assert controls['passed'] and build['candidate_sha256']==controls['ROM_sha256']==sha(O/'candidate.nes')
    assert build['PRG_changed_bytes']==54 and controls['actual_pose_cases']==786
    assert controls['decoded_actual_OAM_pairs']==1940
    parent=R/'build/character-host-union-v5/handoff.json'
    old=json.loads(parent.read_text());bindings=dict(old['bindings'])
    for path,h in build['source_bindings'].items():
        assert sha(path)==h,path
        bindings[path]=h
    for p in [bp,cp,parent,O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',
              R/'tools/audit/prepare_parodius_chr_compact_v1.py',
              R/'tools/audit/parodius_chr_compact_controls_v1.py',Path(__file__).resolve()]:
        bindings[str(p)]=sha(p)
    for path,h in bindings.items():assert sha(path)==h,path
    D.mkdir(parents=True)
    archive=D/'frozen-source-packet.zip';members={}
    exclude={'.nes','.dbg','.lbl','.map','.exe','.dll','.o','.zip','.mp4','.wav','.nesppuv1'}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,h in bindings.items():
            p=Path(path).resolve()
            if not p.is_relative_to(R)or p.suffix in exclude:continue
            name=p.relative_to(R).as_posix()
            info=zipfile.ZipInfo(name,(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes());members[name]=h
    with zipfile.ZipFile(archive)as z:
        assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    result=dict(passed=True,status='SOURCE_CPU_QUALIFIED_PRIVATE_LAYOUT_AND_ALLOCATION',
        ROM_sha256=build['candidate_sha256'],parent_ROM_sha256=build['parent_sha256'],
        source_only=True,shared_installation=False,native_test_pending=True,
        result='Lossless192→36page Parodius layout,54 changed PRG table bytes, no code/RAM/CPU changes.',
        physical_layout=dict(Parodius=dict(first=832,end_exclusive=868),
                             freed=dict(first=868,end_exclusive=1024,bytes=159744)),
        private_Arthur_successor_reservation=dict(first=868,end_exclusive=884,bytes=16384,
            allowed_sprite_windows=[0,6,7],selected_owner='raw32 gameplay/Ready only',
            dependence='Must compile this dense PN alias table/death table and split memory config; never include the original192KB PN CHR producer over this range.',
            window7='Common world-white masks permitted only while Arthur owns the frame, based on actual656-case native-world exclusion audit. Restore/reinitialize on profile/menu/scene changes.',
            old_247_251_reservation='Retained until the new qualified renderer replaces it, then explicitly retire it.',
            palette='Preserve source opaque black and exact visible color roles. Composite color layers are native art, independent of optional outlines setting.'),
        controls={k:v for k,v in controls.items()if k not in ['rows','changed_table_references']},
        source_closure=dict(verified_bindings=len(bindings),parent_handoff_sha256=sha(parent),
                            parent_source_checkpoint='docs/qa/checkpoints/2026-10-30/four-host-current-menu-native'),
        archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,members=len(members)),
        members=members,runtime_references=bindings,
        limitations=['Private layout only; complete native screen comparison still pending.',
                     'Parent four-host Bill performance regression remains; no shared or Downloads update.',
                     'Final integration must preserve dense aliases in every future graphics producer.'])
    (D/'root-review-and-reservations.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(D),receipt_sha256=sha(D/'root-review-and-reservations.json'),
                         archive_bytes=archive.stat().st_size,members=len(members))))


if __name__=='__main__':main()
