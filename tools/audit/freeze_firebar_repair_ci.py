from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'build/verification/firebar-budget-ci';assert not O.exists();O.mkdir()
sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
ce=R/'build/verification/firebar-budget-ce/summary.json';old=read(ce)
roms={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
checks=[z for z in old['native_checks']if z['test']not in('roster-projectiles-oam','megaman-projectiles-overload')]
assert len(checks)==18 and all(z['passed']and z['ROM_sha256']==roms[z['mapper']]for z in checks)
for m in roms:
 for t in('megaman-projectiles-overload','bill-projectiles-oam','link-projectiles-oam','simon-projectiles-oam'):
  p=R/'build/verification'/f'firebar-projectiles-cg-{t}-{m}.log';s=p.read_text(encoding='utf-8');assert'Mesen exit: 0'in s and'FAIL'not in s
  checks.append(dict(mapper=m,test=t,passed=True,ROM_sha256=roms[m],log=p.relative_to(R).as_posix(),log_sha256=sha(p)))
assert all(z['literal']for z in old['baselines'])
report=dict(passed=True,ROMs=roms,native_checks=checks,original_CE_matrix_passed=False,original_CE_matrix_sha256=sha(ce),
 corrected_test_sampling='An independent native observer proved false MMC3 callbacks during NSF NMI: CurrentBank shadow4 but actual opcode f02b8c520130494e versus60684a850b4a650b. Added balanced NMI/IRQ scope to both buster fixture callbacks; same visibility requirement passes16/16 foreground parts. The roster-projectiles file is a helper and requires Bill/Link/Simon wrappers; all6 real wrapper/map runs pass.',
 dense_comparison=old['dense_comparison'],baselines=old['baselines'],old_native_negatives=old['old_negatives'],
 scope='26 scoped native tests, including64 completed dense lists and64 actual DMA observations per mapper, all17 authored ordinary objects once per list, all24 firebar parts with a nontransparent row inside hardware scanline admission. This is an authored render stress scene, not a native castle traversal or a complete all-character audit.',goal_complete=False)
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
CP=R/'build/checkpoints/firebar-budget-ci';assert not CP.exists();CP.mkdir()
names=[f'build/smb-crossover-{m}.{e}'for m in roms for e in('nes','lbl','dbg','map')]
names+=['src/metasprite_engine.s','tests/firebar-budget-fairness.lua','tests/megaman-projectiles-overload.lua','tools/verify.py']
for n in names:
 p=CP/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
manifest=dict(status='DENSE_FIREBAR_ADMISSION_FAIRNESS_REPAIRED_BOTH_MAPPERS_NOT_FINAL_ROSTER_RELEASE',ROMs=roms,parent_checkpoint='build/checkpoints/cannon-cooldown-bz/manifest.json',parent_checkpoint_sha256=sha(R/'build/checkpoints/cannon-cooldown-bz/manifest.json'),hashes={n:sha(CP/n)for n in names},source_hashes={p.relative_to(R).as_posix():sha(p)for p in(R/'src').rglob('*')if p.is_file()},verification_summary_sha256=sha(O/'summary.json'),new_RAM_bytes=0,baseline_header_CHR_unchanged=True,renderer_growth_bytes=18,mmc3_renderer_last_address='BFFC',goal_complete=False)
(CP/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
sheet=Image.new('RGB',(512,528),'#202020');d=ImageDraw.Draw(sheet)
for row,version in enumerate(('old','new')):
 for col,frame in enumerate((650,690)):
  image=Image.open(R/'build/verification/firebar-budget-ce'/version/'mmc3'/f'smb-crossover-mmc3-firebar-budget-{frame}.png').convert('RGB')
  assert image.size==(256,240);sheet.paste(image,(col*256,row*264+24));d.text((col*256+4,row*264+6),f'{"BEFORE"if row==0 else"AFTER"} arena frame{frame}',fill='white')
sheet.save(O/'native-budget-comparison.png')
doc=R/'docs/qa/firebar-budget-2026-10-22.md'
doc.write_text('''# Firebars disappearing in crowded scenes

The renderer always allocated firebars after every ordinary object. When the sprite list filled, the same low-priority firebars were rejected on every update. The OAM priority ring rotates already-allocated records, so it could not recover an object that never entered the list.

Firebars now take the existing shuffled object-list position0. The player retains its reservation, weapons retain their first allocation, and every ordinary object retains exactly one turn. The original live-owner/firebar-ID checks and all native collision parts remain unchanged. Crowded scenes share admission over time; the NES hardware limits still require flicker when overloaded. Sparse scenes retain every firebar part.

## Evidence

An authored dense native-renderer scene contains Bowser's two halves, a long firebar with its duplicate slot, two short firebars, nine hammers, block effects and projectiles. No OAM, ROM, CPU or hardware registers are patched; borrowed render fields are restored at the actual completed-draw return. This is a stress fixture, not a controller-only castle clear.

In64 completed lists on each old mapper build, both short firebars receive zero records every time; the long bar receives only8/12 parts. With the repair, the two short bars receive complete allocation in37/64 and50/64 lists, and the long bar in58/64. All17 ordinary authored objects still receive exactly one draw call. All64 observed DMA payloads match actual hardware sprite RAM, and every one of the24 firebar parts receives a nontransparent mapped sprite row within the eight-sprite scanline limit during the observation window.

The final aggregate has26 scoped native checks: admission ID/flag edges, sparse short/long firebars across the roster, native castle source pixels, Bill overload, Mega Man overload, real Bill/Link/Simon projectile wrappers, cannon cooldown, Cheats UI, score anchors and terrain publication, on both mappers. The original failed CE matrix is retained. One failure was a helper run without its required character wrapper. An independent observer proved the MMC3 buster test was sampling NSF music during NMI at the same CPU address; balanced interrupt guards correct the sampling while retaining the16/16 foreground-part visibility requirement.

The code adds18 renderer bytes and no RAM. Rebuilt baseline ROMs, headers and CHR are unchanged. In this full-list fixture, mean inclusive render time rises from26308 to26493 cycles on MMC3 and25409 to25591 on MMC5. These measurements include interrupt variance; they are not a general lag improvement. No claim is made that all flicker or lag is solved.

Final receipt: `build/verification/firebar-budget-ci/summary.json`. Checkpoint: `build/checkpoints/firebar-budget-ci/manifest.json`. Before/after native screenshots are retained with the test inputs and logs under `build/verification/firebar-budget-ce/`.

Later-castle traversal remains unverified. Ordinary menu-selected diagnostic drivers for4-4 fail at the initial ceiling/pit sequence; the2-4 Bill driver reaches x499 before a later pit. Those failures are retained. Existing1-4 actor evidence and this rendering repair do not certify every castle layout. The original full all-character abilities, source fidelity, SFX, optimization, final recordings and natural Hard showcase requests remain active.
''',encoding='utf-8')
used=workspace_bytes(R);assert used<100000000000
handoff=dict(status='DENSE_FIREBAR_ADMISSION_REPAIRED_BOTH_MAPPERS_FULL_GOAL_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),previous_progress_sha256=sha(R/'build/verification/root-current49-progress-bz.json'),checkpoint=(CP/'manifest.json').relative_to(R).as_posix(),checkpoint_sha256=sha(CP/'manifest.json'),ROMs=roms,report=doc.relative_to(R).as_posix(),report_sha256=sha(doc),verification= (O/'summary.json').relative_to(R).as_posix(),verification_sha256=sha(O/'summary.json'),workspace_bytes=used,workspace_cap=100000000000,all_lossless_and_negatives_retained=True,root_native_handles=[],goal_status='active',goal_complete=False,
 previous_turn_classification='progress: cannon cooldown alias fixed and exact controller A/V comparison retained',current_turn_classification='progress: dense firebar starvation reproduced, virtual object0 admission implemented and hardware/CHR/scanline verified;26 scoped regressions after evidence-backed fixture correction',
 next=['Do not overwrite the installed metasprite-engine changes when composing private candidates. Firebar admission moved from the fixed tail to object index0 in both positive/negative loops; body reservation and weapon-first policy remain. The bank4 renderer now endsBFFC onMMC3 with only3 bytes spare.',
 'Original later-castle route report is not fully reproduced as a controller clear. BU/BV/CH4-4 drivers fail under the initial ceiling. CH2-4 Bill reachesx499 before a pit, no firebar owners yet. Use actual terrain/input mechanics if continuing, not another identical generic policy. diagnostic_level_bu.py now accepts explicit --rom; its default remains frozen BT for old-stimulus reproducibility.',
 'Merge and validate private HUD consumer-busy fix, Land/Arm/Rush/audio/Ryu/visibleWater with current Claude/terrain/score/cheats/cannon/OAM code. New SRAM7FFB/C belongs to Cheats; append pending at7FFD or later; MMC5 SAMUS is fullBFFF. Existing old whole-file copies would revert installed fixes.',
 'Natural Hard upgrades: AY0/1 Flare, AY2/BC3..5 Laser. BF6/8/10 terminal without pickup by3400. Inspect pickup trajectories before more wait sweeps. Hard A/V clips and Easy/Hard landing comparison remain absent; use AZ for old exact AY inputs.',
 'Retiming required for final ordinary no-cheat through2-2 routes. Existing14 movies remain old build identities. Complete all-character/every-special/every-upgrade/acquisition/ammo/SFX/behavior/performance scope before any completion claim. All lossless originals and negatives retained.'])
(R/'build/verification/root-current49-progress-ci.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checkpoint=str(CP),ROMs=roms,checks=len(checks),workspace_bytes=used,goal_complete=False),indent=2))
