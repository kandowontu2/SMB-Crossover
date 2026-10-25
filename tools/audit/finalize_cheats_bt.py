"""Run scoped final regressions and freeze the new Options/Cheats feature."""
from pathlib import Path
from datetime import datetime,timezone
import concurrent.futures,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/cheats-final-bt';assert not O.exists();O.mkdir()
sys.path.insert(0,str(R/'tools'));import run_mesen
sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
roms={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
tasks=[(m,t)for m in roms for t in('character-select','player-outlines','guest-ordinary-contact','world-firebars','score-popup-location','terrain-coin-publication')]
def check(q):
 m,t=q;code=run_mesen.run(R/'tests'/(t+'.lua'),R/'build'/f'smb-crossover-{m}.nes',timeout=60)
 log=R/'build/verification'/f'smb-crossover-{m}-{t}.log';target=O/f'{t}-{m}.log';shutil.copyfile(log,target)
 return dict(mapper=m,test=t,exit=code,passed=code==0,log_sha256=sha(target),ROM_sha256=roms[m])
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:checks=list(pool.map(check,tasks))
for m in roms:
 for t in('cheats-menu','cheats-invincibility','bill-flagpole-full'):
  log=R/'build/verification'/f'cheats-final-bs-{t}-{m}.log';s=log.read_text(encoding='utf-8');assert'Mesen exit: 0'in s and'FAIL'not in s
  checks.append(dict(mapper=m,test=t,exit=0,passed=True,log_sha256=sha(log),ROM_sha256=roms[m]))
assert all(z['passed']for z in checks)
abi=R/'build/verification/cheats-abi-br/summary.json';ab=json.loads(abi.read_text());assert ab['passed']
assert all(z['ROM_sha256']==roms[z['mapper']]for z in ab['results'])
baselines=[]
for m in roms:
 p=R/'build'/f'smb-crossover-{m}-baseline.nes';before=sha(p)
 proc=subprocess.run([sys.executable,str(R/'tools/build.py'),'--mapper',m,'--baseline'],cwd=R,capture_output=True,text=True)
 (O/f'baseline-build-{m}.log').write_text(proc.stdout+proc.stderr,encoding='utf-8');assert proc.returncode==0
 baselines.append(dict(mapper=m,sha256=sha(p),literal_to_before=sha(p)==before));assert sha(p)==before
layout=[]
for m in roms:
 old=(R/'build/checkpoints/score-popup-location-az/build'/f'smb-crossover-{m}.nes').read_bytes()
 new=(R/'build'/f'smb-crossover-{m}.nes').read_bytes()
 assert new[:16]==old[:16]and new[-0x40000:]==old[-0x40000:]
 layout.append(dict(mapper=m,header_and_CHR_unchanged=True,changed_PRG_banks=sorted({(i-16)//8192 for i,(a,b)in enumerate(zip(old,new))if a!=b}),new_SRAM=['CheatInvincible=$7FFB','CheatStartLevel=$7FFC']))
report=dict(passed=True,ROMs=roms,native_checks=checks,compiled_CPU_report_sha256=sha(abi),baselines=baselines,layout=layout,
 scope='18 scoped native checks; 84 invincibility arenas per mapper plus menu tests over all32 selections and real Samus1-2 launch. Separate compiled CPU checks cover all starting-level mappings, continue/default behavior, injury predicate and exact native rare cleanup ABI. Not a full all-character recording or full source-fidelity audit.',goal_complete=False)
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
CP=R/'build/checkpoints/cheats-options-bt';assert not CP.exists();CP.mkdir()
names=[f'build/smb-crossover-{m}.{e}'for m in roms for e in('nes','lbl','dbg','map')]
names+=['smb1base.cfg','src/character_select.s','src/characters.s','src/common.s','src/collision.s','src/entrypoint.s','src/cheats.s','src/game.s','src/guest_body_contact.s','src/terrain_catchup.s','src/score_popup.s','tests/cheats-menu.lua','tests/cheats-invincibility.lua','tools/run_mesen.py','tools/verify.py']
for n in names:
 p=CP/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
manifest=dict(status='CHEATS_SUBMENU_IMPLEMENTED_BOTH_MAPPERS_NOT_FINAL_ROSTER_RELEASE',ROMs=roms,parent_checkpoint='build/checkpoints/score-popup-location-az/manifest.json',parent_checkpoint_sha256=sha(R/'build/checkpoints/score-popup-location-az/manifest.json'),hashes={n:sha(CP/n)for n in names},source_hashes={p.relative_to(R).as_posix():sha(p)for p in(R/'src').rglob('*')if p.is_file()},verification_summary_sha256=sha(O/'summary.json'),new_RAM_bytes=2,cold_tail='Physical bank14 DC00-DFFF is now A-mapped BC00-BFFF; previous Link art and orbit table addresses remain unchanged.',private_HUD_reservation_change='Old private HudStatusPending=$7FFB conflicts with the new real feature. It must be appended at$7FFD or later during additive composition; no old private HUD source was installed here.',goal_complete=False)
(CP/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
doc=R/'docs/qa/cheats-menu-2026-10-22.md'
doc.write_text('''# Options: Cheats submenu

Options now has a third row, CHEATS. Up/Down selects a row; A/Start opens it. Inside Cheats, Up/Down selects INVINCIBLE or START LEVEL. A/Start/Select/Left/Right toggles invincibility; Left/Right cycles the starting level (A/Start/Select also advances). B returns to Options, then the title.

Defaults are invincibility OFF and displayed level1-1. Until the level value is changed, native start/continue behavior remains intact. After a change, the selected1-1 through8-4 applies on the next character confirmation. Deaths and ordinary area transitions do not apply it again. Settings last until reset. Invincibility prevents enemy and hazard damage, retains the current power and avoids flashing/star effects. Pits and timer expiration retain their normal behavior.

## Validation

Both mapper builds pass the real controller menu test over all32 values and both wrap directions, held-button edge toggles, back navigation, existing option preservation, and a Samus1-2 launch through the actual native pipe intro. Screenshots were inspected. A menu-enabled invincibility test passes84 actual enemy-contact arenas per mapper: all14 identities, both modes, and all3 power forms. Native contact with cheats OFF, character selection, outlines, firebars, score anchors, terrain publication and Bill's full flagpole/castle transition also pass. The final scoped matrix has18 native checks.

Compiled CPU tests compare the relocated rare enemy cleanup against the previous ROM, including registers, flags, scratch, six slots, stack, windows and foreign MMC3 selectors. The damage predicate covers every InjuryTimer byte with cheats ON/OFF. Starting-level mapping covers all32 levels, explicit/default state and continue handling. This is not an interrupt-injection claim.

Two SRAM bytes are appended; header, CHR and rebuilt baseline ROMs remain identical. The menu uses an existing unused PRG tail. Only attempted injury gains16 cycles; normal non-contact gameplay gains no instructions. A rare enemy cleanup now incurs a bank round trip. The original menu's static third row is drawn with rendering disabled, keeping dynamic menu packets within the native queue capacity.

The first level implementation overwrote authored native starting stages even when untouched; the final version uses an explicit changed-value bit. The original failed flagpole checks are retained, and the final checks pass. An initial queue assertion incorrectly included gameplay HUD work; the corrected assertion checks the menu it claims to check. Earlier build/command/parser failures remain in the audit directory.

Checkpoint: `build/checkpoints/cheats-options-bt/manifest.json`. Final native receipts: `build/verification/cheats-final-bt/summary.json`. Compiled CPU receipt: `build/verification/cheats-abi-br/summary.json`.

The broader all-character source-fidelity, lag optimization, remaining bugs and final video goal remains active. Original recordings and lossless captures are retained under the user-approved100GB cap.
''',encoding='utf-8')
used=workspace_bytes(R);assert used<100000000000
handoff=dict(status='CHEATS_SUBMENU_FINISHED_BOTH_MAPPERS_FULL_ROSTER_GOAL_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),previous_progress_sha256=sha(R/'build/verification/root-current49-progress-az.json'),checkpoint=(CP/'manifest.json').relative_to(R).as_posix(),checkpoint_sha256=sha(CP/'manifest.json'),ROMs=roms,report=doc.relative_to(R).as_posix(),report_sha256=sha(doc),workspace_bytes=used,workspace_cap=100000000000,all_lossless_and_negatives_retained=True,root_native_handles=[],goal_status='active',goal_complete=False,
 previous_turn_classification='progress: all14 footage review completed and score repair frozen in AZ',
 current_turn_classification='progress: read-only exact Mario/Bill actor replay, new user-requested Cheats feature and scoped native/compiled tests',
 actor_review={'mario':'build/verification/world-actors-ba-mario/actor-summary.json','bill':'build/verification/world-actors-ba-bill/actor-summary.json','finding':'All seven1-4 owners retain six parts; 11,530 cached visible part positions match OAM at the firebar pass. No Bullet Bills occur in these routes. No claim about final DMA, later castles or the reported duplication.'},
 new_default_mario_old_input_failure='cheats-default-mario-bq dies atframe1913 on original old movie inputs. Negative retained, no through2-2 claim; route retiming already needed after terrain repair.',
 next=['Use real Cheats level selection and invincibility as explicitly cheated diagnostics for5-1 cannons and later castles; new menu avoids authored stage RAM. Original actor routes have no Bullet Bills. BD late-seed probe never reached seed, BE early-seed5-1 probe died before cannons; do not repeat same failed stimuli.',
 'Hard natural upgrades: AY0/1 Flare, AY2/BC3..5 Laser. BF6/8/10 terminal, no naturally-collected event before3400; inspect pickup trajectories and adapt controller acquisition before more wait sweeps. No Hard A/V clips captured yet. Use AZ ROM for exact old AY inputs.',
 'Retain cheats, Claude wall/Water/origin, AF terrain and AZ score during additive composition of private HUD/Land/Arm/Rush/audio/Ryu/visibleWater. New actual cheat SRAM occupies7FFB/C; private HUD must move new Pending to7FFD or later. SAMUS now fillsBFFF onMMC5 due6 init bytes; respect capacity.',
 'Retiming needed for fresh ordinary visits/recordings through2-2. Existing films remain old baseline identities. Underground brick palettes, late HUD splits, Bullet Bills, later firebars and remaining candidates are still open.',
 'Original full every-character/every-ability/every-upgrade/mode/SFX/performance scope and final all-character captures remain unfulfilled.'])
(R/'build/verification/root-current49-progress-bt.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checkpoint=str(CP),ROMs=roms,native_checks=len(checks),workspace_bytes=used,goal_complete=False),indent=2))
