from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'build/verification/cannon-cooldown-bz';assert not O.exists();O.mkdir()
sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def labels(p):return {s.split()[2]:int(s.split()[1],16)for s in p.read_text().splitlines()if s.startswith('al ')}
by=R/'build/verification/cannon-repair-by/summary.json';r=read(by);assert r['passed']
checks=[]
for m in('mmc3','mmc5'):
 for t in('mario-water','luigi-native-water-pit','bill-water','megaman-water'):
  p=R/'build/verification'/f'cannon-water-by-{t}-{m}.log';s=p.read_text(encoding='utf-8');assert'Mesen exit: 0'in s and'FAIL'not in s
  checks.append(dict(test=t,mapper=m,log=p.relative_to(R).as_posix(),sha256=sha(p)))
 p=R/'build/verification'/f'cannon-cooldown-bw-native-{m}.log';s=p.read_text(encoding='utf-8');assert'PASS 112 native'in s and'Mesen exit: 0'in s and'FAIL'not in s
 checks.append(dict(test='cannon-cooldown',mapper=m,log=p.relative_to(R).as_posix(),sha256=sha(p)))
negative=R/'build/verification/cannon-cooldown-bw-old-negative.log';assert'actual0 expected14'in negative.read_text(encoding='utf-8')
roms={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
parent=R/'build/checkpoints/cheats-options-bt';layout=[]
for m in roms:
 before=parent/'build'/f'smb-crossover-{m}.nes';after=R/'build'/f'smb-crossover-{m}.nes'
 a,b=before.read_bytes(),after.read_bytes();diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y]
 assert a[:16]==b[:16]and a[-0x40000:]==b[-0x40000:]
 assert all((i-16)//8192==62 for i in diff)
 oldL=labels(before.with_suffix('.lbl'));newL=labels(after.with_suffix('.lbl'));assert all(newL.get(k)==v for k,v in oldL.items())
 baseline=R/'build'/f'smb-crossover-{m}-baseline.nes';oldsha=sha(baseline)
 proc=subprocess.run([sys.executable,str(R/'tools/build.py'),'--mapper',m,'--baseline'],cwd=R,capture_output=True,text=True)
 (O/f'baseline-build-{m}.log').write_text(proc.stdout+proc.stderr,encoding='utf-8');assert proc.returncode==0 and sha(baseline)==oldsha
 layout.append(dict(mapper=m,changed_bytes=len(diff),changed_banks=[62],header_CHR_and_baseline_unchanged=True,all_old_label_addresses_unchanged=True,new_RAM_bytes=0))
CP=R/'build/checkpoints/cannon-cooldown-bz';assert not CP.exists();CP.mkdir()
names=[f'build/smb-crossover-{m}.{e}'for m in roms for e in('nes','lbl','dbg','map')]
names+=['src/game.s','tests/cannon-cooldown.lua','tools/verify.py']
for n in names:
 p=CP/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
cp=dict(status='CANNON_COOLDOWN_ALIAS_REPAIRED_BOTH_MAPPERS_NOT_FINAL_ROSTER_RELEASE',ROMs=roms,parent_checkpoint='build/checkpoints/cheats-options-bt/manifest.json',parent_checkpoint_sha256=sha(parent/'manifest.json'),hashes={n:sha(CP/n)for n in names},source_hashes={p.relative_to(R).as_posix():sha(p)for p in(R/'src').rglob('*')if p.is_file()},layout=layout,native_checks=checks,native_old_ROM_negative_sha256=sha(negative),ordinary_controller_explicit_cheat_diagnosis_sha256=sha(by),goal_complete=False)
(CP/'manifest.json').write_text(json.dumps(cp,indent=2)+'\n',encoding='utf-8')

# Contact sheet contains untouched native pixels, with labels outside the game.
frames=[1000,1200,1650,1850];sheet=Image.new('RGB',(1024,528),'#202020');d=ImageDraw.Draw(sheet)
for row,tag in enumerate(('cannon-bx-before','cannon-bx-after')):
 P=R/'build/roster-through-2-2'/f'{tag}-3-v0-mmc3'
 expr='+'.join(f'eq(n\\,{f-1})'for f in frames)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'playthrough-lossless.mkv'),'-vf','select='+expr,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
 size=256*240*3;assert len(raw)==size*4
 for col,frame in enumerate(frames):
  sheet.paste(Image.frombytes('RGB',(256,240),raw[col*size:(col+1)*size]),(col*256,row*264+24))
  d.text((col*256+3,row*264+5),f'{"BEFORE"if row==0 else"AFTER"} native index{frame-1}',fill='white')
sheet.save(O/'native-cannon-comparison.png')
doc=R/'docs/qa/cannon-cooldown-2026-10-22.md';doc.write_text('''# Bullet Bill rapid-spawn repair

Guest whirlpool immunity cleared `Whirlpool_Flag` on every update, including dry areas. That byte is also `Cannon_Timer[0]`. The first cannon's native14-tick cooldown was reset to zero immediately after it fired, allowing repeated Bullet Bills a few frames apart.

The area-type check now precedes the guest-water branch. Dry areas leave the shared timer untouched; underwater behavior is retained. The same instructions were reordered, with no new RAM, no size growth and no moved old code/RAM labels. Header, CHR and rebuilt baseline ROMs remain identical. Dry dispatch also avoids the unnecessary guest check; this is a small common-path saving, not a claim that all lag is fixed.

## Native verification

- The permanent native regression passes112 cases on each mapper: all14 identities, both modes, all4 area types and all6 shared timer bytes. The old ROM fails precisely on guest character1, dry area1, timer14 overwritten with0.
- Mario water, Luigi's native whirlpool control, Bill water and Mega Man water pass on both mappers.
- The same2,200-frame controller stream selects5-2 and enables invincibility using the actual new menu. This is an explicitly cheated diagnostic, not a final route. The old MMC3 run is byte-identical to the original discovery trace, including cycles. The old run has26 fire attempts and26 forced cooldown clears; the new run has5 attempts, zero forced clears and56 native countdown writes. The minimum attempt interval changes from3 to118 physical frames in this specific stimulus. MMC5 produces the same repaired counts.
- Before and after each retain2,199 native video images and continuous real PCM audio. Both lossless RGB/PCM proofs pass. Full-frame review finds no motion, HUD split, vertical displacement or large background flash candidates in these bounded clips. Audio-ownership candidates are not a source-SFX certification. Multiple normally spaced native Bills remain allowed.

Evidence: `build/verification/cannon-repair-by/summary.json`; native recordings and controller inputs are under `build/roster-through-2-2/cannon-bx-before-3-v0-mmc3/` and `cannon-bx-after-3-v0-mmc3/`. The MMC5 read-only diagnostic is `cannon-bx-after-mmc5-3-v0-mmc5/`. Checkpoint: `build/checkpoints/cannon-cooldown-bz/manifest.json`.

Missing later-castle firebars remain unresolved. Earlier exact Mario/Bill movie replays show all seven1-4 firebars at the firebar OAM pass, but do not prove the later-castle report fixed. Diagnostic4-4 drivers currently fail at the first ceiling/gap combination before reaching the firebars; those negatives are retained. All other source-fidelity, private component composition, natural Hard upgrade showcases, lag optimization and final every-character recordings remain required. Lossless originals and negatives are retained under the user-authorized100GB cap.
''',encoding='utf-8')
used=workspace_bytes(R);assert used<100000000000
handoff=dict(status='BULLET_BILL_RAPID_SPAWNS_REPAIRED_BOTH_MAPPERS_FULL_GOAL_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),previous_progress_sha256=sha(R/'build/verification/root-current49-progress-bt.json'),checkpoint=(CP/'manifest.json').relative_to(R).as_posix(),checkpoint_sha256=sha(CP/'manifest.json'),ROMs=roms,report=doc.relative_to(R).as_posix(),report_sha256=sha(doc),layout=layout,workspace_bytes=used,workspace_cap=100000000000,all_lossless_and_negatives_retained=True,root_native_handles=[],goal_status='active',goal_complete=False,
 previous_turn_classification='progress: Cheats submenu implemented and verified on both mappers',current_turn_classification='progress: reproduced cannon timer alias clobber with real menu input, repaired it, native old/new regressions, exact controller A/V comparisons',
 next=['Missing firebars: 1-4 has all seven owners at the firebar pass; later cases remain. New real-menu4-4 Bill drivers BU/BV die at first ceiling/short-pit sequence. BV log shows jumps atx40/Y80 andx71/Y112 bonking ceiling aroundx78/Y91 before missing pillarx104. Retiming must address that actual geometry; do not repeat the same generic policy.',
 'Investigate dense-firebar allocation starvation as a hypothesis, not a confirmed bug: renderer allocates them after world objects with a fixed owner order, and rejects headers beyond64 total slots. Need actual before/after OAM evidence; existing sparse1-4/vertical fixtures do not cover it.',
 'diagnostic_level_bu.py currently defaults to frozen BT. Supply/update an explicit --rom option before assuming later diagnostics run BZ. It uses real menu invincibility and level selection and no emulated writes. BV5-2 Bill is the successful cannon stimulus; BV5-1 Mario stops too close to his cannon to produce bullets.',
 'Private HUD consumer-busy fix, Land/Arm/Rush/audio/Ryu/visibleWater composition remain uninstalled. Preserve current Claude, terrain, score, cheats and cannon changes; new SRAM7FFB/C belongs to cheats, private Pending must move to7FFD or later; MMC5 SAMUS is fullBFFF.',
 'Natural Hard upgrades: AY0/1 Flare, AY2/BC3..5 Laser. BF6/8/10 terminal without pickup by3400. Inspect native pickup trajectories before another wait sweep. Final Hard clips and Easy/Hard enemy landing comparison remain absent. Use AZ for exact old AY inputs.',
 'Original ordinary through2-2 every-character/every-ability/every-upgrade/source-SFX/performance scope and final A/V recordings remain unfulfilled. Old movies are not retagged as current.'])
(R/'build/verification/root-current49-progress-bz.json').write_text(json.dumps(handoff,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checkpoint=str(CP),ROMs=roms,layout=layout,workspace_bytes=used,goal_complete=False),indent=2))
