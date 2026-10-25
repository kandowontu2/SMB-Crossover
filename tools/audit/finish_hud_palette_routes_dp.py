"""Preserve current scoped findings and controller progress, without adoption."""
from pathlib import Path
from datetime import datetime,timezone
import collections,csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'hud-palette-route-review-dp'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    assert not O.exists();O.mkdir()
    cp=read(R/'build/checkpoints/water-visible-cw/manifest.json')
    assert all(sha(R/n)==value for n,value in cp['source_hashes'].items())
    assert all(sha(R/'build'/f'smb-crossover-{m}.nes')==value for m,value in cp['ROMs'].items())
    paths={n:V/p for n,p in{
        'private_build':'hud-current-cy/build.json','native_busy_consumer':'hud-pending-native-db/summary.json',
        'foreign_order':'hud-foreign-overlap-dd/summary.json','palette':'palette-sharing-de/summary.json',
        'current_Rygar_fixed_replay':'rygar-enemy-replay-dn/summary.json'}.items()}
    d={n:read(p)for n,p in paths.items()}
    assert d['native_busy_consumer']['passed']
    assert d['foreign_order']['status']=='CONFIRMED_PRIVATE_DEFERRED_HUD_FOREIGN_ORDER_DEFECT_NOT_ADOPTED'
    assert all(sum(not z['equal']for z in g['cases'])==5 for g in d['foreign_order']['groups'])
    assert d['palette']['status']=='CONFIRMED_CURRENT_SHARED_PALETTE_CONFLICT_NOT_REPAIRED'
    assert d['current_Rygar_fixed_replay']['frames']==8785
    source=R/'build/roster-through-2-2/root-rygar-retime-dh-7-v0-mmc3'
    bounded=R/'build/roster-through-2-2/root-rygar-prefix-proof-dk-7-v0-mmc3'
    assert (bounded/'trace.csv').read_bytes()==b''.join((source/'trace.csv').read_bytes().splitlines(keepends=True)[:4101])
    assert (bounded/'inputs.csv').read_bytes()==b''.join((source/'inputs.csv').read_bytes().splitlines(keepends=True)[:4100])
    assert read(bounded/'result.json')['failure']=='frame limit'
    replay=R/'build/roster-through-2-2/root-rygar-enemy-proof-dn-7-v0-mmc3'
    splits=list(csv.DictReader((replay/'scroll-writes.csv').open(newline='')))
    active=[z for z in splits if z['mode']=='1'and z['task']=='3'and z['engine']=='8'and z['screenDisabled']=='0'and z['address']=='8197'and 28<=int(z['scanline'])<80]
    lines=collections.Counter(int(z['scanline'])for z in active)
    assert lines=={31:12308}
    attempts=[]
    for tag in('dg','dh','di','dj','dl','dm','do'):
        packet=R/'build/roster-through-2-2'/f'root-rygar-retime-{tag}-7-v0-mmc3'
        attempts.append(dict(tag=tag,manifest_sha256=sha(packet/'manifest.json'),result=read(packet/'manifest.json').get('result'),
            terminal_trace=list(csv.DictReader((packet/'trace.csv').open(newline='')))[-1]))
    report=dict(status='PRIVATE_HUD_REVIEW_AND_VERIFIED_CURRENT_RYGAR_FIRST_TWO_LEVELS_GOAL_ACTIVE',main_ROMs=cp['ROMs'],main_source_unchanged=True,
        receipts={n:dict(path=p.relative_to(R).as_posix(),sha256=sha(p))for n,p in paths.items()},
        current_native_HUD_split=dict(ordinary_Rygar_replay_frames=8785,PPUSCROLL_writes_by_visible_scanline=dict(lines),late_writes=0,
            scope='This current route has no late physical HUD scroll write. It does not reproduce or close the old film glitch, certify all scenes, or provide RGB/audio recordings.'),
        attempts=attempts,private_HUD_adopted=False,world_palette_repaired=False,verified_through_2_2=False,goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    doc=R/'docs/qa/hud-palette-route-review-2026-10-22.md'
    doc.write_text('''# Current HUD, palette and Rygar route review

The playable ROM remains the admitted Water CW checkpoint. This review does not install the private HUD candidate or claim the shared palette issue fixed.

## Private HUD successor

The earlier deferred HUD producer was rebased additively onto current CW, preserving Cheats, Sophia head origins, terrain publication, score anchors, cannon cooldown, Water and firebar admission. The pending byte moves to7FFD, after the two Cheats bytes. Its native block-update consumer now treats pending numeric work as busy. Both mapper builds and both literal baselines build successfully.

The original bank5 reservation now contains the installed103-byte Sophia helper. The first CX build therefore overflowed103 bytes and is retained. Private CY relocates the379-byte HUD flush to bank24 BA00-BB7A. Its private partition reserves B700-B9FF for the frozen725-byte Ryu leaf, BA00-BBFF for HUD, BC00-BFBF for additional Ryu code and BFC0-BFFF for scores. This is private only; the main linker/partition is unchanged.

Native consumer tests on both mappers cover126 pending/header combinations and the disabled-pending control. Pending work preserves both replacement flags; without it, the first native slot writes its packet and the second correctly waits on the now-busy queue. The earlier test incorrectly expected both slots to write; that failed DA result is retained. The CZ path-binding failure is retained too. CW's pending-state negative is a counterfactual control, not an installed-CW bug, because CW has no deferred producer.

A second compiled comparison found a real remaining ordering defect in the private algorithm. It executes current native numeric production and the candidate, with foreign writes before or after the same request. There are14 cases per mapper. All before-numeric and unrelated-write controls match. Five after-numeric cases differ on each mapper: partial score, full score, vertical score, mirrored-name-table score and partial coin writes. The candidate appends numeric packets after those later writes, or removes a foreign full-score packet as if it were its own. The busy guard alone cannot make that correct. The original DC harness used the wrong player request nibble; corrected DD uses the actual P1 request02 and retains DC.

The candidate remains uninstalled. The next design must preserve a numeric request's queue position, distinguish its own packets from foreign packets and coalesce only requests superseded by later requests. Full-size marked placeholders filled in place before publication are a candidate design, not a verified implementation. Marker ownership, queue capacity, consumers, direct-call outputs and attained interrupts still need proof.

## Bass's underground brick colors

Current compiled DrawBlock assigns ordinary bouncing bricks sprite palette3. Current guest face setup writes0F/37/17 into that same palette in1-2, replacing native underground0C/3C/1C. This directly explains the brown/orange effect in the retained1:38 film. Debris also selects palette3.

The actual mapped Bass CHR records show28 base-pose palette3 parts with color2 skin pixels and two hurt parts with all three colors; his special poses also use colored palette3 parts. Disabling pure-black outlines does not free those colored parts. Restoring the native palette globally would recolor faces and specials. No such shortcut is installed. Coordinated palette assignment/art packing must preserve both player colors and world effects, then measure any added OAM pressure. This is current code/CHR evidence, not a newly recorded ordinary encounter.

## Current ordinary Rygar route

An old1-2-only guide was initially started without its1-1 prefix and failed immediately. A full retained-movie guide now supplies only ordinary buttons from current telemetry. Actual enemy reactions, fresh B presses at the observed ceiling wall and two separate jumps onto/across the1-2 pipe let the current CW run clear1-1 and1-2. All attempts, including deaths and the overly broad brick-response attempt, are retained.

DM reaches1-2 at frame4027 and1-3 at7574, then dies at8785. DN independently replays the complete8785 controller/trace rows byte for byte, including cycle counts, with full read-only OAM/CHR/audio/scroll capture. Its expected native exit is1 for that1-3 death; it is not a through2-2 success. The shorter4100-frame DK replay independently confirms the first-level prefix and stops at its explicit limit. Neither replay grants powers, positions, ammo, enemies or terrain.

The current DN route has12308 active visible PPUSCROLL writes, all on scanline31, with no late split in the bounded window. This does not certify every frame's appearance or sound and does not close the old movie's late split. No new final A/V recording is delivered by these controller proofs.

The injury observer identifies DM's1-3 collision as a red Koopa, slot1, at1713/88. The landing response DO gets beyond that encounter but later dies over the next tree gap at1875/245. Do not infer a ROM physics bug or blindly extend the enemy-ID filter; the next route work needs actual platform/landing geometry. The complete through2-2 route, every ability/upgrade, other characters and final recordings remain unfinished.

Evidence aggregate: `build/verification/hud-palette-route-review-dp/summary.json`. All captures and negatives are retained under the user-raised100GB cap.
''',encoding='utf-8')
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(R);assert used<100_000_000_000
    handoff=dict(status=report['status'],utc=datetime.now(timezone.utc).isoformat(),previous_progress_sha256=sha(V/'root-current49-progress-cw.json'),
        checkpoint='build/checkpoints/water-visible-cw/manifest.json',checkpoint_sha256=sha(R/'build/checkpoints/water-visible-cw/manifest.json'),ROMs=cp['ROMs'],
        report=doc.relative_to(R).as_posix(),verification=(O/'summary.json').relative_to(R).as_posix(),workspace_bytes=used,workspace_cap=100_000_000_000,
        all_lossless_and_negatives_retained=True,root_native_handles=[],goal_status='active',goal_complete=False,
        previous_turn_classification='progress: Water consumer admitted after current performance and exact native/compiled checks',
        current_turn_classification='progress: current private HUD rebase and busy guard built/verified, separate valid foreign-order defect proven, current Bass palette conflict bound, current Rygar1-1/1-2 independently replayed',
        next=['Main remains CW; do not adopt CY. A busy-guard-only HUD fix still fails foreign ordering. Implement/verify queue-position-preserving numeric placeholders or an equally complete ordering algorithm. Partial horizontal/vertical/mirrored/full foreign writes must all retain native last-writer order. DD has concrete counterexamples and positive controls.',
            'CY is current-source additive and preserves all installed fixes. Source in hud-current-cy/source, pending7FFD. Private bank24 partition differs from main: HUD BA00-BBFF, Ryu B700-B9FF plus BC00-BFBF. Never copy the old whole source-p files over current Sophia/Cheats/Water/cannon/OAM code. Native DB tests cover only the busy consumer, not full caller/queue admission.',
            'Palette DE binds current compiled DrawBlock/QueueFace and actual Bass CHR. Colored face parts use palette3 with outlines off. Need coordinated player/world palette/art allocation; no blind palette1 swap or global native-palette restore. Current source is unchanged.',
            'Current Rygar DM/DN ordinary route clears1-1/1-2 and reaches1-3 at7574; exact8785-frame replay reproduces red-Koopa death. DO landing response passes that encounter but dies later at1875/245, after an airborne Koopa bounce and tree-side contact. Use actual platform geometry next, not identical guide retries. Current bounded replay all visible HUD scroll writes on31, so old footage glitch not reproduced in this exact route.',
            'Remaining private Land/Arm/Rush/audio/Ryu, natural Hard Bill upgrades/showcases, Easy/Hard landing comparison, all14 current full routes/every upgrade/SFX and final native A/V recordings remain. Existing14 films are older identities. Retain all lossless and negatives, cap100GB.'])
    (V/'root-current49-progress-dp.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(main_unchanged=True,private_HUD_adopted=False,current_Rygar_cleared=['1-1','1-2'],workspace_bytes=used,goal_complete=False),indent=2),flush=True)
if __name__=='__main__':main()
