"""Bind NS optimization to its exact ROM and actual output/regression evidence."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'build/verification/parodius-performance-ns'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
PUBLIC={'mmc3-oversized':'a03284f691e32be333976806462a5f65ee2d70e0659d0e404a6347b5a0d7bae7','mmc5-expanded':'58e44b4ef7324bf1bd093b92738a35d38df6aba55315133d410b444ad7f09c6e'}
def main():
 rom=QA/'candidate-v4.nes';digest=sha(rom);assert digest=='214b39daacdb0fb29590625f83912994fc73fb090235ac9f0f058bb938167f0c'
 parent=read(ROOT/'build/checkpoints/parodius-death-nr/manifest.json')
 rotation=read(QA/'rotation-v5.json');assert rotation['passed']and rotation['after_sha256']==digest and rotation['checker_sha256']==sha(ROOT/'tools/audit/check_parodius_draw_rotation.py')and rotation['actual_pooled_records']==662 and rotation['full_emitter_cases']==44560
 perf=read(QA/'performance-comparison.json');assert perf['passed']and perf['after_rom_sha256']==digest and perf['before_rom_sha256']==parent['rom_sha256']
 assert all(v['full-fleet']['actual_native_inputs_identical']and v['full-fleet']['after']['lagNmis']<v['full-fleet']['before']['lagNmis']for v in perf['variants'].values())
 routes=read(QA/'route-results.json');assert routes['passed']and routes['rom_sha256']==digest and len(routes['results'])==12
 hudchecks=0;replays={};labels=['SPD 2WY TAI RIP OPT RST OTR ','SPD RKT TAI 3WY OPT RST FLD ','SPD POT DBL SPR OPT RST BUB ']
 for mode in ('easy','hard'):
  for variant,name in enumerate(('octopus','twinbee','pentarou'),1):
   key=name+'-'+mode;out=QA/('replay-'+key+'-v4');discovery=QA/('discover-'+key+'-v4');m,d=read(out/'manifest.json'),read(discovery/'manifest.json')
   for item in (m,d):
    assert item['ROM_sha256']==digest and item['exit']==0 and item['controller_only']and not item['memory_writes']and item['result']['cleared']and item['result']['deaths']==0 and item['result']['failure']is None and set(item['result']['stage_entries'])=={'0-0','0-1'}
   assert m['fixed_replay']and not d['fixed_replay']and(out/'inputs.csv').read_bytes()==(discovery/'inputs.csv').read_bytes()
   for observer in ('chr_commit_observer.lua','parodius_render_observer.lua'):assert(ROOT/'tools/audit'/observer).read_text()in(out/'audit.lua').read_text()
   result=subprocess.run([sys.executable,str(ROOT/'tools/audit/check_parodius_render.py'),str(out)],capture_output=True,text=True);assert result.returncode==0,result.stderr
   body=read(out/'parodius-render-proof.json');assert body['passed']and body['fully_hidden_frames']==0 and body['trace_sha256']==sha(out/'parodius-body.csv')
   assert read(out/'chr-commit.json')['mismatched_frames']==0
   trace=list(csv.DictReader((out/'render.csv').open()));assert {r['behaviorVersion']for r in trace if r['mode']=='1'and r['engine']=='8'}=={str(int(mode=='hard'))}
   expected=bytes(36 if c==' 'else int(c)if c.isdigit()else ord(c)-55 for c in labels[variant-1]).hex()
   hud=[r for r in csv.DictReader((out/'parodius-hud.csv').open())if r['world']=='0'and r['level']=='0'and int(r['frame'])>=m['result']['stage_entries']['0-0']+60];assert len(hud)>30 and all(r['tiles']==expected for r in hud);hudchecks+=len(hud)
   replays[key]=dict(frames=m['result']['frames'],input_sha256=sha(out/'inputs.csv'),manifest_sha256=sha(out/'manifest.json'),render=body,chr=read(out/'chr-commit.json'),hud_samples=len(hud))
 entries=read(QA/'entry-v4/results.json');assert entries['rom_sha256']==digest and entries['identities']==37 and len(entries['results'])==37 and all(r['exit']==0 for r in entries['results'].values())
 suites={}
 for name,path in (('components','components-v4'),('bells','bells-v5'),('pickups','pickups-v4')):
  r=read(QA/path/'results.json');assert r['ROM_sha256']==digest and set(r['results'])=={'1','2','3'}and all(v['exit']==0 for v in r['results'].values());suites[name]=r
 assert sum(v['rendered_source_pixel_cases']for v in suites['pickups']['results'].values())==45
 baseline=read(QA/'bells-baseline-v2/results.json');assert baseline['ROM_sha256']==parent['rom_sha256']and all(v['exit']==0 for v in baseline['results'].values())
 for variant in (1,2,3):
  for path in ('bells-v5','bells-baseline-v2'):
   assert(ROOT/'tests/parodius-bells.lua').read_text()in(QA/path/str(variant)/'bells.lua').read_text()
 death=read(QA/'death-source-pixels-v4.json');assert death['passed']and death['rom_sha256']==digest and all(v['original_pixels_and_declared_colors']and v['all_intended_sprites_committed']and v['original_animation_instruction_differential']for v in death['variants'].values())
 roll=read(QA/'roll-components-v4/results.json');assert roll['ROM_sha256']==digest and roll['exit']==0
 native={n:sha(ROOT/n)for n in ('src/parodius_native.s','src/parodius_bell_native.s','src/parodius_data.inc','src/parodius_adapter.s','src/parodius_bells.s','chr/characters/parodius.chr')};assert all(parent['source_files'][n]==h for n,h in native.items())
 assert rom.read_bytes()[16+1024*1024:]==(ROOT/'build/checkpoints/parodius-death-nr/candidate.nes').read_bytes()[16+1024*1024:],'All CHR bytes unchanged'
 changes={n:sha(ROOT/n)for n,h in parent['source_files'].items()if n.startswith(('src/','chr/','audio/','inc/'))and sha(ROOT/n)!=h};assert set(changes)=={'src/parodius.s','src/parodius_render.s'};changes['src/parodius_fast_render.s']=sha(ROOT/'src/parodius_fast_render.s')
 for name,wanted in PUBLIC.items():assert sha(ROOT/'build'/f'smb-crossover-{name}.nes')==wanted
 controls={}
 for mapper,wanted in (('mmc3','97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4'),('mmc5','7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')):
  assert sha(QA/f'control-{mapper}.nes')==wanted;controls[mapper]=wanted
 report=dict(passed=True,rom_sha256=digest,parent='parodius-death-nr',source_changes=changes,unchanged_native_source=native,rotation=rotation,performance=perf,fixed_replays=replays,actual_hud_checks=hudchecks,entries=entries,suites=suites,death=death,roll=roll,unchanged_standard_roms=controls,unchanged_public_roms=PUBLIC,limits=['Private37-identity MMC5 optimization; full gear still lags substantially.','Body partial dropout, dedicated audio and remaining source fidelity remain open.','Production oversized-MMC3 and final every-character/every-physical-powerup matrix are unfinished.','Seeded CPU arenas do not establish campaign performance or physical-console60Hz.'])
 (QA/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,rom_sha256=digest,replays=len(replays),frames=sum(r['frames']for r in replays.values()),hud_samples=hudchecks,identities=37)))
if __name__=='__main__':main()
