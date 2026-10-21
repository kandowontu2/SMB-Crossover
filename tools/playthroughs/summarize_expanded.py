"""Publish the twelve accepted, hash-pinned recordings without changing the original-six audit."""
from pathlib import Path
import csv,hashlib,html,json,subprocess
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/playthroughs'
RATE=60.098811
def rows(p):return list(csv.DictReader(p.open()))
def folder(c,route):return OUT/(f'expanded-qa-ryu-{c}-{route}' if c==10 and route=='surface' else f'expanded-qa-{c}-{route}')
def evidence(directory,center,name):
 first,last=center-3,center+5
 raw=subprocess.run(['ffmpeg','-v','error','-i',str(directory/'native.avi'),'-vf',f"select='between(n,{first-1},{last-1})'",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,check=True).stdout
 frames=np.frombuffer(raw,np.uint8).reshape(-1,240,256,3)
 sheet=Image.new('RGB',(3*256,3*260),'#202020');draw=ImageDraw.Draw(sheet)
 for i,pixels in enumerate(frames):
  x=i%3*256;y=i//3*260;sheet.paste(Image.fromarray(pixels),(x,y));draw.text((x+3,y+242),f'frame {first+i}',fill='white')
 target=OUT/'expanded-issue-evidence'/f'{name}.png';target.parent.mkdir(exist_ok=True);sheet.save(target)
 clip=target.with_suffix('.mp4')
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(max(0,center/RATE-1)),'-i',str(directory/'native.avi'),'-t','3','-vf','setsar=5/4','-c:v','libx264','-crf','12','-pix_fmt','yuv420p','-c:a','aac',str(clip)],check=True)
 return target,clip
def main():
 records=[]
 for c in range(6,12):
  for route in ('surface','pipe'):
   d=folder(c,route);m=json.loads((d/'manifest.json').read_text());r=json.loads((d/'review.json').read_text())
   assert m['verified_full_coverage'] and m['controller_only'] and not m['memory_or_register_writes']
   assert r['video_matches_emulated_frames'] and r['audio']['non_silent'] and r['coverage']['next_level_control']
   assert r['coverage']['enemies_defeated']==(17 if route=='surface' else 6)
   assert r['powerup_emergence_sequences']==(5 if route=='surface' else 1)
   assert hashlib.sha256((d/'smb-crossover-mmc3.nes').read_bytes()).hexdigest()==m['rom_sha256']
   assert not any(r[k] for k in ('hud_split_flags','pixel_vertical_shift_flags','missing_common_sfx_flags','powerup_palette_flags','powerup_emergence_motion_flags'))
   records.append({'directory':d.name,**r})
 assert len({r['rom_sha256'] for r in records})==1
 bass=folder(9,'surface');trace={int(r['frame']):r for r in rows(bass/'trace.csv')}
 overload=next(int(r['frame']) for r in rows(bass/'render.csv') if int(r['frame'])>=550 and int(r['oamMax'])>8 and trace[int(r['frame'])]['enemyCount']=='0')
 findings=[
  {'character':'Luigi','frame':2765,'directory':folder(8,'surface'),'slug':'luigi-powerup-snap','description':'After the airborne flower upgrade, releasing A clamps Luigi to the minimum jump height. In one frame he moves 39 pixels down and eight left. The jump-release code rewinds his position instead of ending the rise.'},
  {'character':'Bass','frame':overload,'directory':bass,'slug':'bass-sprite-overload','description':'Bass can exceed eight sprites on a scanline even without enemies. The two routes have 2,912 overloaded frames (30.1%); priority rotation cannot make every part visible on each frame.'},
  {'character':'Bass','frame':1217,'directory':bass,'slug':'bass-air-shot','description':'Airborne shooting selects the standing attack pose, including its grounded leg position, instead of a separate airborne shooting pose.'},
  {'character':'Ryu','frame':2845,'directory':folder(10,'surface'),'slug':'ryu-air-slash','description':'Airborne melee selects the ground slash sequence. The pinned reference has a separate falling attack sequence.'},
  {'character':'Sophia','frame':2838,'directory':folder(11,'surface'),'slug':'sophia-hover','description':'Hover movement works, but the wheel exhaust/flame animation and sustained hover sound from the pinned reference are absent. The sound is never queued, so common-SFX queue checks cannot detect its absence.'},
  {'character':'Sophia','frame':3469,'directory':folder(11,'surface'),'slug':'sophia-wall','status':'follow-up','description':'The generated wall art is unrotated. This route contains only one wall-contact frame, so a sustained wall-climb replay is needed to judge the visible transition against the reference.'},
 ]
 for f in findings:
  f.setdefault('status','confirmed');pic,clip=evidence(f['directory'],f['frame'],f['slug']);f['seconds']=round(f['frame']/RATE,3);f['directory']=f['directory'].name;f['image']=pic.relative_to(OUT).as_posix();f['clip']=clip.relative_to(OUT).as_posix()
 summary={'rom_sha256':records[0]['rom_sha256'],'decoded_video_frames':sum(r['decoded_video_frames'] for r in records),'method':'Every-frame automated decode/state/PPU/SFX checks; manual contact sheets and sequential issue frames. Not every frame was watched manually.','recordings':records,'findings':findings,'runtime_fixes_in_recordings':False}
 (OUT/'expanded-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 md=['# World 1-1 audit: six added characters','',f"Twelve fixed-controller recordings cover Pit, Rygar, Luigi, Bass, Ryu and Sophia, with both routes for each. All runs survive and verify movement in 1-2. Each surface run defeats all 17 enemies and collects five power-ups; each shortcut run defeats all six encountered enemies and collects its mushroom. Review decoded **{summary['decoded_video_frames']:,} video frames** with native recorded audio.",'','These recordings pin the checkpoint below, before the later Contra optimization. They expose the unresolved defects listed below and do not establish complete reference-game parity. The original-six audit is preserved in [world-1-1.md](world-1-1.md).','','[Video gallery and issue clips](../../build/playthroughs/expanded-review.html) · [Machine-readable audit](../../build/playthroughs/expanded-summary.json)','','| Character | Video | Frames | Enemies | Pickups | Lag frames | Overloaded sprite frames |','| --- | --- | ---: | ---: | ---: | ---: | ---: |']
 for r in records:
  md.append(f"| {r['character']} | [{r['route']}](../../build/playthroughs/{r['directory']}/playthrough.mp4) | {r['decoded_video_frames']:,} | {r['coverage']['enemies_defeated']} | {r['powerup_emergence_sequences']} | {r['lag_frames']} | {r['sprite_overload_frames']} |")
 md+=['','## Findings','', 'Five findings are confirmed; the brief wall-contact clip is a follow-up. Frame numbers refer to end-frame telemetry; rendered OAM changes can appear one captured frame later.','']
 for f in findings:
  md.append(f"- **{f['character']}, {f['seconds']:.2f}s / frame {f['frame']} ({f['status']}):** {f['description']} [Sequential frames](../../build/playthroughs/{f['image']}) · [Clip](../../build/playthroughs/{f['clip']})")
 md+=['','These are audit findings; the Contra optimization does not fix these character-specific defects.','','## Checks and limits','','Every captured frame was decoded. Automated checks found no stage-row vertical shifts, bad HUD split timing, missing **queued common SFX**, mushroom palette errors, or abnormal mushroom-emergence motion. Pit and Rygar raised no crouch/air-attack pose flags. PCM audio is present in all twelve captures. Common-SFX voice checks do not verify every source-specific sound or waveform identity.','','Manual inspection covered animation-context contact sheets, route milestones, item-emergence sequences and consecutive frames around findings. Bass has 22 pose/CHR timing candidates across the two routes; the inspected bank-transition sequence looks normal, so those candidates are not reported as confirmed corrupted graphics.','','Lag counts measure overloaded update frames; sprite counts measure hardware eight-sprites-per-scanline overload, not full-body disappearance. Native sprite limits remain enabled. The final stop callback is one frame beyond AVI capture; the trace and endpoint screenshot preserve that control check.','','The initial Ryu surface replay did not clear and was rejected. The accepted retry uses a fixed controller tail to traverse the flagpole approach. No level-clear recording writes game RAM or registers. Mesen starts with randomized RAM, so these are pinned successful recordings rather than a claim that uninitialized power-on state is identical on every replay.','','Each directory includes native AVI/PCM, a viewing MP4, manifest, hashes, actual controller inputs, read-only state/animation/PPU/APU traces, coverage events, and review sheets. Explicit injected stress fixtures used later for Contra are separate.','','## Checkpoint and reproduction','',f"MMC3 SHA-256: `{summary['rom_sha256']}`",'','```powershell','python tools/playthroughs/review.py build/playthroughs/expanded-qa-6-surface','python tools/playthroughs/summarize_expanded.py','```','', 'Reference comparison uses the pinned extracted Crossover 2 scripts under `reference/crossover2/extracted/scripts/com/smbc/characters/` and the generated pose mappings in `tools/reference/build_expanded_assets.py`.']
 (ROOT/'docs/qa/world-1-1-expanded.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 cards=[]
 for r in records:
  p=r['directory'];cards.append(f'<article><h2>{html.escape(r["character"])} — {r["route"]}</h2><video controls preload="none" src="{p}/playthrough.mp4"></video><p>{r["coverage"]["enemies_defeated"]} enemies · {r["powerup_emergence_sequences"]} pickups · {r["lag_frames"]} lag frames</p><a href="{p}/review-contact-sheet.png">Route sheet</a> · <a href="{p}/review.json">Audit</a> · <a href="{p}/native.avi">Native recording</a></article>')
 issues=''.join(f'<li><b>{f["character"]}, {f["seconds"]:.2f}s:</b> {html.escape(f["description"])} <a href="{f["image"]}">Frames</a> · <a href="{f["clip"]}">Clip</a></li>' for f in findings)
 page='<!doctype html><meta charset="utf-8"><title>World 1-1: added characters</title><style>body{background:#12151c;color:#e9ecf5;font:16px system-ui;margin:32px auto;max-width:1200px;padding:0 20px}a{color:#93c9ff}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px}article{background:#222837;padding:18px;border-radius:12px}video{width:100%;image-rendering:pixelated}h2{font-size:20px}li{margin:12px 0}code{overflow-wrap:anywhere}</style><h1>World 1-1 · six added characters</h1><p>12 complete controller-only runs · 57,084 decoded frames · native video and audio. This checkpoint predates the Contra performance fix.</p><h2>Findings</h2><ul>'+issues+'</ul><h2>Recordings</h2><main>'+''.join(cards)+'</main><p>Every-frame automated checks plus manual sequence/contact-sheet inspection. Unresolved findings remain; full website parity is not claimed.</p><p>ROM SHA-256 <code>'+summary['rom_sha256']+'</code></p>'
 (OUT/'expanded-review.html').write_text(page,encoding='utf-8')
 print(f'Published {len(records)} recordings, {summary["decoded_video_frames"]:,} decoded frames, {len(findings)} findings.')
if __name__=='__main__':main()
