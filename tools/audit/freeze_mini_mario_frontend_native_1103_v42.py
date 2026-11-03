"""Compact exact frontend/art/animation/controller checkpoint; no ROM copies."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
from prepare_selected_native_packet_v1 import R,sha
import prepare_mini_mario_native_smoke_1103_v25 as S
import prepare_mini_mario_full11_1103_v28 as F
O=R/'build/mini-mario-frontend-final-1103-v42'

def main():
    O.mkdir(exist_ok=True)
    stems=['prepare_mini_mario_animation_1103_v20.py',
        'prepare_mini_mario_native_smoke_1103_v25.py','prepare_mini_mario_native_smoke_1103_v25.lua',
        'prepare_mini_mario_full11_1103_v28.py','prepare_mini_mario_full11_1103_v28.lua',
        *['prepare_mini_mario_native_smoke_1103_v'+str(n)+'.py'for n in [29,30,31,32]],
        *['prepare_mini_mario_full11_1103_v'+str(n)+'.py'for n in [33,34]],
        'prepare_mini_mario_native_final_1103_v36.py','prepare_mini_mario_chr_writers_1103_v38.py',
        'prepare_mini_mario_native_final_1103_v41.py',Path(__file__).name]
    sources=[R/'tools/audit'/n for n in stems];members=set(sources)
    anim=R/'build/mini-mario-animation-1103-v20'
    members.update(anim/n for n in ['animate.s','animate.cfg','animate.bin','animate.lbl','receipt.json'])
    members.update(R/'build'/p for p in ['mini-mario-native-packet-1103-v25/template.json',
        'mini-mario-full11-packet-1103-v28/template.json','mini-mario-full11-packet-1103-v28/gap-policy-negative.json',
        'mini-mario-native-smoke-1103-v31/observer-resolution.json'])
    packets=[R/'build'/p for p in ['mini-mario-native-packet-1103-v25/smoke',
        *['mini-mario-native-smoke-1103-v'+str(n)+'/smoke'for n in [29,30,31,32]],
        *['mini-mario-full11-packet-1103-v'+str(n)+'/full11'for n in [28,33,34]],
        'mini-mario-native-packets-1103-v36/smoke35','mini-mario-native-packets-1103-v36/full36',
        'mini-mario-chr-writers-1103-v38/diagnostic',
        'mini-mario-native-packets-1103-v41/smoke41','mini-mario-native-packets-1103-v41/full41']]
    native=[]
    for p in packets:
        if not(p/'ready.json').exists():continue
        members.add(p/'ready.json')
        if p.parent.name.endswith('v41'):members.update([p/'controller.lua',p/'run.py'])
        bind=p/'capture/binding.json';result=p/'capture/result.json'
        if bind.exists():
            b=json.loads(bind.read_text());assert b['ready_sha256']==sha(p/'ready.json')
            members.add(bind);q=json.loads(result.read_text())if result.exists()else{}
            if result.exists():members.add(result)
            native.append(dict(packet=p.relative_to(R).as_posix(),exit_code=b['exit_code'],
                passed=q.get('passed'),ROM_sha256=b['ROM_sha256'],error=q.get('error'),
                physical_frames=q.get('physical_frames'),source_updates=q.get('source_updates')))
    art=R/'build/mini-mario-menu-1103-v14/mini-art-menu-source-v19.zip'
    assert sha(art)=='56ba5c475ad4d9e6701f14593884f8192ae3fa3de3b0d1a4982ed538c69ab5dd'
    plan=dict(flat=S.source_plan(),gaps=F.source_gap_cases(),
        scope='Isolated source/controller feasibility only; host22 fixtures omit generic nativecollision. Native acceptance is separately listed, with every negative retained.')
    paths=sorted(members);assert all(p.is_file()for p in paths)
    archive=O/'mini-frontend-native-source-v42.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9)as z:
        for p in paths:z.writestr(p.relative_to(R).as_posix(),p.read_bytes())
    manifest={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,SHA256=sha(p))for p in paths}
    with ZipFile(archive)as z:
        assert len(z.namelist())==len(paths)
        for name,row in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==row['SHA256']
    q=dict(frozen=True,ROM_written=False,archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,
        archive_SHA256=sha(archive),members=manifest,
        references=[dict(path=art.relative_to(R).as_posix(),bytes=art.stat().st_size,SHA256=sha(art),
            role='Existing immutable81KB art/menu/officialcompiler/source-input checkpoint reused read-only; not nested/copied.')],
        source_checks=plan,native_results_snapshot=native,
        final_private_ROM_SHA256='b99a24d987d872cbe23069cbe1b200bcd6b28c9be9791841ba5d270e26b39dab',
        scope='Own frontend/indexedart/engineanimation and exact controller sources/proofs only. Root owns final native delivery/release and its acceptance scope. No full-stage claim inferred from prepared41. No outputs pruned.',
        commit_files=[p.relative_to(R).as_posix()for p in sources])
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    (O/'commit-files.txt').write_text('\n'.join(q['commit_files'])+'\n')
    print(json.dumps(dict(frozen=True,archive=str(archive),bytes=q['archive_bytes'],members=len(paths),SHA256=q['archive_SHA256'],native_terminal_snapshots=len(native))))

if __name__=='__main__':main()
