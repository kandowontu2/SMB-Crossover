"""Candidate-specific ce635 MegaHard14 source/readiness; no native option."""
from pathlib import Path
import argparse,ast,copy,difflib,hashlib,json,shutil,sys
import final_megaproto_common_source_v2 as source
import final_megaproto_common_render_v3 as render
import final_megaproto_common_pharaoh_ready_v2 as pharaoh
from final_megaproto_common_ready_v5 import renderer_models,setup_models
from final_megaproto_common_collector_witness_v1 import interpret_events
from final_item_abilities_current731_prepare_v1 import protocol
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_run import lua
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from parodius_visibility_hud_static_startup_v1 import MOCK
D=source.D;R=source.R;CAND=D/'root-render-audio-palette-hud-union-v2';SHA='ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111'
OLD=D/'current0a-mega-common-pharaoh-ready-v2';FINAL=D/'current0a-mega-common-final-v1';RUN=R/'tools/audit/final_megaproto_common_ce635_run_v1.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))

def metadata(b,old):
 c=copy.deepcopy(old);c['ROM_sha256']=SHA
 for name in c['ram']:c['ram'][name]=address(b,name)
 def hook(name,previous):
  targets={'finish':'GameLoop','NmiReturn':'NonMaskableInterrupt','IrqReturn':'IrqScrollSplit','completion':'PostDmaMaskEnable'};target=targets.get(name,name);delta=int(b['syms'][target]['size'],0)-1 if name in['finish','NmiReturn','IrqReturn']else 3 if name=='completion'else 0;pos=location(b,target)+delta
  return dict(address=address(b,target)+delta,physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+len(previous['bytes'])]))
 c['hooks']={n:hook(n,h)for n,h in c['hooks'].items()};c['dma_protocol']=protocol(b)
 c['art']={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in c['art']};c.update(render.records(b))
 c['smc_fields']=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
 pos=location(b,'IrqScrollSplit');size=int(b['syms']['IrqScrollSplit']['size'],0);c['irq_scroll_stores']=[address(b,'IrqScrollSplit')+i for i in range(size-2)if b['raw'][pos+i:pos+i+3]==b'\x8d\x05\x20'];assert c['irq_scroll_stores']
 for q in c['cases']:
  i=16+q['item'];ptr=b['raw'][location(b,'InvNameLo')+i]+256*b['raw'][location(b,'InvNameHi')+i];bank=(location(b,'InvNameLo')-16)//8192;at=16+bank*8192+ptr%8192;q['hud_name']=list(b['raw'][at:at+7]);q['source_cost']=b['raw'][location(b,'InvCosts')+i];q['icon_bank']=b['raw'][location(b,'InvHudPhysicalBanks')+q['item']-1]
 diag=c['diagnostic'];diag['hooks']={n:hook(n,h)for n,h in diag['hooks'].items()};diag['ram']={n:address(b,n)for n in diag['ram']};diag['CHR_offset']=16+b['raw'][4]*16384;diag['CHR_pages']=(len(b['raw'])-diag['CHR_offset'])//1024
 assert c['identity']==old['identity']and c['cases']==old['cases']and c['effect_records']==old['effect_records']and c['native_brick']==old['native_brick']and c['native_chunk']==old['native_chunk']and c['buster_record']==old['buster_record']
 return c

def collector_models():
 n=OLD/'native';events=[json.loads(s)for s in(n/'events.jsonl').open()];cfg=json.loads((n/'config.json').read_text());summary=json.loads((n/'native-megaproto-common.json').read_text());original=json.dumps([events,cfg,summary],sort_keys=True);positive=interpret_events(events,cfg,summary);assert positive['actual_ordered_cases']==14 and json.dumps([events,cfg,summary],sort_keys=True)==original
 results=[]
 def reject(name,change):
  es=copy.deepcopy(events);ss=copy.deepcopy(summary);cc=copy.deepcopy(cfg);change(es,cc,ss)
  try:interpret_events(es,cc,ss);failed=False
  except AssertionError:failed=True
  assert failed,name;results.append(dict(name=name,expected='reject',passed=True))
 for case,c in enumerate(cfg['cases'],1):
  reject('missing-refusal-case'+str(case),lambda es,cc,ss,c=c:es.__setitem__(slice(None),[q for q in es if not(q['kind']=='ppu-frame-captured'and q['data']['name']==c['name']+'-exhaust-refusal')]))
 def field(es,kind,phase,case,path,value):
  q=next(q for q in es if q['case']==case and q['kind']==kind and q['phase']==phase)
  for key in path[:-1]:q=q[key]
  q[path[-1]]=value
 reject('accepted-empty-debit',lambda es,c,s:field(es,'actual-source-spend','empty',3,['data','accepted'],True))
 reject('wrong-empty-cost',lambda es,c,s:field(es,'actual-source-spend','empty',3,['data','cost'],8))
 reject('nonzero-empty-stock',lambda es,c,s:field(es,'gallery-phase','empty',3,['data','ammo'],4))
 reject('empty-emission',lambda es,c,s:es.append(dict(case=3,phase='empty',kind='actual-special-spawn')))
 reject('short-refusal-duration',lambda es,c,s:field(es,'gallery-phase','setup-pool',3,['update'],next(q['update']for q in es if q['case']==3 and q['kind']=='gallery-phase'and q['phase']=='empty')+24))
 reject('wrong-pool-policy-cost',lambda es,c,s:field(es,'actual-full-pool-special','pool',9,['data','cost'],0))
 reject('missing-pool-witness',lambda es,c,s:es.__setitem__(slice(None),[q for q in es if not(q['case']==5 and q['kind']=='actual-full-pool-refusal')]))
 reject('pool-not-complete',lambda es,c,s:field(es,'gallery-phase','pool',3,['data','shots',0,'type'],0))
 reject('cleanup-live-effect',lambda es,c,s:field(es,'gallery-phase','next',4,['data','shots',0,'type'],10))
 reject('cleanup-still-selected',lambda es,c,s:field(es,'gallery-phase','next',4,['data','selected'],2))
 reject('missing-funded-zero',lambda es,c,s:es.__setitem__(slice(None),[q for q in es if not(q['case']==3 and q['kind']=='actual-funded-debit-zero')]))
 reject('missing-funded-contact',lambda es,c,s:es.__setitem__(slice(None),[q for q in es if not(q['case']==3 and q['kind']=='actual-source-contact')]))
 reject('wrong-summary-case',lambda es,c,s:s['cases'][3]['q'].__setitem__('name','wrong'))
 assert all(q['emptyChecked']is False for q in summary['cases'])and json.dumps([events,cfg,summary],sort_keys=True)==original
 return dict(passed=True,positive_actual_0a_case_witnesses=14,negative_controls=len(results),results=results,raw_summary_flags_retained=[q['emptyChecked']for q in summary['cases']],input_objects_unchanged=True,original0a_native_proof=bind(n/'proof.json'),scope='Collector algorithm source qualification using immutable0a saved events. No combined-native coverage and no rewritten raw summary.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(CAND/'candidate.nes')==SHA;manifest=json.loads((CAND/'source-manifest.json').read_text());assert len(manifest)==871
 for name,h in manifest.items():assert sha(CAND/'source'/name)==h
 assert verify_manifest(OLD/'manifest.json')==995;verify_manifest(FINAL/'manifest.json');b=scoped_load(CAND/'candidate.nes');oldcfg=json.loads((OLD/'native/config.json').read_text());cfg=metadata(b,oldcfg);before=(OLD/'native/run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(oldcfg)+'\n';assert before.startswith(prefix);after='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+before[len(prefix):];assert after.split('\n',1)[1]==before.split('\n',1)[1]
 put(a.output/'config-refresh.json',dict(passed=True,old_ROM_sha256=oldcfg['ROM_sha256'],actual_ROM_sha256=SHA,old=oldcfg,current=cfg,only_configuration_prefix_changed=True,all14_cases_controller_seeds_body_caps_and_guards_literal=True))
 # Libraries execute fresh actual b/metadata. Only their output/path constants
 # are parameterized; no old native receipt or test predicate is retagged.
 source.SHA=SHA;render.SHA=SHA;pharaoh.SHA=SHA;pharaoh.B=CAND
 owner=source.source_cpu(b);put(a.output/'fresh-owner-controls.json',owner);rendered=render.compiled(b,cfg);put(a.output/'fresh-render-controls.json',rendered);release=pharaoh.compiled(b);put(a.output/'fresh-release-controls.json',release)
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 art=renderer_models(LuaRuntime,after,cfg,b,rendered);seeds=setup_models(LuaRuntime,after,cfg,b);callback=pharaoh.callback_models(LuaRuntime,before,after,cfg,b,release)if False else None
 # Both old/new candidate scripts already have the corrected capture. Reuse
 # the known pre-correction closure only for the required rejected model.
 fault=after.replace('local caseOwner=current;','local owner=current;').replace('current==caseOwner and','current==owner and');assert fault!=after;callback=pharaoh.callback_models(LuaRuntime,fault,after,cfg,b,release)
 put(a.output/'fresh-Lua-controls.json',dict(passed=True,art=art,complete_setup=seeds,full_release_callback=callback))
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'+after);assert rt.eval('#callbacks')==74 and rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535');rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 for frame in[1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
 assert rt.eval('#callbacks')==74;put(a.output/'collector-controls.json',collector_models())
 oldrunner=(R/'tools/audit/final_megaproto_common_oam_run_v1.py').read_text();newrunner=RUN.read_text();normalized=newrunner
 replacements=[('"""Exact combined ce635 MegaHard14 one-shot with ordered refusal witnesses."""','"""Profile-local E3 hardware-oracle successor; one granted native attempt only."""'),("SHA='"+SHA+"'","SHA='"+oldcfg['ROM_sha256']+"'"),('\nfrom final_megaproto_common_collector_witness_v1 import ordered_case_witnesses',''),("['naturalCleanup','poolPassed','selectionCleanup']","['naturalCleanup','emptyChecked','poolPassed','selectionCleanup']"),("  parts['ordered_case_witnesses']=ordered_case_witnesses(out,cfg,z)\n",'')]
 for new,old in replacements:assert normalized.count(new)==1;normalized=normalized.replace(new,old)
 assert normalized==oldrunner;put(a.output/'literal-predicates.json',dict(passed=True,all_other_runner_predicates_literal=True,only_collector_semantic_change='Reset terminal emptyChecked metadata replaced by explicit ordered typed witnesses; raw native flags retained.',reverse_replacements=[dict(new=x,old=y)for x,y in replacements],fixed_callbacks=74,dispatcher_last=True,three_inactive_frames=True,full_body_after_config_literal=True));(a.output/'collector.patch').write_text(''.join(difflib.unified_diff(oldrunner.splitlines(True),newrunner.splitlines(True),fromfile='frozen0a-runner',tofile='candidate-specific-ce635-ordered-witness-runner')),encoding='utf-8')
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(CAND/('candidate.'+ext),out/('candidate.'+ext))
 (out/'run.lua').write_text(after,encoding='utf-8');put(out/'config.json',cfg);shutil.copy2(OLD/'native/inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua');assert sha(out/'inherited-NMI-stack-APU-guards.lua')=='6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf'
 env=copy.deepcopy(json.loads((OLD/'proof.json').read_text())['environment']);runtime=a.output/'emulator';runtime.mkdir()
 for q in Path(env['emulator']).parent.iterdir():
  if q.is_file():shutil.copy2(q,runtime/q.name)
 env['emulator']=str(runtime/'Mesen.exe');env['user_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'MesenCore.dll')==env['core_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];put(a.output/'environment.json',env);put(a.output/'plans.json',cfg['cases'])
 files={Path(z['path'])for z in json.loads((OLD/'manifest.json').read_text())['bindings']}|{CAND/'candidate.nes',CAND/'candidate.dbg',CAND/'candidate.lbl',CAND/'candidate.map',CAND/'proof.json',CAND/'source-manifest.json',OLD/'proof.json',OLD/'manifest.json',FINAL/'proof.json',FINAL/'manifest.json',RUN,Path(__file__),Path('C:/Mesen2/settings.json'),Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__)};files.update(CAND/'source'/name for name in manifest)
 pending=[Path(__file__),RUN];seen=set()
 while pending:
  q=pending.pop()
  if q in seen:continue
  seen.add(q);files.add(q)
  for node in ast.walk(ast.parse(q.read_text(encoding='utf-8-sig'))):
   names=[node.module]if isinstance(node,ast.ImportFrom)else[z.name for z in node.names]if isinstance(node,ast.Import)else[]
   for name in names:
    if name:
     dep=R/'tools/audit'/(name.split('.')[0]+'.py')
     if dep.is_file():pending.append(dep)
 files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json');command='python -B tools/audit/final_megaproto_common_ce635_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,profile_local_OAM_encoding='attributeE3-v2',ROM_sha256=SHA,profile='mega-hard-common',mode_value=1,variant=0,maximum_cases=14,maximum_launches=1,maximum_owned_workers=1,retry=False,automatic_other_profiles=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,stable_command=command,lane='B',acquisition=False,all_prior_FALSEs_preserved=True,Proto_prepared=False));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=count,script_sha256=sha(out/'run.lua'),stable_command=command),indent=2))
if __name__=='__main__':main()
