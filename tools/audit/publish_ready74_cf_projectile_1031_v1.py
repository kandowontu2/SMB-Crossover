"""Freeze reviewed exact-hash CF contact runs and publish the narrow successor."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import zipfile

R=Path(__file__).resolve().parents[2]
J=R/'build/contra-force-projectile-contact-1031-v3/joint'
S=R/'docs/qa/checkpoints/2026-10-31/contra-force-projectile-contact-source-v1/handoff.json'
N=R/'build/contra-force-shooting-native-1031-v3'
P=R/'build/ready74-cf-projectile-peach-native-1031-v1/peach'
Q=R/'build/contra-force-score-queue-analysis-1031-v1/controls.json'
D=R/'docs/qa/checkpoints/2026-10-31/ready74-cf-projectile-native-v1'
OLD='a4410264ffccc7ce44e3b5ead1da639428cfa0594c94b2f63fa99fb4feab5b38'
NEW='f4767d595a25bf64355b1e2cea86be7a93046f1cf139a4d9b0544e35f9ed4182'
SOURCE='78ce571a5670df0d3cf97a20e3b5a27499497fd685eb81fda90eb66c0645d706'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))


def check(q):
    for p,h in q['bindings'].items():
        assert sha(p)==h,p


def save(p,q):
    assert not p.exists(),p
    p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert not D.exists() and sha(J/'candidate.nes')==NEW and sha(S)==SOURCE
    source=read(S);check(source)
    assert source['passed'] and source['candidate']==NEW and source['parent']==OLD
    assert source['source_ready74'] and source['menu_profiles']==86
    prepared=read(N/'prepared.json');check(prepared)
    assert prepared['source_candidate']==NEW and prepared['source_handoff_sha256']==SOURCE
    files={Path(__file__),N/'prepared.json',N/'source-observer-binding.json'}
    files.update(Path(p)for p in prepared['bindings']if Path(p).is_relative_to(R/'tools')and Path(p).suffix.lower()in['.py','.lua'])
    results=[]
    for name,folder in [(n,N/n)for n in ['burns','smith','iron','beans']]+[('Peach',P)]:
        ready=read(folder/'ready.json');binding=read(folder/'capture/binding.json');result=read(folder/'capture/result.json')
        check(ready);check(binding)
        assert binding['ready_sha256']==sha(folder/'ready.json')
        assert ready['ROM_sha256']==binding['ROM_sha256']==result['ROM_sha256']==NEW
        assert binding['exit_code']==0 and result['passed'],name
        assert result['timing']['nmi']==result['gameplay_frames']
        assert result['main_updates']==result['source_Main']
        if name=='Peach':
            assert ready['source_handoff_sha256']==SOURCE
            assert result['main_updates']==result['source_movement']==180
            assert result['jumped'] and result['landed'] and result['walked']>16
            assert result['body_P0_source_exact'] and result['vector_guards']==360
            assert all(result['actual_UI_DMA_checks'][x]>0 for x in ['selected','lives'])
            middle='entered.png'
        else:
            assert result['main_updates']==result['source_body_steps']==result['source_Main_returns']
            assert result['main_updates']>=200 and result['source_construct']==1
            assert result['maximum_worldX']>=369 and result['maximum_camera']>=257
            assert result['terrain_changed'] and result['actual_parser_calls']>0
            assert result['native_enemy_DMAS']>=4 and result['native_enemy_pixel_frames']>=4
            assert result['vector_guards']>=1200 and result['body_checks']>20
            assert result['native_defeats']==result['native_score_calls']==result['source_impact_calls']==result['source_impact_commits']==1
            assert result['earned']['original_impact_verified'] and result['earned']['post_kind']==6
            assert result['earned']['post_raw_A']==3 and result['earned']['post_raw_C']==2
            assert result['ground_projectile_observations']>0 and result['source_projectile_records']>0
            middle='earned-shot.png'
        pngs=sorted((folder/'capture').glob('*.png'))
        assert {p.name for p in pngs}=={'selected.png','lives.png',middle,'endpoint.png'}
        assert len([p for p in folder.rglob('*')if p.is_file()])<=64
        assert sum(p.stat().st_size for p in folder.rglob('*')if p.is_file())<512*1024*1024
        results.append(dict(identity=name,result=result,result_sha256=sha(folder/'capture/result.json'),root_reviewed_full_frame_PNGs={p.name:sha(p)for p in pngs}))
        files.update(p for p in folder.rglob('*')if p.is_file())
    score=read(Q);check(score)
    assert score['passed'] and score['native'] and score['ROM_sha256']==NEW
    assert not score['suspected_HUD_bug_reproduced'] and not score['product_change_required']
    files.add(Q)
    files.update(Path(p)for p in score['bindings'])
    files.add(R/'tools/audit/prepare_contra_force_score_queue_native_1031_v2.py')
    # Keep observer failures identifiable as failures. They did not change ROM.
    for folder in [R/'build/contra-force-shooting-native-1031-v1/burns',R/'build/contra-force-shooting-native-1031-v2/burns']:
        files.update(p for p in folder.rglob('*')if p.is_file())
    files.update([R/'build/contra-force-shooting-predicate-audit-1031-v2/diagnosis.json',R/'build/contra-force-projectile-impact-boundary-diagnostic-1031-v1/controls.json'])
    assert all(p.suffix.lower()in['.py','.json','.lua','.csv','.png','.log']for p in files)
    assert sum(p.stat().st_size for p in files)<16*1024*1024
    downloads=Path.home()/'Downloads'
    latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
    version=downloads/'SMB-Crossover-2026-10-31-Ready74-CF-Projectile-Contact-MMC5.nes'
    backup=downloads/'SMB-Crossover-Before-CF-Projectile-a4410264-MMC5.nes'
    temporary=downloads/'SMB-Crossover-Latest-WIP-MMC5.pending'
    assert sha(latest)==OLD and not any(p.exists()for p in[version,backup,temporary])
    D.mkdir(parents=True)
    archive=D/'native-results.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    limits=[
        'Exact-hash cold menu/lives and bounded opening movement; all four CF classes earn one ordinary pistol/native Goomba defeat, native score/SFX and original impact. No full1-1 or every-powerup claim.',
        'Original donor muzzle/art/radii are retained. Native SMB enemy body rectangles are an intentional host adaptation, not original Contra Force enemy geometry.',
        'Substantial lag remains. This contact correction does not claim constant60Hz or physical-console qualification.',
        'Only the CF contact source changed from a441. Existing menu polish, other character bugs, advanced moves/audio and pending identities remain incomplete.',
        'Campaign frontend/cache and private Thomas/Hogan source components are not included. Roster remains74 playable out of86 menu identities.',
    ]
    manifest=dict(passed=True,candidate=NEW,parent=OLD,source_handoff_sha256=SOURCE,
                  verified_source_bindings=len(source['bindings']),exact_candidate_native=results,
                  native_score_queue_diagnosis=score,limits=limits,
                  archive_sha256=sha(archive),archive_members=len(files),
                  files={p.relative_to(R).as_posix():sha(p)for p in sorted(files)})
    save(D/'manifest.json',manifest)
    (D/'README.md').write_text('# Ready74 Contra Force projectile contact\n\nExact f4767d59, four controller-earned pistol defeats, native score/SFX/source impact, camera and hardware graphics; Peach cold regression. All20 primary PNGs reviewed. No full-level, powerup,60Hz or hardware claim.\n\nThe suspected score HUD anomaly was a mistaken screenshot reading: actual PPU2062 shows100 one Main after internal credit. The passive diagnostic records and excludes its RAM3/ROM3 helper-hook coincidences. Earlier shooting observer failures remain failures in the archive.\n',encoding='utf-8')
    shutil.copyfile(latest,backup);assert sha(backup)==OLD
    shutil.copyfile(J/'candidate.nes',version);assert sha(version)==NEW
    shutil.copyfile(J/'candidate.nes',temporary);assert sha(temporary)==NEW
    os.replace(temporary,latest);assert sha(latest)==NEW
    receipt=dict(date='2026-10-31',passed=True,installed=True,status='INSTALLED_READY74_CF_PROJECTILE_CONTACT_WIP',
                 ROM_sha256=NEW,previous_sha256=OLD,latest=str(latest),versioned=str(version),backup=str(backup),
                 playable=74,individual_identities=86,pending_individual_identities=12,menu_slots=32,menu_rows=4,
                 source_handoff_sha256=SOURCE,native_manifest_sha256=sha(D/'manifest.json'),limits=limits,
                 all_characters_1_1_and_every_powerup_complete=False,goal_complete=False)
    save(R/'docs/qa/functional-roster-ready74-cf-projectile-2026-10-31.json',receipt)
    print(json.dumps(dict(installed=str(latest),sha256=sha(latest),native_archive_bytes=archive.stat().st_size,primary_native_cases=len(results),playable=74,goal_complete=False)))


if __name__=='__main__':
    main()
