"""Save tested Roll integration without publishing an unfinished roster build."""
from pathlib import Path
import datetime,gzip,hashlib,importlib.util,json,shutil,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/roll-roster-nn'
FINAL=ROOT/'build/checkpoints/roll-core-nn'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 assert not FINAL.exists(),'Preserve completed checkpoints'
 rom=QA/'smb-crossover-mmc5-roll-v18.nes';digest=sha(rom)
 assert digest=='e805bbec953fc5305fc3b3391961566f8b50bc925604916c4bea2229d93d6bdf'
 parent=read(ROOT/'build/checkpoints/parodius-bells-nm/manifest.json')
 public=read(ROOT/'build/checkpoints/mmc3-menu-nk/manifest.json')
 evidence={};art=read(QA/'art-proof.json');assets=read(ROOT/'reference/roll-mobile/art.json')
 assert art['passed'] and len(art['cases'])==68 and len(art['shots'])==10
 assert art['CHR_sha256']==assets['CHR_sha256']==sha(ROOT/'chr/characters/roll.chr')
 assert art['source_sha256']==sha(ROOT/'reference/new-roster-art/rollsheet_mobile1.png')
 assert all(len(assets['shot_records'][n])<=4 for n in (2,3))
 evidence['source_art']=art;evidence['roll_components']={};evidence['roll_rewards']={}
 for mode in ('easy','hard'):
  for suite,folder in (('components',f'final-components-{mode}-v18-r2'),('rewards',f'final-rewards-{mode}-v18')):
   path=QA/folder;result=read(path/'results.json');f=path/'build/verification'
   assert result['ROM_sha256']==digest and result['exit']==0 and result['behavior']==mode
   assert result['outlines']==(mode=='hard')
   assert result['test_sha256']==sha(ROOT/f'tests/roll-{suite}.lua')
   assert result['script_sha256']==sha(path/f'{suite}.lua')
   assert result['menu_sha256']==sha(ROOT/'tests/roll-menu.lua')
   assert result['observer_sha256']==sha(ROOT/'tools/audit/roll_render_observer.lua')
   proof=read(f/('roll-proof.json'if suite=='components'else'rewards-proof.json'))
   assert proof['passed']
   if suite=='components':
    assert proof['peakNormalShots']==3 and proof['charged'] and proof['headBumpNoShift'] and proof['adjacentBricksPreserved']
    assert proof['realInjuryAndLifeLoss'] and proof['physicalBlockReward'] and proof['physicalHealthAndEnergy']
    pixels=read(f/'roll-render-proof.json');assert pixels['passed'] and pixels['actual_rendered_body_frames']>700
    assert pixels['trace_sha256']==sha(f/'roll-body.csv')
    proof=dict(proof=proof,render=pixels)
   else:
    assert proof['nativeBlockRewards']==4 and proof['enemyCapsules']==4
    assert proof['starExpiredNaturally'] and proof['twoShotBrick'] and proof['chargedBrick']
   evidence['roll_'+suite][mode]=dict(result=result,details=proof)
 entries=read(QA/'final-entry-v18-r2/results.json')
 assert entries['rom_sha256']==digest and entries['identities']==37 and len(entries['results'])==37
 for name,row in entries['results'].items():
  assert row['exit']==0,name
  path=QA/'final-entry-v18-r2'/name.lower().replace(' ','-')
  assert row['script_sha256']==sha(path/'entry.lua')
  assert (path/'entry.lua').read_text().endswith((ROOT/'tests/full-roster-entry.lua').read_text())
 evidence['cold_entries']=entries;evidence['routes']={}
 for mode in ('easy','hard'):
  path=QA/f'final-replay-roll-{mode}-v18';r=read(path/'manifest.json')
  assert r['ROM_sha256']==digest and r['exit']==0 and r['fixed_replay']
  assert r['controller_only'] and not r['memory_writes']
  assert r['result']['cleared'] and r['result']['deaths']==0 and r['result']['failure']is None
  assert set(r['result']['stage_entries'])=={'0-0','0-1'}
  assert r['inputs_sha256']==sha(path/'inputs.csv')
  assert r['harness_sha256']==sha(path/'harness.lua') and r['policy_sha256']==sha(path/'policy.lua')
  assert (ROOT/'tools/audit/roll_render_observer.lua').read_text()in(path/'audit.lua').read_text()
  pixels=read(path/'roll-render-proof.json');assert pixels['passed'] and pixels['actual_rendered_body_frames']>2800
  assert pixels['trace_sha256']==sha(path/'roll-body.csv')
  evidence['routes'][mode]=dict(manifest=r,render=pixels,audit_sha256=sha(path/'audit.lua'),run_sha256=sha(path/'run.lua'))
 camera=read(QA/'camera-proof-v18.json');assert camera['passed'] and camera['ROM_sha256']==digest
 for mode,row in camera['modes'].items():
  assert row['camera_step_min']==0 and row['camera_step_max']<=2 and row['maximum_player_screen_x']<=112
  assert row['trace_sha256']==sha(QA/f'final-replay-roll-{mode}-v18/trace.csv')
 evidence['camera']=camera;evidence['parodius']={}
 validator=module('roll_pn_pixel_validator',ROOT/'tools/audit/check_parodius_pickups.py')
 for suite,proof_name in (('components','proof.json'),('bells','bell-proof.json'),('pickups','pickup-proof.json')):
  folder=QA/f'final-parodius-{suite}-v18';result=read(folder/'results.json')
  assert result['ROM_sha256']==digest and set(result['results'])=={'1','2','3'}
  assert all(row['exit']==0 for row in result['results'].values())
  details={}
  for variant in (1,2,3):
   f=folder/str(variant)/'build/verification';p=read(f/proof_name)
   if suite=='components':assert p['passed'] and p['missingPoses']==0
   elif suite=='bells':assert p['passed'] and p['redShots']==3 and p['paletteReads']>=64
   else:assert validator.pixels(f,p,variant)==15
   details[str(variant)]=p
  evidence['parodius'][suite]=dict(summary=result,details=details)
 evidence['standard_compatibility']={}
 for mapper,wanted in (('mmc3','97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4'),
                       ('mmc5','7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')):
  path=QA/f'final-standard-{mapper}-compatibility.nes';assert sha(path)==wanted
  evidence['standard_compatibility'][mapper]=read(path.with_suffix('.build.json'))
 m3=read(QA/'public-mmc3-entry/results.json')
 assert m3['ROM_sha256']==public['ROMs']['mmc3-oversized'] and set(m3['results'])=={'Lance','Bass'}
 assert all(row['exit']==0 for row in m3['results'].values())
 evidence['published_mmc3_entry']=m3
 names=set(parent['source_files'])
 for directory in ('src','chr','audio','inc','ports/mmc3-oversized','reference/roll-mobile'):
  names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/directory).rglob('*')if p.is_file()and p.suffix not in('.o','.pyc'))
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tools/audit').glob('*roll*')if p.is_file())
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tools/reference').glob('prepare_roll*.py'))
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tests').glob('roll-*.lua'))
 names.update(['reference/new-roster-art/rollsheet_mobile1.png','reference/new-roster-art/rollsheet_mobile2-unused.png',
               'tools/playthroughs/new_roster_run_nd.py','tools/playthroughs/new_roster_policy_nd.lua',
               'tools/audit/check_full_roster_entry.py','tools/audit/check_mmc3_oversized.py','tests/full-roster-entry.lua',
               'docs/qa/roll-mobile-private-implementation-2026-10-23.md','docs/qa/final-verification-plan-2026-10-23.md'])
 assert all((ROOT/n).is_file()for n in names)
 hashes={name:sha(ROOT/name)for name in sorted(names)}
 sys.path.insert(0,str(ROOT/'tools'));from playthroughs.roster_run import workspace_bytes
 assert workspace_bytes(ROOT)+3*sum((ROOT/n).stat().st_size for n in names)<30_000_000_000
 stage=QA/'snapshot-v18';assert not stage.exists();stage.mkdir()
 with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
  for name in sorted(names):archive.write(ROOT/name,name)
 source=stage/'source'
 with zipfile.ZipFile(stage/'source.zip')as archive:archive.extractall(source)
 output=stage/'roundtrip.nes'
 result=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
                        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(output)],
                       cwd=source,capture_output=True,text=True)
 (stage/'roundtrip.log').write_text(result.stdout+result.stderr)
 assert result.returncode==0 and sha(output)==digest,'Saved-source MMC5 rebuild differs'
 assert all(sha(ROOT/name)==value for name,value in hashes.items()),'Source changed during snapshot'
 for mapper,value in public['ROMs'].items():assert sha(ROOT/'build'/('smb-crossover-'+mapper+'.nes'))==value
 FINAL.mkdir();shutil.copy2(stage/'source.zip',FINAL/'source.zip')
 for suffix in('.nes','.lbl','.map','.dbg'):
  path=rom.with_suffix(suffix)
  if suffix=='.dbg':(FINAL/'candidate.dbg.gz').write_bytes(gzip.compress(path.read_bytes(),mtime=0))
  else:shutil.copy2(path,FINAL/('candidate'+suffix))
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PRIVATE_ROLL_CORE_WITH_OPEN_PERFORMANCE_AND_SOURCE_AUDIO',
             parent_checkpoint='parodius-bells-nm',identities=37,ROM_sha256=digest,source_zip_sha256=sha(FINAL/'source.zip'),
             source_bundle_rebuild_exact=True,source_files=hashes,evidence=evidence,
             limitations=['Lag NMIs and extensive partial sprite dropout remain; decoder pixel checks do not establish whole-scene visibility or60Hz.',
                          'Roll uses documented SMB adaptations; exact mobile timing/health/audio and refill presentation remain unverified.',
                          'Dedicated source music/audio and production oversized-MMC3 Roll/Parodius integration remain unfinished.',
                          'The completed final roster still needs every-character1-1 and every-powerup verification.',
                          'Other profiles need a CHR publication/skipped-drawing audit.',
                          'Published33-identity MMC3/MMC5 ROMs are unchanged.'])
 (FINAL/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 assert workspace_bytes(ROOT)<30_000_000_000
 print(json.dumps(dict(checkpoint=str(FINAL),ROM_sha256=digest,source_bundle_rebuild_exact=True,published=False)))

if __name__=='__main__':main()
