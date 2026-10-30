"""Preserve the source and exact native proof of Rogue's victory presentation."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile

from checkpoint_roster_packets_v1 import verify

R=Path(__file__).resolve().parents[2]
UNIT=R/'build/rogue-dawn-victory-pose-v4'
RUN=R/'build/verification/rogue-dawn-victory-native-easy-v1'
REPORT=R/'docs/qa/rogue-dawn-victory-pose-2026-10-30.json'
DEST=R/'docs/qa/checkpoints/2026-10-30/rogue-dawn-victory-pose'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def binding(path):
    p=Path(path).resolve()
    return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))


def main():
    assert not DEST.exists() and not REPORT.exists()
    inputs={}
    for name in ['handoff.json','build.json','controls.json','caller-edges.json']:
        p=UNIT/name
        d=json.loads(p.read_text())
        assert d['passed']
        verify(d,inputs)
        inputs[str(p)]=sha(p)
    ready=json.loads((RUN/'ready.json').read_text())
    for p,h in ready['bindings'].items():assert sha(p)==h,p
    inputs.update(ready['bindings'])
    result=json.loads((RUN/'result.json').read_text())
    review=json.loads((RUN/'review.json').read_text())
    budget=json.loads((RUN/'capture-budget.json').read_text())
    picture=json.loads((RUN/'actual-victory-walk.json').read_text())
    assert result['passed'] and result['zero_deaths'] and result['cheats_off']
    assert result['actual_mode']==0 and result['real_1_2_control_updates']>=25
    assert result['ROM_sha256']==ready['ROM_sha256']==sha(UNIT/'candidate.nes')
    assert review['passed'] and not review['agent_visual_review']
    assert budget['owned_process_only'] and budget['returncode']==0 and not budget['violations']
    assert picture['selected_image_count_with_marker_sheet']==8 and picture['trace']['engine']=='5'
    assert picture['PNG_sha256']==sha(RUN/'actual-victory-walk.png')
    for p,h in picture['bindings'].items():assert sha(p)==h,p
    files=[p for p in RUN.iterdir() if p.is_file()]
    assert len(files)<=64 and sum(p.stat().st_size for p in files)<600_000_000
    inputs.update({str(p):sha(p) for p in files})
    extras=[Path(__file__),R/'tools/audit/rogue_dawn_victory_frame_v1.py']
    for folder in [UNIT,R/'build/rogue-dawn-victory-pose-v1',
                   R/'build/rogue-dawn-victory-pose-v2',R/'build/rogue-dawn-victory-pose-v3']:
        extras.extend(folder.glob('*negative*.json'))
        extras.extend(folder.glob('negative*.json'))
        extras.extend(folder.glob('builder-draft.py'))
    for p in extras:inputs[str(p.resolve())]=sha(p)
    report=dict(status='Private source/native qualified victory pose; shared full-roster integration remains open',
        installed=False,ROM=binding(UNIT/'candidate.nes'),parent=binding(R/'build/rogue-dawn-flagpole-v1/candidate.nes'),
        implementation=dict(new_RAM=0,standing_source_frame=8,automatic_SMB_engines=[4,5],
            source_motion_action_health_radii_unchanged=True,
            hidden_frame_fix='Actual visibility predecessor permits automatic victory when the source stopped on literal F7 hurt flash.',
            display='Authentic source standing records and palette contract; unsupported costume still empty; original death descriptors and all CHR identical.',
            caller='Actual two-site collision dispatch retains X; dead incoming A/P removed to fit the visibility guard. Source-built absolute references relinked.'),
        CPU_checks={name:{k:len(v) for k,v in json.loads((UNIT/name).read_text())['checks'].items()}
                    for name in ['controls.json','caller-edges.json']},
        native=dict(result=result,review=binding(RUN/'review.json'),outputs=[binding(p)for p in files]),
        root_visual_review=dict(selected_images_viewed=8,all_frame_visual_review=False,
            confirmed='Seven whole marker frames reviewed for menu/lives/gameplay/powerup/endpoint context. '
                'The eighth actual PPU frame5465 shows Rogue standing on the ground during castle movement at worldX3210,Y176, replacing the frozen airborne pose.',
            source_scope='Private predecessor frontend shown here; current shared32-slot80-profile menu still needs composition.'),
        retained_negatives='Early drawing drafts mishandled F7/unsupported costume; old full-DrawAll test omitted the legitimate source weapon-slot iterator. '
            'Current consumer proof permits only its exact STX writer to D0/E0/F0 and verifies every other source byte. '
            'One attempted interrupt offset was a CMP operand; corrected to the actual LDA-zero-page instruction boundary.',
        storage=dict(workspace_bytes_at_native_preflight=budget['workspace_bytes'],workspace_cap=70_000_000_000,
            lossless_container=binding(RUN/'captures.nesppuv1'),per_frame_files=0),
        open=['Shared source/menu/audio composition and admission','Hard and every-powerup earned coverage',
              'Shortcut and remaining coin/vine/axe/scene transitions','Performance optimization; no constant60Hz claim'])
    REPORT.write_text(json.dumps(report,indent=2)+'\n')
    inputs[str(REPORT)]=sha(REPORT)
    DEST.mkdir(parents=True)
    archive=DEST/'frozen-source-packet.zip'
    members={}
    excluded={'.nes','.dbg','.lbl','.map','.exe','.dll','.mp4','.wav','.nesppuv1'}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for path,h in inputs.items():
            p=Path(path).resolve()
            assert sha(p)==h,p
            if not p.is_relative_to(R) or p.suffix in excluded:continue
            member=p.relative_to(R).as_posix()
            info=zipfile.ZipInfo(member,(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes());members[member]=h
    with zipfile.ZipFile(archive)as z:
        assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    proof=dict(status='Root-reviewed private source/native checkpoint; no shared installation',
               report=binding(REPORT),archive=binding(archive),verified_bindings=len(inputs),members=members,runtime_references=inputs)
    (DEST/'root-review.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(report=binding(REPORT),archive=binding(archive),members=len(members))))


if __name__=='__main__':main()
