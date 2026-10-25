from pathlib import Path
import json,hashlib,shutil,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
ag=R/'build/verification/terrain-repair-build-ag/summary.json';g=read(ag);assert g['passed']and len(g['results'])==22
aj=R/'build/verification/showcase-pixels-aj/report.json';j=read(aj);assert j['source_frames']==j['edit_frames']==2459 and j['different_gameplay_pixel_frames']==0 and j['native_pcm_identical']
native={}
for m in ('mmc3','mmc5'):
 p=R/'build/verification'/f'terrain-coin-permanent-{m}-af.log';s=p.read_text(encoding='utf-8');assert 'PASS native queued attributes'in s and 'Mesen exit: 0'in s and 'FAIL'not in s;native[m]=dict(path=str(p.relative_to(R)),sha256=sha(p))
O=R/'build/checkpoints/terrain-publication-af';assert not O.exists();O.mkdir()
names=[f'build/smb-crossover-{m}.{e}'for m in ('mmc3','mmc5')for e in ('nes','lbl','dbg','map')]+['src/game.s','src/guest_body_contact.s','src/terrain_catchup.s','tests/terrain-coin-publication.lua','tools/verify.py']
for n in names:
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
roms={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in ('mmc3','mmc5')}
for z in g['layout']:assert roms[z['mapper']]==z['sha256']
cp=dict(status='INSTALLED_TERRAIN_PUBLICATION_AF_NOT_FINAL_RELEASE',parent_commit='443d07a498ba26fb3925465feaa2b37daf38c69c',parent_checkpoint_sha256=sha(R/'build/checkpoints/terrain-publication-o/manifest.json'),hashes={n:sha(O/n)for n in names},source_hashes={p.relative_to(R).as_posix():sha(p)for p in(R/'src').rglob('*')if p.is_file()},ROMs=roms,build_and_existing22_regression_sha256=sha(ag),new_native_regression=native,normal_no_lag_instruction_path_unchanged=True,new_RAM_bytes=0,all_old_RAM_and_code_label_addresses_unchanged=True,changed_ROM_bytes_each_mapper=19,changed_banks=[62,63],scope='Retain a published secondary VRAM packet before another catch-up update. Final all-character routes and broader fixes remain open.',goal_complete=False)
(O/'manifest.json').write_text(json.dumps(cp,indent=2)+'\n',encoding='utf-8')
clip=R/'Playthrough Videos/Showcases/Ready/Bill-Easy-Progression.mp4';clipreport=R/'Playthrough Videos/Showcases/Ready/Bill-Easy-Progression.json';c=read(clipreport);assert sha(clip)==c['mp4_sha256']
report=R/'docs/qa/terrain-publication-repair-2026-10-22.md';assert not report.exists()
report.write_text('''# Terrain publication repair and Easy Bill demonstration

The green ground/cloud patch in Bill’s 1-3 movie was caused by a dropped attribute column. A normal update queued seven background attribute writes. Before NMI consumed them, an immediate lag catch-up collected a coin. The native coin/axe erase writes the secondary VRAM queue from its beginning, replacing the column with its own ten-byte packet and terminator.

The original, read-only Bill replay reproduces the overwrite at frame **14406**. Its first 15,000 trace rows and cycle counts are byte-identical to the original recording. `build/verification/bill-green-producer-l/producers.csv` preserves both producers and their exact packet contents; `summary.json` binds the literal replay.

## Installed repair

After an update actually lags, `IdleLoop` now checks whether secondary VRAM work is still published. If so it lets NMI consume that work before starting another catch-up. Otherwise it retains the existing one-catch-up behavior and sprite-skip flag. Normal updates retain the original comparison/branch path and incur no additional instructions.

The helper occupies fourteen bytes of an already unreachable resident bridge tail. Both mappers change only nineteen ROM bytes in banks62/63. All old code-label addresses and RAM addresses, header and CHR remain unchanged. No new RAM or mapper feature is required. Checkpoint: `build/checkpoints/terrain-publication-af/manifest.json`.

The first O candidate called its predicate even on normal frames. AF moves the check behind the existing lag branch to avoid that common cost. O remains frozen because the demonstration below was recorded on that exact candidate. No recording is retagged as AF.

## Verification

- The old-ROM native fixture fails specifically because coin collection overwrites the queued attribute column.
- The new permanent `terrain-coin-publication` test passes on MMC3 and MMC5. It authors a lag/coin arena, then observes the actual coin handler, NMI consumer and all seven physical PPU attributes. This is an explicit diagnostic fixture, not a controller-only clear.
- Eleven existing tests pass on each mapper: character selection, outline option, Mario pipes, Luigi physics, Bill flagpole, Samus head displacement, Sophia weapons, springs, firebar draw admission, roster stomps and Bill inventory. These are24 checks including the new regression on each mapper; they are not a new full757-case suite.
- Build and existing-test receipt: `build/verification/terrain-repair-build-ag/summary.json`. Permanent native logs: `build/verification/terrain-coin-permanent-mmc3-af.log` and `terrain-coin-permanent-mmc5-af.log`.

## New ordinary Easy progression recording

[Bill Easy progression MP4](../../Playthrough%20Videos/Showcases/Ready/Bill-Easy-Progression.mp4) shows the normal rifle, a naturally collected mushroom and machine gun, then the naturally collected 1-1 Fire Flower and spread shot. It includes native game audio and captions above the image. The posted edit is40.916seconds; there are no gameplay cuts after removing the menu/loading prefix.

The fixed power-on replay has3,000 emulator frames and2,999 native captured images, with zero deaths. Its trace and inputs exactly match the independently discovered prefix. The lossless native RGB/PCM verification passes. Every edited gameplay frame also matches the native pixels after reversing the nearest-neighbor scaling, and its PCM audio matches the trimmed native PCM exactly. The H.264 MP4 is the lossy delivery copy.

- Native packet, controller replay and lossless capture: `build/roster-through-2-2/bill-easy-showcase-z-3-v0-mmc3/`.
- Editorial lossless master and delivery manifest: `Playthrough Videos/Showcases/Ready/`.
- Pixel/PCM receipt: `build/verification/showcase-pixels-aj/report.json` —2,459/2,459 frames, zero differing gameplay-pixel frames, identical native PCM.
- General frame review: no motion, split, lag-CHR or vertical-row flags in this bounded capture. Audio queue flags are not interpreted as proof of missing sounds; all source-SFX parity remains part of the larger audit.

This demonstration is a bounded1-1 sequence on O. It is not a through-2-2 clear or a claim that all current bugs are fixed. Earlier editorial attempts are preserved: AC dropped the last frame through shortest-stream truncation; AD kept the frames but used YUV caption composition. The Ready/RGB edit fixes both and is the intended file to use.

## Open work

The terrain repair changes catch-up timing, so original full-route inputs cannot be assumed valid on it. The first old Bill transfer dies in1-1. New controller policies collect both1-1 upgrades and clear1-1, then currently reach a later1-2 failure at x2303. A specific first-gap controller correction clears the low brick ceiling before jumping; this is ordinary gameplay, not a ROM collision change. A fresh ordinary visit and recording of the formerly corrupted1-3 location still remains to be completed.

The score-popup report now has an ordinary replay baseline: five of sixteen observed Bill score anchors use a stale shared enemy-relative X. That repair is not installed. Bullet Bill duplication, missing firebars, underground bounced-brick colors, late HUD splits, Pit’s contact-frame candidate and the tree-color strip remain open. A passing firebar draw-admission test is not proof that the user’s missing-firebar report is fixed.

Hard-mode natural upgrade clips, the Easy/Hard enemy-landing comparison, all-character final recordings, every special/alternate/upgrade lifecycle and remaining lag optimization remain required. The older frozen Land/Arm/Rush/audio/HUD/Ryu/visible-Water candidates have not been merged by this repair. All original videos, native captures and negative evidence are retained under the user-approved100GB cap.
''',encoding='utf-8')
review=R/'docs/qa/footage-review-2026-10-22.md';s=review.read_text(encoding='utf-8');s+='\nFollow-up: [terrain repair and new Easy Bill recording](terrain-publication-repair-2026-10-22.md) documents the later installed repair. Findings above retain their original movie/build identities.\n';review.write_text(s,encoding='utf-8')
used=workspace_bytes(R);assert used<100000000000
handoff=dict(status='TERRAIN_COLOR_DROP_REPAIRED_AF_BOTH_MAPPERS_EASY_BILL_PREVIEW_READY_FULL_GOAL_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),previous_progress_sha256=sha(R/'build/verification/root-current49-progress-footage-k.json'),checkpoint=str((O/'manifest.json').relative_to(R)),checkpoint_sha256=sha(O/'manifest.json'),ROMs=roms,source_changes=['src/game.s','src/guest_body_contact.s','src/terrain_catchup.s'],test_changes=['tests/terrain-coin-publication.lua','tools/verify.py'],existing_checks=22,new_native_regression_maps=2,normal_lag_free_path_unchanged=True,report=str(report.relative_to(R)),report_sha256=sha(report),preview=str(clip.relative_to(R)),preview_metadata_sha256=sha(clipreport),preview_ROM=c['rom_sha256'],preview_is_O_not_AF=True,preview_source_images=2999,preview_edit_images=2459,preview_lossless_native_pcm_and_gameplay_pixels_exact=True,full_all_character_final_movies_not_regenerated=True,goal_status='active',goal_complete=False,current_turn_classification='progress',workspace_bytes=used,workspace_cap=100000000000,all_lossless_and_negatives_retained=True,root_native_handles=[],remaining=['Visit and record repaired1-3 location with retimed ordinary Bill controls; first new full candidate reaches1-2 x2303 before dying.','Fix stale score anchors: ordinary baseline16 calls/5wrong in score-popup-baseline-m. Consider moving SetupFloateyNumber body to the unused OBJECT bank0 tail behind a same-size native farcall stub; compute target worldX-camera while preserving caller C/V and X/Y. Check both mapper tail capacity first. Avoid another long resident-space search; current helper uses14/16 GuestBodyContactBridge padding.','Diagnose/fix actual Bullet Bill duplicates, missing castle firebars, underground bouncing-brick colors, late HUD splits and remaining visual candidates.','Finish reviewed/private HUD consumer-busy semantics, Land/Arm/Rush/audio/Ryu/visible-Water composition on current AF while retaining Claude wall-climb/cache/origin improvements.','Create natural Hard Contra upgrade recordings and Easy/Hard landing comparison; Ready clip currently covers Easy1-1 only.','Complete original all-character/all-ability/all-upgrade/mode/acquisition/SFX/performance scope and fresh final through2-2 recordings on final ROMs.'])
(R/'build/verification/root-current49-progress-ak.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checkpoint':str(O),'ROMs':roms,'preview':str(clip),'workspace_bytes':used,'goal_complete':False},indent=2))
