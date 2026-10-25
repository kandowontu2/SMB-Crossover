"""Bind the per-character death repair to its exact candidate and evidence."""
from pathlib import Path
import csv,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'build/verification/parodius-death-nr'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
PUBLIC={'mmc3-oversized':'a03284f691e32be333976806462a5f65ee2d70e0659d0e404a6347b5a0d7bae7','mmc5-expanded':'58e44b4ef7324bf1bd093b92738a35d38df6aba55315133d410b444ad7f09c6e'}


def main():
 rom=QA/'candidate-v2.nes';digest=sha(rom);assert digest=='2931163dd7d3c31f9a81776b16c45631a0abd2120abff4454833084825475590'
 death=read(QA/'native-death-proof-v7.json');runtime=read(QA/'death-v7/results.json')
 assert death['passed']and death['rom_sha256']==runtime['rom_sha256']==digest and runtime['passed']
 assert runtime['fixture_sha256']==sha(ROOT/'tests/parodius-native-death.lua')
 assert set(death['variants'])=={'1','2','3'}and [death['original_capture'][str(v)]['animation']for v in(1,2,3)]==[89,91,90]
 assert sum(v['frames']for v in death['variants'].values())==354
 assert all(v['original_pixels_and_declared_colors']and v['all_intended_sprites_committed']and v['original_animation_instruction_differential']for v in death['variants'].values())
 replays=read(QA/'replays-v3.json');assert replays['passed']and replays['ROM_sha256']==digest and len(replays['results'])==6
 modechecks=hudchecks=0
 labels=['SPD 2WY TAI RIP OPT RST OTR ','SPD RKT TAI 3WY OPT RST FLD ','SPD POT DBL SPR OPT RST BUB ']
 for mode in('easy','hard'):
  for variant,name in enumerate(('octopus','twinbee','pentarou'),1):
   out=QA/f'replay-{name}-{mode}-v3';disc=QA/f'discover-{name}-{mode}-v3';m,d=read(out/'manifest.json'),read(disc/'manifest.json')
   for item in(m,d):
    assert item['ROM_sha256']==digest and item['exit']==0 and item['controller_only']and not item['memory_writes']
    assert item['result']['cleared']and item['result']['deaths']==0 and item['result']['failure']is None and set(item['result']['stage_entries'])=={'0-0','0-1'}
   assert m['fixed_replay']and not d['fixed_replay']and(out/'inputs.csv').read_bytes()==(disc/'inputs.csv').read_bytes()
   chrproof=read(out/'chr-commit.json');body=read(out/'parodius-render-proof.json')
   assert chrproof['passed']and chrproof['mismatched_frames']==0 and body['passed']and body['trace_sha256']==sha(out/'parodius-body.csv')
   trace=list(csv.DictReader((out/'render.csv').open()));assert {r['behaviorVersion']for r in trace if r['mode']=='1'and r['engine']=='8'}=={str(int(mode=='hard'))};modechecks+=1
   expected=bytes(36 if c==' 'else int(c)if c.isdigit()else ord(c)-55 for c in labels[variant-1]).hex()
   hud=[r for r in csv.DictReader((out/'parodius-hud.csv').open())if r['world']=='0'and r['level']=='0'and int(r['frame'])>=m['result']['stage_entries']['0-0']+60]
   assert len(hud)>30 and all(r['tiles']==expected for r in hud);hudchecks+=len(hud)
 entries=read(QA/'entry-v2/results.json');assert entries['rom_sha256']==digest and entries['identities']==37 and len(entries['results'])==37 and all(r['exit']==0 for r in entries['results'].values())
 suites=read(QA/'regressions-v2/suites.json');assert suites['passed']and suites['rom_sha256']==digest
 for name in('components','bells','pickups'):
  r=read(QA/'regressions-v2'/name/'results.json');assert r['ROM_sha256']==digest and set(r['results'])=={'1','2','3'}and all(v['exit']==0 for v in r['results'].values())
 roll=read(QA/'roll-components-v2/results.json');assert roll['ROM_sha256']==digest and roll['exit']==0
 art=read(QA/'packed-art-v2.json');assert art['native_pose_pixels_equal']and len(art['cases'])==662 and art['CHR_sha256']==sha(ROOT/'chr/characters/parodius.chr')
 parent=read(ROOT/'build/checkpoints/parodius-render-nq/manifest.json')
 changed={n:sha(ROOT/n)for n,h in parent['source_files'].items()if n.startswith(('src/','chr/','audio/','inc/'))and sha(ROOT/n)!=h}
 assert set(changed)=={'src/vic_render.s','src/vic_adapter.s','src/parodius_render.s','src/parodius.s','chr/characters/parodius.chr'}
 changed.update({n:sha(ROOT/n)for n in('src/parodius_death.s','src/parodius_death_art.inc')})
 core={n:sha(ROOT/n)for n in('src/parodius_native.s','src/parodius_bell_native.s','src/parodius_data.inc','src/parodius_adapter.s')};assert all(parent['source_files'][n]==h for n,h in core.items())
 with zipfile.ZipFile(ROOT/'build/checkpoints/parodius-render-nq/source.zip')as z:old=z.read('chr/characters/parodius.chr')
 current=(ROOT/'chr/characters/parodius.chr').read_bytes();pages=[832+i for i in range(192)if old[i*1024:(i+1)*1024]!=current[i*1024:(i+1)*1024]];assert pages==[892,956,1020]
 for name,h in PUBLIC.items():assert sha(ROOT/'build'/f'smb-crossover-{name}.nes')==h
 report=dict(passed=True,rom_sha256=digest,parent='parodius-render-nq',source_changes=changed,unchanged_native_source=core,death=death,entries=entries,
  fixed_replays=replays,actual_mode_checks=modechecks,actual_hud_checks=hudchecks,suites=suites,roll=roll,source_art=dict(pooled_live_pose_comparisons=662,proof_sha256=sha(QA/'packed-art-v2.json'),changed_CHR_pages=pages),unchanged_public_roms=PUBLIC,
  limitations=['Private MMC5 checkpoint, not a release or full-roster campaign certificate.',
   'Pentarou yellow28 maps to shared yellow27; NPC palettes unchanged.',
   'SMB retains its120-update death lifecycle; original terminal-cursor wait and overall respawn duration are not copied.',
   'Octopus dropout, global lag, full fleets/Big forms, dedicated audio, production oversized MMC3 and final every-identity/every-powerup matrix remain open.'])
 (QA/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,rom_sha256=digest,fixed_replays=6,video_frames=sum(r['frames']for r in replays['results'].values()),death_DMA_frames=354,identities=37,hud_samples=hudchecks)))


if __name__=='__main__':main()
