"""Checkpoint source-verified ordinary Peach hover without playable admission."""
from pathlib import Path
import json
import shutil
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_functional_roster_visuals58_v1 as B

O=R/'build/smb3plus-peach-float-host-1031-v4';J=O/'joint'
D=R/'docs/qa/checkpoints/2026-10-31/smb3plus-peach-float'
P=R/'docs/qa/checkpoints/2026-10-31/smb3plus-big-toad-kick'
N=R/'build/smb3plus-peach-float-donor-native-1031-v1'


def main():
    assert not D.exists() and not (O/'handoff.json').exists()
    names=['source-stage.json','float-controls-v2.json','wobble-controls-v1.json',
        'graphics-controls-v2.json','body-controls-v5.json','movement-controls-v1.json','vectors-v1.json']
    receipts={n:json.loads(B.read(O/n)) for n in names}
    for d in receipts.values():B.bound(d)
    stage=receipts['source-stage.json'];candidate=stage['candidate']
    assert candidate=='e9f0d09cb744cdf0995a07fc5f6d4b064ac4b33a631fd2e6843dcacbe984975d'
    for n,d in receipts.items():
        if n!='source-stage.json':assert d['passed']
        if 'candidate' in d:assert d['candidate']==candidate
    assert receipts['float-controls-v2.json']['source_cases']==1533
    assert receipts['graphics-controls-v2.json']['exact_graphics_pairs']==9072
    assert receipts['body-controls-v5.json']['source_pixel_cases']==2156
    assert receipts['movement-controls-v1.json']['foreign_movement_pairs']==1344
    assert receipts['vectors-v1.json']['real_vectors']==2084
    parent=json.loads(B.read(P/'handoff.json'));B.bound(parent)
    native=json.loads(B.read(N/'discovery/capture/binding.json'));B.bound(native)
    files={Path(__file__),P/'handoff.json'}
    files.update(O/n for n in names)
    files.update(O/n for n in ['graphics-duplicate-fixture-negative-v1.json',
        'main-build.json','union-build.json','chr-build.json','final-link.json'])
    files.update(R/'tools/audit'/f'prepare_smb3plus_peach_float_host_1031_v{i}.py' for i in range(1,5))
    files.update(R/'tools/reference'/f'smb3plus_peach_float_1031_v{i}.s' for i in range(1,4))
    files.update(R/'tools/audit'/n for n in ['prepare_smb3plus_peach_float_discovery_1031_v1.py',
        'measure_smb3plus_peach_float_1031_v1.py','smb3plus_peach_wobble_controls_1031_v1.py',
        'smb3plus_peach_movement_controls_1031_v1.py','smb3plus_peach_vectors_1031_v1.py'])
    for prefix in ['smb3plus_peach_float_controls','smb3plus_peach_graphics_controls']:
        files.update(R/'tools/audit'/f'{prefix}_1031_v{i}.py' for i in [1,2])
    files.update(R/'build'/p for p in [
        'smb3plus-peach-float-host-1031-v1/wobble-negative-v1.json',
        'smb3plus-peach-float-host-1031-v3/float-negative-v1.json',
        'smb3plus-peach-float-host-1031-v3/source-stage.json',
        'smb3plus-peach-float-code-1031-v1/measurement.json'])
    files.update(J/n for n in ['entrypoint.s','src/smb3_native_controller.inc','src/smb3_mario_art.inc',
        'src/smb3_mario_render.s','smb3plus_float_state.inc','smb3plus_float_source.s','smb3plus_float_data.s'])
    files.update(p for p in N.rglob('*') if p.is_file())
    assert all(p.is_file() and p.is_relative_to(R) for p in files)
    assert all(p.suffix.lower() in ['.py','.s','.inc','.json','.lua','.bin','.txt','.csv','.log','.png'] for p in files)
    assert sum(p.stat().st_size for p in files)<8*1024*1024
    bindings={str(p):B.sha(p) for p in sorted(files)}
    bindings.update({str(J/n):B.sha(J/n) for n in ['candidate.nes','candidate.dbg','candidate.lbl']})
    D.mkdir(parents=True);archive=D/'source-delta-and-donor-results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    d=dict(status='FROZEN_ORDINARY_PEACH_FLOAT_SOURCE_CPU_QUALIFIED_NOT_ADMITTED',source=True,
        native_host=False,installed=False,menu_unlocked=False,candidate=candidate,parent=stage['parent'],
        joint=str(J),parent_checkpoint=str(P),parent_archive_sha256=B.sha(P/'source-delta-and-donor-results.zip'),
        ordinary_original_state_cases=1533,wobble_table_cases=768,exact_graphics_pairs=9072,
        source_pixel_cases=2156,source_palette_cases=28,foreign_movement_pairs=1344,
        actual_interrupt_cases=2084,public_M3_labels_preserved=285,CHR_byte_exact=True,
        source_hover_ticks=160,source_hover_controller_updates=80,
        state='Four bytes5C64..67 inside existing selected17 private overlay; no new global state.',
        limits=stage['limits'],archive_members=len(files),archive_bytes=archive.stat().st_size,
        archive_sha256=B.sha(archive),bindings=bindings)
    B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n')
    for n in ['handoff.json',*names]:shutil.copy2(O/n,D/n)
    (D/'README.md').write_text(
        'Ordinary Peach hover translated from the actual SMB3+ donor, credited to Infidelity. '
        'The native controller-only donor discovery contains three screenshots and bounded RAM/PPU '
        'snapshots. Actual original instructions confirm160 timer ticks at two velocity callbacks per '
        'update:80 updates, not160. The joined genuine controller covers initial jump, landing/reset, '
        'release, water, form gates, signed wobble and expiry.\n\n'
        '1533 original state cases and768 wobble table cases pass. 9072 old/new graphics comparisons '
        'preserve all final registers/maps and every ordered application write except the two explicitly '
        'checked transient form5 low-pointer stores. The low table is exactly form3 plus4; no sprite '
        'pixels change. 2156 original donor pixel cases,28 palettes,1344 foreign movement pairs and2084 '
        'real interrupt cuts pass. Existing disabled Kuribo records remain disclosed failures.\n\n'
        'The retained failures found an A90 helper called while A92 was mapped, missing wobble indices16/48, '
        'and a premature power-form gate in the float-ready producer. A duplicate old graphics fixture '
        'also rejected the already-qualified scratch-pointer relocation; the successor keeps its donor '
        'pixel assertions and the stronger four-identity ordered-write checks. All285 existing M3 labels '
        'and all CHR bytes stay fixed; neighboring Rogue Dawn audio is preserved.\n\n'
        'This is a source checkpoint, not a playable unlock. Native host collisions/menu integration, '
        'Toad kick audio, donor ground-pound/custom stomp delay and special-form/growth consumers remain. '
        'The separately verified66-character ROM in Downloads is unchanged. No videos or frame forests.\n',
        encoding='utf-8',newline='\n')
    print(json.dumps(dict(checkpoint=str(D),candidate=candidate,members=len(files),bytes=archive.stat().st_size)))


if __name__=='__main__':main()
