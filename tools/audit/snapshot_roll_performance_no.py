"""Preserve the exact tested private Roll performance candidate and its source."""
from pathlib import Path
import datetime,gzip,hashlib,json,shutil,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/roll-performance-no'
FINAL=ROOT/'build/checkpoints/roll-performance-no'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())


def main():
 assert not FINAL.exists(),'Do not replace an existing checkpoint'
 rom=QA/'roll-empty-v4.nes';digest=sha(rom)
 assert digest=='14b0955db88871be563216fb4ccbff735393ad81cb5f715af54fc45c0a1080ae'
 parent=read(ROOT/'build/checkpoints/roll-core-nn/manifest.json');public=read(ROOT/'build/checkpoints/mmc3-menu-nk/manifest.json')
 evidence={}
 for key,name in(('art','repacked-art-proof.json'),('renderer','renderer-v4.json'),('broad_phases','empty-space-v4-exhaustive.json'),('performance','performance-proof.json'),('routes','camera-route-proof.json')):
  proof=read(QA/name);assert proof['passed'],key
  if 'rom_sha256'in proof:assert proof['rom_sha256']==digest
  if 'ROM_sha256'in proof:assert proof['ROM_sha256']==digest
  evidence[key]=dict(proof=proof,sha256=sha(QA/name))
 art=evidence['art']['proof'];assert len(art['cases'])==68 and len(art['shots'])==10 and art['previous_body_pixels_identical']
 assert art['previous_source_sha256']==sha(ROOT/'build/checkpoints/roll-core-nn/source.zip')
 assert art['CHR_sha256']==sha(ROOT/'chr/characters/roll.chr')
 assert evidence['renderer']['proof']['checks']==5904
 assert evidence['broad_phases']['proof']['terrain_cases']==98304 and evidence['broad_phases']['proof']['enemy_cases']==14400
 performance=evidence['performance']['proof']['measurements']
 assert performance['after']['rom_sha256']==digest and performance['before']['rom_sha256']==sha(ROOT/'build/checkpoints/roll-core-nn/candidate.nes')
 for label,folder in(('before','before-final'),('after','empty-easy-v4')):
  assert performance[label]['calls_sha256']==sha(QA/folder/'build/verification/roll-performance-calls.csv')
  assert performance[label]['frames_sha256']==sha(QA/folder/'build/verification/roll-performance-frames.csv')
 evidence['roll_arenas']={}
 for mode in('easy','hard'):
  for suite in('components','rewards'):
   name=f'empty-{mode}-v4'if suite=='components'else f'rewards-{mode}-v4';path=QA/name;result=read(path/'results.json')
   assert result['ROM_sha256']==digest and result['exit']==0 and result['behavior']==mode and result['outlines']==(mode=='hard')
   for field,file in(('test_sha256',ROOT/f'tests/roll-{suite}.lua'),('menu_sha256',ROOT/'tests/roll-menu.lua'),('observer_sha256',ROOT/'tools/audit/roll_render_observer.lua')):assert result[field]==sha(file)
   assert result['script_sha256']==sha(path/f'{suite}.lua')
   proof=read(path/'build/verification'/('roll-proof.json'if suite=='components'else'rewards-proof.json'));assert proof['passed']
   if suite=='components':
    pixels=read(path/'build/verification/roll-render-proof.json');assert pixels['passed']and pixels['actual_rendered_body_frames']>700
    assert pixels['trace_sha256']==sha(path/'build/verification/roll-body.csv')
   else:assert proof['nativeBlockRewards']==4 and proof['enemyCapsules']==4 and proof['starExpiredNaturally']and proof['twoShotBrick']and proof['chargedBrick']
   evidence['roll_arenas'][mode+'_'+suite]=dict(result=result,proof=proof)
 entries=read(QA/'entry-v4/results.json');assert entries['rom_sha256']==digest and entries['identities']==37 and len(entries['results'])==37
 for name,result in entries['results'].items():
  path=QA/'entry-v4'/name.lower().replace(' ','-')/'entry.lua';assert result['exit']==0 and result['script_sha256']==sha(path)
  assert path.read_text().endswith((ROOT/'tests/full-roster-entry.lua').read_text())
 evidence['entries']=entries;evidence['fixed_replays']={}
 for mode,folder in(('easy','replay-easy-v4-r2'),('hard','replay-hard-v4')):
  path=QA/folder;manifest=read(path/'manifest.json');pixels=read(path/'roll-render-proof.json')
  assert manifest['ROM_sha256']==digest and manifest['exit']==0 and manifest['fixed_replay']and manifest['controller_only']and not manifest['memory_writes']
  assert manifest['result']['cleared']and manifest['result']['deaths']==0 and manifest['result']['failure']is None
  assert set(manifest['result']['stage_entries'])=={'0-0','0-1'}
  assert manifest['inputs_sha256']==sha(path/'inputs.csv')and pixels['trace_sha256']==sha(path/'roll-body.csv')and pixels['passed']
  assert(path/'inputs.csv').read_bytes()==(QA/f'route-{mode}-v4/inputs.csv').read_bytes()
  assert(ROOT/'tools/audit/roll_render_observer.lua').read_text()in(path/'audit.lua').read_text()
  assert(ROOT/'tools/audit/roll_performance_observer.lua').read_text()in(path/'audit.lua').read_text()
  evidence['fixed_replays'][mode]=dict(manifest=manifest,pixels=pixels,audit_sha256=sha(path/'audit.lua'),run_sha256=sha(path/'run.lua'))
 evidence['parodius']={}
 for suite in('components','bells','pickups'):
  result=read(QA/f'parodius-{suite}-v4/results.json');assert result['ROM_sha256']==digest and set(result['results'])=={'1','2','3'}
  assert all(row['exit']==0 for row in result['results'].values())
  if suite=='pickups':assert all(row['rendered_source_pixel_cases']==15 for row in result['results'].values())
  evidence['parodius'][suite]=result
 for mapper,wanted in(('mmc3','97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4'),('mmc5','7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')):
  assert sha(QA/f'standard-{mapper}.nes')==wanted
 for mapper,wanted in public['ROMs'].items():assert sha(ROOT/'build'/f'smb-crossover-{mapper}.nes')==wanted
 names=set(parent['source_files'])
 for directory in('src','chr','audio','inc','ports/mmc3-oversized','reference/roll-mobile'):
  names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/directory).rglob('*')if p.is_file()and p.suffix not in('.o','.pyc'))
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tools/audit').glob('*roll*')if p.is_file())
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'tools/reference').glob('*roll*.py'))
 names.update(['tools/playthroughs/new_roster_run_nd.py','docs/qa/roll-mobile-private-implementation-2026-10-23.md','smb1base-mmc5-expanded.cfg'])
 hashes={name:sha(ROOT/name)for name in sorted(names)}
 sys.path.insert(0,str(ROOT/'tools'));from playthroughs.roster_run import workspace_bytes
 assert workspace_bytes(ROOT)+sum((ROOT/n).stat().st_size for n in names)+80_000_000<30_000_000_000
 stage=QA/'snapshot-v4';assert not stage.exists();stage.mkdir()
 with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name in sorted(names):z.write(ROOT/name,name)
 source=stage/'source'
 with zipfile.ZipFile(stage/'source.zip')as z:z.extractall(source)
 rebuilt=stage/'roundtrip.nes'
 process=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(rebuilt)],cwd=source,capture_output=True,text=True)
 (stage/'rebuild.log').write_text(process.stdout+process.stderr);assert process.returncode==0 and sha(rebuilt)==digest,'Exact source-bundle rebuild'
 assert all(sha(ROOT/name)==value for name,value in hashes.items())
 FINAL.mkdir();shutil.copy2(stage/'source.zip',FINAL/'source.zip')
 for suffix in('.nes','.lbl','.map'):shutil.copy2(rom.with_suffix(suffix),FINAL/('candidate'+suffix))
 (FINAL/'candidate.dbg.gz').write_bytes(gzip.compress(rom.with_suffix('.dbg').read_bytes(),mtime=0))
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PRIVATE_ROLL_PERFORMANCE_WITH_OPEN_GLOBAL_LAG_DROPOUT_AND_AUDIO',parent_checkpoint='roll-core-nn',identities=37,rom_sha256=digest,source_zip_sha256=sha(FINAL/'source.zip'),source_bundle_rebuild=dict(exact=True,rom_sha256=sha(rebuilt)),source_files=hashes,evidence=evidence,limitations=['Private MMC5 only; published33-identity builds remain unchanged.','Rapid-fire arena improves; full-level lag and partial sprite dropout remain.','Dedicated audio, source fidelity details and production oversized MMC3 integration remain.','Final every-character1-1 and every-powerup matrix still required.'])
 (FINAL/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
 (QA/'checkpoint.json').write_text(json.dumps(dict(checkpoint=str(FINAL),rom_sha256=digest,source_zip_sha256=report['source_zip_sha256'],goal_complete=False),indent=2)+'\n')
 assert workspace_bytes(ROOT)<30_000_000_000
 print(json.dumps(dict(checkpoint=str(FINAL),rom_sha256=digest,source_zip_sha256=report['source_zip_sha256'])))


if __name__=='__main__':main()
