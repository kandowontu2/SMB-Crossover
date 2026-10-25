"""Bind the private Parodius rendering repair to actual current evidence."""
from pathlib import Path
import csv,hashlib,json
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/parodius-render-nq'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NAMES=['octopus','twinbee','pentarou']
PUBLIC={'mmc3-oversized':'a03284f691e32be333976806462a5f65ee2d70e0659d0e404a6347b5a0d7bae7',
        'mmc5-expanded':'58e44b4ef7324bf1bd093b92738a35d38df6aba55315133d410b444ad7f09c6e'}


def main():
 rom=QA/'candidate-v3.nes';digest=sha(rom)
 assert digest=='c5f15fcd1bca72ca6a0787782f010342dbea99df8391c57a305be1addca8bf2e'
 results={};hud_checks=0
 labels=['SPD 2WY TAI RIP OPT RST OTR ','SPD RKT TAI 3WY OPT RST FLD ','SPD POT DBL SPR OPT RST BUB ']
 for mode in('easy','hard'):
  for variant,name in enumerate(NAMES,1):
   folder=QA/f'replay-{name}-{mode}-v3';discovery=QA/f'discover-{name}-{mode}-v3'
   m,d=read(folder/'manifest.json'),read(discovery/'manifest.json')
   for item in(m,d):
    assert item['ROM_sha256']==digest and item['exit']==0 and item['result']['cleared']
    assert item['result']['deaths']==0 and item['result']['failure']is None
    assert set(item['result']['stage_entries'])=={'0-0','0-1'}and item['controller_only']and not item['memory_writes']
    assert item['config']['variant']==variant and item['config']['behavior']==mode
   assert m['fixed_replay']and not d['fixed_replay']
   assert m['inputs_sha256']==sha(folder/'inputs.csv')and d['inputs_sha256']==sha(discovery/'inputs.csv')
   assert(folder/'inputs.csv').read_bytes()==(discovery/'inputs.csv').read_bytes()
   for observer in('chr_commit_observer.lua','parodius_render_observer.lua'):
    assert(ROOT/'tools/audit'/observer).read_text()in(folder/'audit.lua').read_text()
   chr_proof=read(folder/'chr-commit.json');body=read(folder/'parodius-render-proof.json')
   assert chr_proof['passed']and chr_proof['mismatched_frames']==0
   assert body['passed']and body['fully_hidden_frames']==0 and body['trace_sha256']==sha(folder/'parodius-body.csv')
   native=list(csv.DictReader((folder/'render.csv').open()))
   actual_modes={r['behaviorVersion']for r in native if r['mode']=='1'and r['engine']=='8'}
   assert actual_modes=={str(int(mode=='hard'))}
   expected=bytes(36 if c==' 'else int(c)if c.isdigit()else ord(c)-55 for c in labels[variant-1]).hex()
   hud=[r for r in csv.DictReader((folder/'parodius-hud.csv').open())if r['world']=='0'and r['level']=='0'and int(r['frame'])>=m['result']['stage_entries']['0-0']+60]
   assert len(hud)>30 and all(r['tiles']==expected for r in hud),'Actual HUD labels/glyphs'
   hud_checks+=len(hud)
   results[name+'_'+mode]=dict(manifest_sha256=sha(folder/'manifest.json'),inputs_sha256=m['inputs_sha256'],
        frame_count=m['result']['frames'],chr=chr_proof,render=body,hud_samples=len(hud),hud_sha256=sha(folder/'parodius-hud.csv'))
 before={}
 for name in NAMES:
  folder=QA/f'baseline-{name}';m=read(folder/'manifest.json');body=read(folder/'parodius-render-proof.json')
  assert m['ROM_sha256']==sha(ROOT/'build/checkpoints/chr-publication-np/candidate.nes')and m['exit']==0
  assert body['trace_sha256']==sha(folder/'parodius-body.csv')
  before[name]=dict(rom_sha256=m['ROM_sha256'],render=body,manifest_sha256=sha(folder/'manifest.json'))
 for name in('twinbee','pentarou'):
  assert results[name+'_easy']['render']['pixel_weighted_fraction']>.98
  assert results[name+'_easy']['render']['pixel_weighted_fraction']>before[name]['render']['pixel_weighted_fraction']
 death=read(QA/'death-final-v3/results.json');failed=read(QA/'death-repro-final/results.json')
 assert death['passed']and death['rom_sha256']==digest and set(death['results'])=={'1','2','3'}
 assert death['fixture_sha256']==failed['fixture_sha256']==sha(ROOT/'tests/parodius-death.lua')
 assert not failed['passed']and failed['results']['3']['proof']['mismatches']==49
 assert all(r['exit']==0 and r['proof']['mismatches']==0 and r['proof']['respawn']for r in death['results'].values())
 entries=read(QA/'entry-v3/results.json')
 assert entries['rom_sha256']==digest and entries['identities']==37 and len(entries['results'])==37 and all(r['exit']==0 for r in entries['results'].values())
 suites={}
 for suite in('components','bells','pickups'):
  result=read(QA/f'{suite}-v3/results.json')
  assert result['ROM_sha256']==digest and set(result['results'])=={'1','2','3'}and all(r['exit']==0 for r in result['results'].values())
  if suite=='pickups':assert sum(r['rendered_source_pixel_cases']for r in result['results'].values())==45
  suites[suite]=result
 roll=read(QA/'roll-components-v3/results.json');assert roll['ROM_sha256']==digest and roll['exit']==0
 art=read(QA/'packed-art-v2.json');manifest=read(ROOT/'reference/parodius-nes/art/packed/manifest.json')
 assert art['native_pose_pixels_equal']and art['CHR_sha256']==manifest['CHR_sha256']==sha(ROOT/'chr/characters/parodius.chr')
 assert sum(len(p['body_frames'])for p in manifest['pools'])==131
 assert len(art['cases'])==662
 standards={}
 for mapper,wanted in [('mmc3','97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4'),('mmc5','7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')]:
  assert sha(QA/f'standard-{mapper}.nes')==wanted;standards[mapper]=wanted
 for name,wanted in PUBLIC.items():assert sha(ROOT/'build'/f'smb-crossover-{name}.nes')==wanted
 parent=read(ROOT/'build/checkpoints/chr-publication-np/manifest.json')
 compiled={n:sha(ROOT/n)for n,wanted in parent['source_files'].items()if n.startswith(('src/','chr/','audio/','inc/'))and sha(ROOT/n)!=wanted}
 assert set(compiled)=={'src/vic_render.s','src/parodius_render.s','src/parodius_art.inc','chr/characters/parodius.chr'}
 core={n:sha(ROOT/n)for n in('src/parodius_native.s','src/parodius_bell_native.s','src/parodius_data.inc','src/parodius_adapter.s')}
 assert all(parent['source_files'][n]==v for n,v in core.items()),'Native movement/weapon adapter programs unchanged'
 canvas=Image.new('RGB',(1024,3*510),'#111c29');draw=ImageDraw.Draw(canvas)
 for i,name in enumerate(NAMES):
  for col,folder in enumerate((QA/f'baseline-{name}',QA/f'replay-{name}-easy-v3')):
   frame=folder/'frames/002592.png'
   draw.text((col*512+12,i*510+8),name.upper()+(' BEFORE / NP'if col==0 else' AFTER / NQ')+' / frame2592',fill='white')
   canvas.paste(Image.open(frame).convert('RGB').resize((512,480),Image.Resampling.NEAREST),(col*512,i*510+30))
 canvas.save(QA/'before-after.png')
 report=dict(passed=True,rom_sha256=digest,parent='chr-publication-np',source_changes=compiled,unchanged_native_source=core,
       fixed_replays=results,before=before,death=death,death_reproduced=failed,entries=entries,regressions=suites,roll=roll,
       source_art=dict(checks=len(art['cases']),body_poses=131,proof_sha256=sha(QA/'packed-art-v2.json'),CHR_sha256=art['CHR_sha256']),
       actual_hud_checks=hud_checks,unchanged_standard_roms=standards,unchanged_public_roms=PUBLIC,
       limits=['Remaining partial body dropout and substantial lag, especially Octopus.',
               'Death test repairs the existing common Gradius burst; original Parodius death-animation fidelity remains to finish.',
               'Dedicated audio, production oversized MMC3 port, final all-identity/all-powerup matrix remain open.'])
 (QA/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(passed=True,rom_sha256=digest,fixed_replays=len(results),video_frames=sum(r['frame_count']for r in results.values()),hud_samples=hud_checks)))


if __name__=='__main__':main()
