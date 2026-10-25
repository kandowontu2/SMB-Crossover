"""Admit the current measured Water optimization without closing the roster goal."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,statistics,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'water-visible-final-cw';CP=R/'build/checkpoints/water-visible-cw'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    assert not O.exists()and not CP.exists();O.mkdir();CP.mkdir()
    roms={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
    receipts={name:V/path for name,path in{
        'water_native':'water-visible-current-ck/summary.json','cheats_native':'cheats-current-cl/summary.json',
        'retained_fix_regressions':'water-current-regressions-cv/summary.json','populated_profile':'water-visible-profile-cm/summary.json',
        'dense_profile':'water-current-dense-ct/summary.json','geometry':'water-current-geometry-co/compiled-i.json',
        'caller_liveness':'water-current-suffix-cr/summary.json','dense_caller_liveness':'water-current-dense-caller-cu/summary.json',
        'layout':'water-current-layout-cs/layout.json','bridge':'water-current-layout-cs/bridge-w.json'}.items()}
    data={n:read(p)for n,p in receipts.items()}
    checks=[]
    for name,key in(('water_native','results'),('cheats_native','checks'),('retained_fix_regressions','results')):
        d=data[name];assert d['passed']
        for z in d[key]:
            assert z['passed']and z.get('ROM_sha256',z.get('rom_sha256'))==roms[z['mapper']]
            checks.append(z)
    assert len(checks)==42
    assert data['populated_profile']['passed']and data['dense_profile']['passed']and data['layout']['passed']
    for key in('geometry','caller_liveness','dense_caller_liveness','bridge'):assert data[key]['status'].startswith('PASS')
    assert all(g['cases']==42760 for g in data['geometry']['groups'])
    assert all(g['Bridge_cases']==1040 and g['consumer_cases']==2080 for g in data['bridge']['groups'])
    caller_groups=data['caller_liveness']['groups']+data['dense_caller_liveness']['groups']
    calls=sum(len(g['calls'])for g in caller_groups);interrupts=sum(c['actual_interrupts']for g in caller_groups for c in g['calls'])
    assert(calls,interrupts)==(213,42)
    profile=[]
    for mapper in roms:
        for character in(1,9):
            before,after=[next(g for g in data['populated_profile']['groups']if g['revision']==rev and g['mapper']==mapper and g['character']==character)for rev in('CI','CJ')]
            key='SpecialWeapons/expand/populated/full8';a,b=before['scopes'][key],after['scopes'][key]
            profile.append(dict(mapper=mapper,character=character,ability_before=a,ability_after=b,reduction_percent=100*(a['mean']-b['mean'])/a['mean'],
                GameLoop_before=before['scopes']['GameLoop/expand/populated/full8'],GameLoop_after=after['scopes']['GameLoop/expand/populated/full8']))
    report=dict(passed=True,ROMs=roms,native_checks=checks,receipts={n:dict(path=p.relative_to(R).as_posix(),sha256=sha(p))for n,p in receipts.items()},
        native_full_caller_replays=calls,attained_interrupts=interrupts,geometry_cases_per_mapper=42760,populated_comparison=profile,
        retained_negatives=['water-current-caller-cn: previous privateJ oracle assumed publicY/scratch equality; CI lacks its offscreen gate, so that assumption is false. Actual subsequent reads are checked in CR/CU.',
            'water-current-suffix-cp: strict suffix-write bytes differ at relocated draw return pushes and standard farcall operand.',
            'water-current-suffix-cq: additionally required symbolic binding for relocated Bass helpers. CR binds every actual changed write, with no discarded stack/SMC range.'],
        limitations=['Populated run grants equipment and source mode with journaled writes. Dense run additionally authors all six enemies/eight projectiles. Neither is an ordinary route or acquisition recording.',
            'Populated MMC3 Mega Man GameLoop maximum rises33420->36363 cycles. Frame populations/interrupt phase differ; this is retained, not hidden by averages.',
            'Dense fullGameLoop mean falls45050->44496 MMC3 and42454->41771 MMC5, but total skip counts remain46/45. Water Shield lag is not solved.',
            '213 native caller replays cover attained interrupts, not universal interrupt phases. No new public ABI preserving privateY or dead proxy scratch is claimed.'],goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    names=[f'build/smb-crossover-{m}.{ext}'for m in roms for ext in('nes','dbg','lbl','map')]
    names+=['smb1base.cfg','src/special_weapons.s','src/entrypoint.s','src/water_shield_enemies.s',
        'tools/audit/merge_visible_water_cj.py','tools/audit/profile_visible_water_cm.py','tools/audit/check_water_current_cn.py',
        'tools/audit/check_water_suffix_cp.py','tools/audit/review_water_layout_cs.py','tools/audit/profile_water_dense_ct.py','tools/audit/check_water_regressions_cv.py']
    for name in names:
        path=CP/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,path)
    manifest=dict(status='VISIBLE_WATER_CONSUMER_OPTIMIZATION_ADMITTED_FULL_ROSTER_GOAL_ACTIVE',ROMs=roms,
        parent_checkpoint='build/checkpoints/firebar-budget-ci/manifest.json',parent_checkpoint_sha256=sha(R/'build/checkpoints/firebar-budget-ci/manifest.json'),
        hashes={n:sha(CP/n)for n in names},source_hashes={p.relative_to(R).as_posix():sha(p)for p in(R/'src').rglob('*')if p.is_file()},
        verification_summary_sha256=sha(O/'summary.json'),new_RAM_bytes=0,helper_range='bank24:A:B600-B6CF',SpecialMM_growth_bytes=10,goal_complete=False)
    (CP/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    doc=R/'docs/qa/water-visible-optimization-2026-10-22.md'
    doc.write_text('''# Water Shield collision work

The current Mega Man/Bass shield uses a direct Water50 enemy consumer. It keeps the original inclusive/wrapping collision core and native DamageEnemy routine. Every ball reads live enemy state, visibility, position and health; earlier balls can change the later balls' targets. No geometry snapshot or replacement physics is introduced. The broad candidate scan omits offscreen enemies that the original consumer already rejects.

The additive merge preserves the installed terrain publication, score anchors, Cheats, cannon cooldown, firebar allocation and Claude Sophia head-origin changes. The helper occupies208 bytes at bank24 A:B600-B6CF, adds no RAM, and leaves the shared Ryu and score reservations intact. Existing SPECIAL_MM grows10 bytes and its external callers are bound to the same symbolic routines. Header, CHR and rebuilt baselines are unchanged.

## Current evidence

Both mapper builds pass42 scoped native tests:18 Water behavior/drawing/armor checks,4 Cheats checks and20 audio/weapon/retained-fix regressions. The unchanged geometry oracle executes42760 cases per mapper over flags, all enemy IDs, state boundaries, offscreen classes, inclusive/wrapped edges, armor, health and multiple contacts. The private Bridge/both-consumer oracle checks1040 Bridge cases and2080 consumer calls per mapper.

An independent current-ROM replay executes213 captured full weapon calls with all42 attained interrupt boundaries, exact registers, every10240 RAM bytes, hardware-read order, mapper restoration and ordered writes. A separate matched-input no-interrupt comparison continues the actual parent suffix to GameLoop's publication. It proves every differing input RAM cell is replaced before any read there and changedY is overwritten before use. Actual moved return pushes and standard farcall operands are individually decoded and symbolically bound; no stack/SMC range is discarded. This is bounded attained coverage, not a universal interrupt-phase claim.

Earlier CN/CP/CQ comparisons and their failures remain. CN inherited a privateJ output-equality assumption that does not apply to CI's older unfiltered candidate scan. CI's rejected offscreen consumers leave different deadY/proxy scratch. CP then required literal suffix write equality despite relocated draw pushes; CQ exposed an additional relocated Bass target. The final CR/CU checks preserve complete native equality and explicitly prove subsequent use of changed inputs, while binding each changed suffix write to its actual producer.

## Measured cost

In the populated1-1 diagnostic, actual inputs summon eight balls, approach native enemies and expand the shield. Equipment and Hard mode are authored and journaled; player positions, enemies and terrain are ordinary native world state. These runs are not natural-acquisition or playthrough evidence. Exclusive timings subtract attained IRQ/NMI time; nested scopes are not additive.

| Expansion near visible enemies | Previous ability cycles, mean | Current | Reduction |
| --- | ---: | ---: | ---: |
| Mega Man MMC3 |11750|10636|9.5%|
| Bass MMC3 |11735|10600|9.7%|
| Mega Man MMC5 |11587|10463|9.7%|
| Bass MMC5 |11601|10466|9.8%|

Full GameLoop means also fall in these four bins, but the MMC3 Mega Man maximum rises33420 to36363 cycles. Native interrupt phase, route pacing and sample populations differ across builds. The raw maximum is retained and prevents a universal frame-time claim.

In a separately authored six-enemy/eight-ball stress arena, complete GameLoop mean falls45050 to44496 cycles on MMC3 and42454 to41771 on MMC5. Worst cases also fall in that arena. The total lag increments remain46 on MMC3 and45 on MMC5. This is a CPU saving; visible Water Shield lag still needs further work.

Checkpoint: `build/checkpoints/water-visible-cw/manifest.json`. Aggregate receipt: `build/verification/water-visible-final-cw/summary.json`. All source captures, raw profiles, controller journals and negative checks are retained. The original full-roster through2-2, every ability/upgrade, remaining footage defects and final recordings goal is still active under the user-authorized100GB retention cap.
''',encoding='utf-8')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(R);assert used<100_000_000_000
    handoff=dict(status='WATER_VISIBLE_CONSUMER_ADMITTED_FULL_GOAL_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),
        previous_progress_sha256=sha(V/'root-current49-progress-ci.json'),checkpoint=(CP/'manifest.json').relative_to(R).as_posix(),checkpoint_sha256=sha(CP/'manifest.json'),
        ROMs=roms,report=doc.relative_to(R).as_posix(),verification=(O/'summary.json').relative_to(R).as_posix(),workspace_bytes=used,workspace_cap=100_000_000_000,
        all_lossless_and_negatives_retained=True,root_native_handles=[],goal_status='active',goal_complete=False,
        previous_turn_classification='progress: Cheats current-build menu and invincibility verified on both mappers, receipt CL and docs updated',
        current_turn_classification='progress: current Water optimization profiled,85,520 geometry cases,213 exact native caller replays plus parent liveness,42 scoped native tests, checkpoint admitted',
        next=['Continue Water/HUD lag reduction; dense fullGameLoop still skips46/45 frames. Pending HUD source-p consumer-busy fix is not implemented. Do not copy whole private sources over current fixes; HUD pending SRAM must move from7FFB to7FFD or later.',
            'Remaining private Land/Arm/Rush/audio/Ryu fixes are not merged. Bank24 Water B600-B6FF, Ryu B700-BFBF, Score BFC0-BFFF. SPECIAL_MM nowBFF6 MMC3; SAMUS MMC5 fullBFFF; renderer MMC3 BFFC.',
            'Retiming and ordinary no-cheat routes through2-2 still required for all14 final recordings. Existing films are old build identities, not this checkpoint. Bass bounced underground brick palette, Rygar/Lance late HUD split and other footage candidates remain.',
            'Natural Hard Bill showcases: AY0/1 Flare, AY2/BC3..5 Laser; BF6/8/10 fail pickup by3400. Inspect actual pickup trajectories before further wait sweeps. Hard A/V clips, other powerups and Easy/Hard landing comparison remain absent.',
            'Cheats submenu is complete; do not spend another turn reimplementing it. Later-castle traversal remains unverified; generic BU/BV/CH initial ceiling/pit failures are retained. All captures and negatives retained under user-raised100GB cap.'])
    (V/'root-current49-progress-cw.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(checkpoint=str(CP),ROMs=roms,native_checks=len(checks),workspace_bytes=used,goal_complete=False),indent=2))

if __name__=='__main__':main()
