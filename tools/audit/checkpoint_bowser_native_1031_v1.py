"""Retain the bounded native milestone and the defects blocking adoption."""
from pathlib import Path
import json
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_functional_roster_visuals58_v1 as B

O=R/'build/bowser-native-1031-v2'
H=R/'build/bowser-current64-v3/handoff.json'
D=R/'docs/qa/checkpoints/2026-10-31/bowser-bounded-native'


def main():
    assert not D.exists()
    h=json.loads(B.read(H));B.bound(h)
    assert h['candidate']=='95295fa6b15518b3813cad8609d833755bb92ba1e7eff3e39a60c9003f9f1ce1'
    outcomes=[];files={Path(__file__),O/'prepared.json'}
    for name,variant in [('smb3',0),('smb1',8)]:
        p=O/name;r=json.loads(B.read(p/'capture/result.json'))
        bound=json.loads(B.read(p/'capture/binding.json'));B.bound(bound)
        assert r['passed'] and bound['exit_code']==0 and r['ROM_sha256']==h['candidate']
        assert bound['ROM_sha256']==h['candidate'] and r['variant']==variant
        assert r['main_updates']==r['source_Main']==r['source_movement']==r['source_EndFrame']==148
        assert r['vector_guards']==444 and r['source_fire_calls']>=1
        assert r['jumped'] and r['landed'] and r['body_P0_source_exact']
        pngs=sorted((p/'capture').glob('*.png'));assert len(pngs)==5
        files.update(q for q in p.rglob('*')if q.is_file())
        outcomes.append(dict(identity=name,variant=variant,passed_scoped_smoke=True,
            physical_gameplay_frames=r['gameplay_frames'],complete_Main_updates=148,
            vector_restores=444,jump_rise=r['rise'],HP=r['HP'],
            source_fire_calls=r['source_fire_calls'],timing=r['timing'],
            root_reviewed_PNGs={q.name:B.sha(q)for q in pngs},
            result_sha256=B.sha(p/'capture/result.json')))
    negative=R/'build/bowser-native-1031-v1'
    files.add(negative/'fixture-negative.json')
    files.update(q for q in (negative/'smb3').rglob('*')if q.is_file())
    files.update(R/f'tools/audit/prepare_bowser_native_1031_v{i}.py'for i in [1,2])
    files.update(R/f'tools/reference/bowser_native_ui_1031_v{i}.lua'for i in [1,2])
    assert all(p.suffix.lower()in ['.py','.lua','.json','.csv','.log','.png']for p in files)
    assert sum(p.stat().st_size for p in files)<16*1024*1024
    D.mkdir(parents=True)
    archive=D/'native-results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    d=dict(status='BOUNDED_NATIVE_MILESTONE_KNOWN_ADOPTION_BLOCKERS',
        candidate=h['candidate'],native=True,admitted=False,installed=False,
        installed_ROM_unchanged='f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78',
        installed_playable=64,source_handoff_sha256=B.sha(H),verified_source_bindings=len(h['bindings']),
        native_runs=outcomes,full1_1=False,every_powerup=False,constant60Hz=False,
        blocking_findings=[
            'Longer genuine contact traversal finds service6 returning tier0, which routes directly to KillPlayer before own HP injury.',
            'Source1 jump rises37px; actual tall-pipe progression needs verification/adaptation.',
            'Both lives portraits overlap WORLD1-1 text; source3 is most visible.',
            'Both smokes complete148 Main updates in222 physical gameplay frames; lag remains.'
        ],
        fixture_correction='Menu source descriptor is emitted on redraw, while native DMA repeats cached OAM. Identity/variant binding and complete actual pixel checks replace the invalid2-frame age assumption. Recorded selected descriptor ages32..48 validate the diagnosis; failure retained.',
        archive_sha256=B.sha(archive),archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix():B.sha(p)for p in sorted(files)})
    B.write(D/'manifest.json',json.dumps(d,indent=2)+'\n')
    B.write(D/'README.md',
        'Root-run, controller-only native smokes for both Bowser forms on95295fa6. Each passes '
        'menu/lives original-pixel/palette/physical-CHR checks,148 complete Main updates, jump/landing, '
        'source breath and444 actual ISR restores. Root reviewed all10 full-frame PNGs. The first '
        'fixture falsely required a fresh descriptor every2 frames even though the menu caches OAM; '
        'that failure is retained. The successor keeps identity, complete-part DMA and exact pixel '
        'assertions and records the actual descriptor age. No ROM/debug-RAM writes or video captures.\n\n'
        'NOT ADMITTED OR INSTALLED. Longer source traversal finds the real service6 tier0→KillPlayer '
        'bug before own HP injury. Source1 jump/pipe progression and lives portrait text overlap also '
        'need repair. Measured148 Main updates in222 video frames is not60Hz. Downloads remains the '
        'corrected64-identity Peach build. No full1-1/every-powerup or campaign qualification.\n')
    print(json.dumps(dict(checkpoint=str(D),members=len(files),archive_bytes=archive.stat().st_size,
        manifest_sha256=B.sha(D/'manifest.json'),admitted=False,installed=False)))


if __name__=='__main__':main()
