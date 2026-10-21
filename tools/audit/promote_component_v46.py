"""Accept the bounded Samus optimization after compiled/native/crowd controls."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'build/checkpoints/roster-audit-v45'
SRC=ROOT/'build/checkpoints/roster-audit-v46-provisional-a'
DST=ROOT/'build/checkpoints/roster-audit-v46'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert not DST.exists(),'Never replace an accepted checkpoint'
candidate=read(SRC/'candidate.json')
roms={m:sha(SRC/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
assert roms=={m:q['sha256']for m,q in candidate['roms'].items()}
assert roms['mmc3']==sha(OLD/'smb-crossover-mmc3.nes')
assert candidate['roms']['mmc5']['samus_free']==15
proofs={}

def retain(name,relative):
    p=ROOT/relative;proofs[name]=dict(path=relative,sha256=sha(p));return read(p)

checked=set()
def verify_records(value):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str)and isinstance(value.get('sha256'),str):
            p=Path(value['path']);p=p if p.is_absolute()else ROOT/p
            assert p.is_file()and sha(p)==value['sha256'],p
            if 'bytes'in value:assert p.stat().st_size==value['bytes']
            checked.add(str(p))
        for item in value.values():verify_records(item)
    elif isinstance(value,list):
        for item in value:verify_records(item)

summary=retain('full_suite','build/verification/summary-roster-audit-v46-provisional-a.json')
bound=retain('bound_suite','build/checkpoints/roster-audit-v46-provisional-a/validation/bound-summary.json')
assert summary['result']==bound['result']=='passed'and len(summary['cases'])==bound['case_count']==bound['passed']==761
assert bound['failed']==0 and bound['single_full_run']and not summary['failures']and not summary['changed_fixtures']
assert summary['fixture_hashes_before']==summary['fixture_hashes_after']
assert all(sha(ROOT/n)==h for n,h in summary['fixture_hashes_after'].items())
assert summary['roms']==bound['roms']==roms
assert bound['summary_sha256']==proofs['full_suite']['sha256']
assert all(sha(ROOT/q['log'])==q['log_sha256']for q in bound['cases'])
cpu=retain('compiled_cpu','build/verification/samus-idle45-component/cpu45-46-m5-a.json')
assert cpu['result']=='passed'and cpu['cases']==8508
assert cpu['stats']['empty-independent-oracle']['cases']==8448
assert cpu['stats']['live-or-guard-bypass']['cases']==60
verify_records(cpu)
native=retain('native_suites','build/verification/component46-native-v2-root-a/report.json')
assert native['result']=='all-native-suites-and-comparisons-passed'and len(native['runs'])==6
for mapper in('mmc3','mmc5'):
    paired=retain('native_'+mapper,f'build/verification/component46-native-v2-root-a/comparison-{mapper}.json')
    assert paired['result']=='passed'and paired['cases']==138 and paired['all_character_ids']==list(range(13))and paired['Lance']
    verify_records(paired)
    for row in paired['rows']:
        component=read(Path(row['report']['path']))
        assert row['checker_exit']==0 and component['result']=='passed'and not component['failures']
        verify_records(component)
    for side in('control45','candidate46'):
        suite=retain(f'{side}_{mapper}',f'build/verification/samus-idle45-native-v2/suite-{side}-{mapper}-root-a.json')
        assert suite['result']=='passed-native'and len(suite['runs'])==11
        verify_records(suite)
        for row in suite['runs']:
            result=read(Path(row['native_result']['path']));assert result['native_exit']==0;verify_records(result)
retain('initial_native_negative','build/verification/samus-idle45-component/bindings/control45-m5-run-a/native-result.json')
assert read(ROOT/proofs['initial_native_negative']['path'])['native_exit']==1
classification=retain('negative_classification','build/verification/samus-idle45-native-v2/v1-negative-classification.json')
retain('native_v2_freeze','build/verification/samus-idle45-native-v2/freeze.json')
verify_records(read(ROOT/proofs['native_v2_freeze']['path']))
crowds=retain('crowds','build/verification/plain-walking-v45-v46a-samus-three-b-comparison.json')
assert crowds['canonical_mismatch_count']==0 and len(crowds['runs'])==3
for q in crowds['runs']:
    assert q['canonical_rows']==1200 and q['canonical_observation_fields']==204 and q['mapper']=='mmc5'
    for scene in q['scenes']:
        assert all(scene[k]['before']==scene[k]['after']for k in('physicalFrames','drawAllCalls','physicalDmas','visibleEnemyFrames'))
retain('unsupported_pit_baseline','build/verification/component46-pit-crowd-baseline-classification.json')
archive=SRC/'source-v46a.zip'
rebuild=retain('fresh_rebuild','build/checkpoint-tests/source-v46a-rebuild-smoke/report.json')
assert rebuild['archive_sha256']==sha(archive)and rebuild['source_files']==401
assert len(rebuild['cases'])==2 and all(q['exit']==0 and q['equal']and q['sha256']==roms[q['mapper']]for q in rebuild['cases'])
with zipfile.ZipFile(archive)as z:
    sources=json.loads(z.read('archived-file-hashes.json'))
    assert len(sources)==401 and len(z.namelist())==402
    assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in sources.items())
assert all(sha(ROOT/n)==h for n,h in sources.items())
with zipfile.ZipFile(OLD/'source-v45.zip')as z:previous=json.loads(z.read('archived-file-hashes.json'))
assert {n for n in sources if sources[n]!=previous[n]}=={'README.md','src/samus_weapons.s'}
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import workspace_bytes
used=workspace_bytes(ROOT)
assert used+sum(p.stat().st_size for p in SRC.rglob('*')if p.is_file())+64*1024*1024<30_000_000_000
shutil.copytree(SRC,DST)
shutil.copyfile(archive,DST/'source-v46.zip')
qa=ROOT/'docs/qa/roster-component-v46.md'
assert not qa.exists()
qa.write_text('''# Samus idle weapon work on MMC5

Accepted46 saves142 CPU cycles per ordinary idle Samus update in all20 matched
standing/walking scenes. SamusWeapons changes242→100 cycles and its inclusive
ProcFireball_Bubble caller1052→910. All3,600 paired updates across Samus, Mega Man
and Bass retain all204 recorded gameplay fields. Draw counts, physical frames,
DMA counts and measured enemy visibility are unchanged. The six-Goomba walking
scene still draws30/60 frames: this is a CPU saving, not a visible lag cure.

The27-byte shortcut applies only on MMC5 with an active engine, all three beam
and all three bomb slots empty, and current B released. It preserves initial
sprite cleanup, firing-pose countdown, shared bridge cleanup and return ABI.
It leaves body contacts, inventory drops, remaining weapons, freeze/Screw Attack
and swimming bubbles live. Held B retains the old path and costs one extra
branch cycle. MMC5 SAMUS has15 free bytes; MMC3's entire ROM remains identical45.
Header and CHR bytes are unchanged.

All761 existing emulator checks pass in one unchanged-fixture run, with every
raw log frozen and ROM-bound. The actual compiled CPU proof passes8,508 cases:
8,448 independent idle/flag cases and60 live/guard cases, including all10,240
gameplay RAM bytes and ordered hardware writes. Only actual discarded push
cells and label-proven farcall operand relocations are normalized there.

Each mapper passes138 matched native caller cases, including IDs0..12 and Lance,
live beams/bombs, B/Select, drops, freeze/Screw, pause and swimming bubbles.
Native checks compare return/entry ABI and the explicit effect/scratch projection;
the complete10,240-byte snapshots are also retained. Fresh extraction of401
source files rebuilds both ROMs byte identically.

The first native fixture fails on accepted45 because forced life-loss engine
and Y-high2 arenas contaminate later lifecycle updates. Its original source,
failure and raw snapshots remain intact. V2 preserves all138 case contents:
128 safe cases share a process, while ten hazardous cases each cold boot and
stop at the actual caller return. Bounds/assertions remain unchanged. An attempted
all-character crowd expansion also fails its old45 no-injury precondition for
Pit; it is retained separately and contributes no paired performance claim.

Outlines remain OFF by default, and their option row stays gold. Samus has no
ordinary stomp in the2.02 source; upgraded Screw Attack supplies contact damage.
Dense-scene lag/flicker, remaining source/weapon differences, all14 complete
final-hash routes and all-character final audiovisual review remain open.

Evidence is bound in build/checkpoints/roster-audit-v46/manifest.json. The broader
goal remains active; this component does not certify source-perfect behavior.
''',encoding='utf8')
readme=ROOT/'README.md';text=readme.read_text();anchor='The [v45 component update]'
at=text.index(anchor)
paragraph=('The [v46 component update](docs/qa/roster-component-v46.md) skips empty Samus beam/bomb loops on MMC5, saving142 CPU cycles per idle update. All761 unchanged-fixture regression slots,8,508 compiled CPU cases,138 native caller cases per mapper and fresh401-file archive rebuilds pass. The paired3,600-update crowd check retains all204 gameplay fields, but redraw/visibility counts do not improve. MMC3 stays byte identical45. Outlines remain off by default with a gold option row. ROMs are in `build/checkpoints/roster-audit-v46/`; dense-scene lag and the full roster/weapon/recording audit remain open.\n\n')
readme.write_text(text[:at]+paragraph+text[at:],encoding='utf8')
manifest=dict(status='accepted-bounded-component',goal_complete=False,parent=OLD.name,
    accepted_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),roms=roms,
    candidate_sha256=sha(SRC/'candidate.json'),source_archive_sha256=sha(archive),source_count=401,
    scope=candidate['scope'],proofs=proofs,verified_file_records=len(checked),qa=qa.relative_to(ROOT).as_posix(),
    qa_sha256=sha(qa),README_postarchive=dict(archived_sha256=sources['README.md'],current_sha256=sha(readme),reason='Post-validation release ledger only'),
    measured_idle_cycles_saved=142,redraw_improvement=False,
    limits=['Dense scenes still lag and hardware scanline flicker remains.',
            'The paired crowd claim covers20 scenes for Samus/Mega Man/Bass only; broader Pit arena precondition failed on45.',
            'All14 final-hash routes, every weapon/upgrade and all-character final recordings/frame/audio review remain incomplete.'],
    workspace_bytes_before=used,workspace_cap_bytes=30_000_000_000)
(DST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('ACCEPTED46',roms,'761 full-suite,8508 CPU,138 native/map; goal remains active',flush=True)
