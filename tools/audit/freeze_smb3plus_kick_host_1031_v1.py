"""Freeze the source kick join and bounded donor discovery, without admission."""
from pathlib import Path
import json
import shutil
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_functional_roster_visuals58_v1 as B

O=R/'build/smb3plus-kick-host-1031-v1';J=O/'joint'
P=R/'docs/qa/checkpoints/2026-10-31/smb3plus-body-palette-host'
D=R/'docs/qa/checkpoints/2026-10-31/smb3plus-big-toad-kick'


def main():
    assert not D.exists() and not (O/'handoff.json').exists()
    stage=json.loads(B.read(O/'source-stage.json'))
    controls=json.loads(B.read(O/'kick-controls-v1.json'))
    vectors=json.loads(B.read(O/'kick-vectors-v3.json'))
    caller=R/'build/smb3plus-kick-caller-1031-v1/caller-controls.json'
    c=json.loads(B.read(caller));parent=json.loads(B.read(P/'handoff.json'))
    for receipt in [stage,controls,vectors,c,parent]:B.bound(receipt)
    assert stage['candidate']=='4a2a9908d47075df0a1d26660e5e42a2a94bf5db288a5246a2cb083800a453c2'
    assert controls['candidate']==vectors['candidate']==stage['candidate']
    assert controls['passed'] and vectors['passed'] and c['passed']
    assert controls['source_kick_cases']==432 and controls['foreign_movement_pairs']==1344
    assert vectors['real_vectors']==180 and len(c['cases'])==56
    files={Path(__file__),caller,P/'handoff.json'}
    files.update(R/'tools/audit'/f'prepare_smb3plus_kick_discovery_1031_v{i}.py' for i in range(1,4))
    files.update(R/'tools/audit'/name for name in ['smb3plus_kick_caller_1031_v1.py',
        'prepare_smb3plus_kick_host_1031_v1.py','smb3plus_kick_host_controls_1031_v1.py'])
    files.update(R/'tools/audit'/f'smb3plus_kick_vectors_1031_v{i}.py' for i in range(1,4))
    files.update(O/name for name in ['source-stage.json','kick-controls-v1.json','kick-vectors-v3.json',
        'kick-vector-negative-v1.json','kick-vector-negative-v2.json',
        'main-build.json','union-build.json','chr-build.json','final-link.json'])
    files.update(J/name for name in ['src/smb3_mario_motion.s','src/smb3_native_controller.inc',
        'src/smb3_mario_art.inc','entrypoint.s','smb3plus_kick_host.s'])
    for i in range(1,4):
        files.update(p for p in (R/f'build/smb3plus-kick-donor-native-1031-v{i}').rglob('*') if p.is_file())
    assert all(p.is_file() and p.is_relative_to(R) for p in files)
    assert all(p.suffix.lower() in ['.py','.s','.inc','.json','.lua','.bin','.txt','.csv','.log','.png'] for p in files)
    assert sum(p.stat().st_size for p in files)<4*1024*1024
    bindings={str(p):B.sha(p) for p in sorted(files)}
    bindings.update({str(J/name):B.sha(J/name) for name in ['candidate.nes','candidate.dbg','candidate.lbl']})
    bindings[str(P/'source-only.zip')]=B.sha(P/'source-only.zip')
    D.mkdir(parents=True)
    archive=D/'source-delta-and-donor-results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    d=dict(status='FROZEN_BIG_TOAD_KICK_SOURCE_JOIN_NOT_ADMITTED',source=True,
        native_host=False,installed=False,menu_unlocked=False,candidate=stage['candidate'],
        parent=stage['parent'],parent_checkpoint=str(P),parent_archive_sha256=B.sha(P/'source-only.zip'),
        joint=str(J),donor_controller_cases=56,source_kick_cases=432,
        foreign_movement_pairs=1344,actual_vector_cases=180,public_M3_labels_preserved=285,
        CHR_byte_exact=True,new_RAM_bytes=0,retired_constant_high_tables=5,
        archive_sha256=B.sha(archive),archive_bytes=archive.stat().st_size,archive_members=len(files),
        limits=stage['limits'],bindings=bindings)
    B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n')
    for name in ['handoff.json','source-stage.json','kick-controls-v1.json','kick-vectors-v3.json',
                 'kick-vector-negative-v1.json','kick-vector-negative-v2.json']:
        shutil.copy2(O/name,D/name)
    (D/'README.md').write_text(
        'Big Toad kick source join, not a playable unlock. The genuine native donor B-edge snapshot '
        'was followed through the original controller in56 explicit CPU variants. Only dry big-form '
        'GndMov_Big invokes the donor kick, after SoarJumpFallFrame. The host now calls the translated '
        'kick at that exact point using existing Player_TailAttack, its12..6 timer, frame2D and '
        'QLevel2=$10 request. No independent attack timer or new RAM.\n\n'
        '432 cases match the original timer/frame/sound-request/Y outputs. 1344 old/new Mario, Luigi '
        'and Peach movement pairs preserve registers/flags, ordered application writes and final maps. '
        '180 genuine interrupt cases cut45 emitted instruction sites. The first fixture disconnected '
        'the serial controller during normal NMI; its changed inputs are retained as a negative. The '
        'second assumed BankPRGC had no redundant LDA between shadow and hardware stores. The '
        'successor models real serial B input and classifies only that exact emitted PC/byte sequence, '
        'while retaining live registers, stack,33SMC and mapper assertions.\n\n'
        'All285 pre-existing M3 labels and all CHR bytes stay fixed. A fifth retired constant81-byte '
        'high-table span holds the source routine; a46-byte existing-bank wrapper maps/restores C '
        'around the original native step. Rogue Dawn neighboring audio is not overwritten. This '
        'delta depends on the separately tracked body/palette parent source archive named in the '
        'handoff. It includes the bounded donor discovery and parser failure; no ROM/object/debug '
        'binaries, videos or image forests.\n\n'
        'Peach float, other special-form consumers, native host gameplay and admission remain. The '
        'original kick sound request is generated but the existing host still clears it without '
        'playing that effect. This checkpoint must not be described as a complete Toad integration. '
        'Downloads instead contains the independently verified66-character Bowser WIP.\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(checkpoint=str(D),candidate=d['candidate'],members=len(files),
        bytes=archive.stat().st_size,source_only=True,native_host=False)))


if __name__=='__main__':main()
