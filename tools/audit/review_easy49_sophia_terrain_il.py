"""Static closure for private IK; native caller and union admission separate."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
D=V/'root49-sophia-source-terrain-ik';P=V/'root49-sophia-source-body-hs';F=V/'root49-sophia-source-terrain-if'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))
G=V/'ryu49-head-status-bridge-g';sys.path.insert(0,str(G))
spec=importlib.util.spec_from_file_location('terrain_static_bus',G/'check.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)


def segment(im,name):
 s=next(x for x in im.segs.values()if x['name']==name)
 return s,im.raw[s['ooffs']:s['ooffs']+s['size']]


def main():
 out=D/'static-il.json';assert not out.exists()
 report=dict(status='RUNNING',script_sha256=sha(__file__),preparation=rec(D/'preparation.json'),maps=[],main_changed=False,accepted_release=False)
 try:
  prep=json.loads((D/'preparation.json').read_text());assert len(prep['source_sha256'])==445
  assert all(sha(D/'source'/n)==h for n,h in prep['source_sha256'].items())
  fp=json.loads((F/'preparation.json').read_text())
  changes=[n for n,h in fp['source_sha256'].items()if prep['source_sha256'][n]!=h]
  assert sorted(changes)==['src/collision.s','src/sophia_source_terrain.s'],changes
  report['changes_from_IF']=changes
  for n,status in [('compiled-ig.json','PASS_COMPILED_NORMAL_SOURCE_TERRAIN_FIXTURES'),('brick-none-ik.json','PASS_COMPILED_SOURCE_BRICK_NONE_COINS_AND_ORIGINAL96')]:
   assert json.loads((D/n).read_text())['status']==status
  report['compiled_checks']=[rec(D/n)for n in ['compiled-ig.json','brick-none-ik.json']]
  for mapper,baseline in [('mmc3','0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'),('mmc5','34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd')]:
   filename='smb-crossover-'+mapper+'.nes'
   old=g.Image(P/'source/build'/filename);im=g.Image(D/'source/build'/filename);prior=g.Image(F/'source/build'/filename)
   assert all(im.ram[n]==a for n,a in old.ram.items())
   assert old.raw[:16]==im.raw[:16]and old.raw[16+524288:]==im.raw[16+524288:]
   assert sha(D/'source/build'/('smb-crossover-'+mapper+'-baseline.nes'))==baseline
   unchanged={}
   for s in old.segs.values():
    name=s['name']
    if not s.get('size')or'ooffs'not in s:continue
    if any(t in name for t in ['AUDIO','MUSIC','DPCM','SMCCODE'])and name!='REMAINING_AUDIO':
     new,b=segment(im,name);a=old.raw[s['ooffs']:s['ooffs']+s['size']]
     assert (s['start'],s['size'],s['ooffs'])==(new['start'],new['size'],new['ooffs']),('Segment location',mapper,name)
     assert a==b,('Segment bytes',mapper,name)
     unchanged[name]=dict(bytes=len(a),sha256=hashlib.sha256(a).hexdigest())
   resident={}
   for name in ['NonMaskableInterrupt','IrqScrollSplit','MegaManVineAnchor']:
    assert im.hook(name)==old.hook(name),(mapper,name)
    resident[name]=im.hook(name)
   old_collision,before=segment(prior,'COLLISION');new_collision,after=segment(im,'COLLISION')
   assert before==after and old_collision['start']==new_collision['start'],('Crossover-disabled guards altered native cross collision',mapper)
   # The corrected cold bank11 code cannot disturb these IF-tested producers.
   procedures={}
   for name in ['MegaManSpringVelocityModes','CrossoverPatchStatusName','RyuSourceBodyBox','RyuSourceBodyPlatformBasic','RyuSourceBodyPlatformOverlap','RyuSourceBodyPlatformPrepare','RyuSourceBodyPlatformFinish']:
    a=prior.hook(name);b=im.hook(name);size=prior.sym(name)['size']
    assert a==b and size==im.sym(name)['size'],(mapper,name,'layout')
    aa=prior.raw[a['rom_offset']:a['rom_offset']+size];bb=im.raw[b['rom_offset']:b['rom_offset']+size]
    assert aa==bb,(mapper,name,'bytes')
    procedures[name]=dict(bytes=size,sha256=hashlib.sha256(bb).hexdigest(),hook=b)
   a=prior.hook('EasyLinkFirebarStart');b=im.hook('EasyLinkFirebarStart')
   assert a==b and prior.raw[a['rom_offset']:a['rom_offset']+184]==im.raw[b['rom_offset']:b['rom_offset']+184]
   artifacts={e:rec(D/'source/build'/('smb-crossover-'+mapper+'.'+e))for e in ['nes','lbl','map','dbg']}
   report['maps'].append(dict(mapper=mapper,artifacts=artifacts,baseline=rec(D/'source/build'/('smb-crossover-'+mapper+'-baseline.nes')),all_old_RAM_names=len(old.ram),header_and_CHR_literal=True,audio_DPCM_SMC_literal=unchanged,resident_continuations=resident,IF_collision_segment_literal=True,unchanged_IF_producers=procedures,Link_H_leaf184_literal=True))
  checkpoint=R/'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json';main=json.loads(checkpoint.read_text());assert len(main['source_hashes'])==442
  for n,h in main['source_hashes'].items():assert sha(R/n)==h,n
  for build in main['builds']:
   for a in build['artifacts'].values():assert sha(R/a['path'])==a['sha256'],a['path']
  report.update(status='PASS_PRIVATE_IK_STATIC_BASELINES_AUDIO_RAM_AND_RESIDENT_CONTINUATIONS',current_GQ_checkpoint=rec(checkpoint),main442_sources8_artifacts_exact=True,qualification='Compiled components and literal relocation only. Actual full native head/side/canonical callers, contextual E merge and final fresh routes still required. Corner calcAxis/fullfootspan/rotated source anchors/vine/firebar positive bitmap parity remain open.')
 except Exception as exc:report.update(status='FAIL_RETAINED',error=str(exc));raise
 finally:out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],sources=445,main_GQ_unchanged=True)))


if __name__=='__main__':main()
