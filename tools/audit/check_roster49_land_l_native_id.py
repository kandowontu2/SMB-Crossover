"""Fresh native Land lifecycle/source checks on the actual combined L ROMs."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-rush-h-a';S=V/'root49-components-land-l-ia/source';O=V/'root49-land-l-native-ie'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 assert not O.exists();O.mkdir()
 build=V/'root49-components-land-l-ia/build-review-ic.json';assert sha(build)=='2e9afeb6045b6f557881a4fc7b2040e4e0feea3ddf6229e99aa8741d40d67ffc'
 ao=H/'audio-freeze-ao.json';assert sha(ao)=='5733862cb1ac7f7dc3a1cc15062103aacb93ccbc219d6047e35505d30413380b';packet=read(ao)
 sp=importlib.util.spec_from_file_location('land_id_image',V/'agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+120000000<100000000000
 deps=['witness_f.lua','caller_x.lua','audio_x.lua','witness_aa.lua','caller_aa.lua','audio_ac.lua']
 for n in deps:assert sha(H/n)==packet['receipts'][n]['sha256']
 (O/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),combined_build_sha256=sha(build),parent_AO_sha256=sha(ao),dependencies={n:sha(H/n)for n in deps},workspace_before=used,phase_cap=120000000,reserve=30000000,global_cap=100000000000,scope='Fresh actual L images, exact frozen Lua fixture cores. Authored setup, controller pickup/Select/B and native AudioUpdate/ISR/register captures; no main install, fullroute or natural acquisition-distribution claim.'),indent=2)+'\n',encoding='utf-8')
 groups=[]
 for z in packet['reproduction']:
  assert workspace_bytes(O)+5000000+30000000<120000000
  mapper=z['mapper'];tag=z['tag'];parent=read(H/tag/'binding.json');cfg=dict(parent['config']);rom=S/'build'/f'smb-crossover-{mapper}.nes';image=im.Image(rom)
  dest=O/tag;dest.mkdir();(dest/'native-output').mkdir();cfg['out']=(dest/'native-output').as_posix()+'/'
  cfg['hooks']={'AudioUpdate':image.hook('AudioUpdate')};cfg['audioEnd']=image.hook('MegaManRushLandEnd')
  for name,label,delta in [('NMI','NonMaskableInterrupt',0),('NMIEnd','NonMaskableInterrupt','last'),('IRQ','IrqScrollSplit',0),('IRQEnd','IrqScrollSplit','last')]:cfg['hooks'][name]=image.hook(label,delta=delta)
  # Copy the bound parent wrapper's exact core sequence, changing CFG only.
  original=(H/tag/'component.lua').read_text(encoding='utf-8');split=original.index('\n')
  wrapper=dest/'component.lua';wrapper.write_text('CFG='+im.lua(cfg)+original[split:],encoding='utf-8')
  binding=dict(mapper=mapper,control=parent['control'],ROM_sha256=sha(rom),combined_source_preparation_sha256=sha(V/'root49-components-land-l-ia/preparation.json'),combined_build_sha256=sha(build),parent_binding_sha256=sha(H/tag/'binding.json'),config=cfg,wrapper_sha256=sha(wrapper),core_sequence_literal_parent_after_CFG=True,actual_semantics=z['actual_semantics'])
  (dest/'binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf-8')
  args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(dest/'host-output'),str(wrapper),str(rom),'--timeout','180'];(dest/'command.json').write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
  with(dest/'host.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
  group=dict(tag=tag,mapper=mapper,exit=q.returncode,binding_sha256=sha(dest/'binding.json'),rom_sha256=sha(rom));groups.append(group);(O/'partial-native.json').write_text(json.dumps(groups,indent=2)+'\n',encoding='utf-8');print('L_NATIVE',tag,q.returncode,flush=True)
  if q.returncode:raise RuntimeError('Retained actual L lifecycle failure '+tag)
 # Reuse the root's corrected-cycle caller verifier, with every original
 # oracle intact and output/ROM/input folders bound to the actual new run.
 source=V/'root49-rush-land-root-review-hx/review_ad.py.txt';code=source.read_text(encoding='utf-8')
 anchor='H=Path(__file__).resolve().parent;R=H.parents[2]';assert code.count(anchor)==1
 code=code.replace(anchor,anchor+'\nH=ROOT_NATIVE')
 old='rom=H/f"source-v/build/smb-crossover-{binding[\'mapper\']}.nes"';assert code.count(old)==1
 code=code.replace(old,'rom=ROOT_SOURCE/f"build/smb-crossover-{binding[\'mapper\']}.nes"')
 (O/'caller-review-id.py.txt').write_text(code,encoding='utf-8')
 for z in groups:
  tag=z['tag'];suffix='audio-ad-'+tag;previous=sys.argv;sys.argv=[str(H/'review_ad.py'),'--tag',tag,'--suffix',suffix];stream=io.StringIO();namespace={'__name__':'__main__','__file__':str(H/'review_ad.py'),'ROOT_OUTPUT':O,'ROOT_NATIVE':O,'ROOT_SOURCE':S}
  try:
   with contextlib.redirect_stdout(stream):exec(compile(code,str(H/'review_ad.py'),'exec'),namespace)
  finally:
   sys.argv=previous
   if 'ROOT_OLD_CPU'in namespace:namespace['m'].q.core.NesMPU=namespace['ROOT_OLD_CPU']
  (O/(tag+'-caller-review.log')).write_text(stream.getvalue(),encoding='utf-8')
  report=read(O/f'caller-review-{suffix}.json');assert report['status'].startswith('PASS_')and len(report['calls'])==43
  assert all(r['native_cycles']==r['instruction_cycles']for r in report['calls'])
  z.update(calls=43,actual_interrupts=sum(r['actual_interrupts']for r in report['calls']),actual_DEC_counts=[len(cpu.root_dec)for cpu in namespace['ROOT_CPUS']],caller_review_sha256=sha(O/f'caller-review-{suffix}.json'))
  print('L_CALLERS',tag,43,z['actual_interrupts'],flush=True)
 # The source image/trigger/release/priority/world/pause assertions consume
 # these new raw streams. Only H (data/output) is rebound; source CSV stays R.
 original=H/'review_ag.py';code=original.read_text(encoding='utf-8');anchor='H=Path(__file__).resolve().parent;R=H.parents[2]';assert code.count(anchor)==1
 code=code.replace(anchor,anchor+'\nH=ROOT_NATIVE');(O/'source-review-id.py.txt').write_text(code,encoding='utf-8');stream=io.StringIO()
 with contextlib.redirect_stdout(stream):exec(compile(code,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'ROOT_NATIVE':O})
 (O/'source-review-id.log').write_text(stream.getvalue(),encoding='utf-8')
 source_review=read(O/'source-audio-review-ag.json');assert source_review['status'].startswith('PASS_')and len(source_review['groups'])==12
 out=O/'review.json';result=dict(status='PASS_PRIVATE_L_12_FRESH_NATIVE_LAND_SOURCE_LIFECYCLE_GROUPS_AND_EXACT_516_CALLERS',script_sha256=sha(__file__),preparation_sha256=sha(O/'preparation.json'),groups=groups,source_review_sha256=sha(O/'source-audio-review-ag.json'),total_calls=sum(z['calls']for z in groups),total_attained_interrupts=sum(z['actual_interrupts']for z in groups),limits=['Exact fresh actualL caller registers/all10240RAM/orderedwrites/banks/correctednativecycles and attainedIRQs; no old ROM retag.','All frozen source image/retrigger/release/pause/world/character-switch/priority2stomp/priority3injury oracles run on actual L captures.','Authored setup and component producers only. No ordinary fullroute/natural pickup-distribution/fullweapon/finalmovie claim.','Land is combined with I/J/Arm/Rush/HU, but Ryu/HUD/visibleWater are not inL. MainHU remains installed.'],installed=False,goal_complete=False)
 result['receipts']={str(p.relative_to(O)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in O.rglob('*')if p.is_file()}
 out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');assert result['total_calls']==516
 print('L_LAND_REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
