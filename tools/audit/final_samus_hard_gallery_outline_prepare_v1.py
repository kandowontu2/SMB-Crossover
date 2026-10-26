"""Narrow outline-RAM observer successor; exact old mechanics, no native run."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,shutil,sys
from final_samus_hard_gallery_source_v1 import SHA,PARENT,ROOT,D
from final_samus_hard_gallery_prepare_v2 import compose,phase_models
from final_samus_hard_gallery_outline_controls_v2 import controls
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_run import lua
from final_item_abilities_static_prepare_v2 import core_tests,old_core
from final_item_abilities_current731_prepare_v1 import dma_mocks
from parodius_visibility_hud_static_startup_v1 import MOCK
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
OLD=D/'current3b112-samus-hard-gallery-ready-v2'
NEG=D/'current3b112-samus-hard-gallery-negative-v1'

def observer_models(LuaRuntime,script,cfg,compiled):
 pre=MOCK+'''
 L={};OUTPUT='mock/';mem={};rom={};CB=13;RETURNBANK=0
emu.memType.nesPrgRom=6
emu.read=function(a,t)if t==6 then return rom[a]or 0 else return mem[a]or 0 end end
emu.write=function()error('Observer never mutates emulated state')end
emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end
emu.convertAddress=function(a)
 local b=a>=0xe000 and 127 or a>=0xc000 and CB or a>=0xa000 and 10 or a>=0x8000 and 4 or RETURNBANK
 return{address=b*8192+a%8192}
end
'''
 export='''
entered=true;phase='source-observer-model'
function TEST_CONTEXT()drawContext={kind='body'}end
function TEST_FILTERED()return drawContext.filtered~=nil end
function TEST_ENTRY()local h=C.hooks.PlayerRemoveOutlines;state['cpu.pc']=h.address;for _,q in ipairs(callbacks)do if q.kind==2 and q.lo==h.address and q.hi==h.address then q.fn()end end end
function TEST_RETURN()state['cpu.pc']=0x16e;callbacks[#callbacks].fn(0x16e)end
function TEST_RENDER()local h=C.hooks.MetaspriteRenderLoop;state['cpu.pc']=h.address;for _,q in ipairs(callbacks)do if q.kind==2 and q.lo==h.address and q.hi==h.address then q.fn()end end end
'''
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(pre+script+export);count=rt.eval('#callbacks')
 rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 mem,rom=rt.globals().mem,rt.globals().rom
 for h in cfg['hooks'].values():
  for i,v in enumerate(h['bytes']):mem[h['address']+i]=v
 for q in cfg['body_records'].values():
  for i,v in enumerate(q['bytes']):rom[q['bank']*8192+q['address']%8192+i]=v
 def setup(z,body):
  rt.globals().CB=z['source_bank'];rt.globals().RETURNBANK=0
  rt.execute("state['cpu.sp']=243;TEST_CONTEXT()")
  mem[500]=0x6d;mem[501]=1
  for n,v in [('R0',z['source_pointer']&255),('R1',z['source_pointer']>>8)]:mem[cfg['ram'][n]]=v
  for i,v in enumerate(body['bytes']):mem[body['pointer']+i]=v
 def output(body):
  mem[cfg['ram']['R0']]=body['pointer']&255;mem[cfg['ram']['R1']]=body['pointer']>>8
  rt.execute("state['cpu.sp']=245")
 def attempt(fn,want):
  try:fn();got=True
  except Exception:got=False
  assert got==want,(got,want)
 results=[]
 for q in compiled['cases']:
  if not q['filters']:continue
  for i,label in [(0,'uncached'),(1,'cached')]:
   f=q['filters'][i];body=q['body']if i==0 else q['repeated_body'];setup(f,body);rt.globals().TEST_ENTRY();output(body);rt.globals().TEST_RETURN();assert rt.globals().TEST_FILTERED();rt.globals().TEST_RENDER()
   results.append(dict(kind='actual-filter-'+label,mode=q['mode'],power=q['power'],owned=q['owned'],face=q['face'],pose=q['pose'],passed=True))
 q=next(q for q in compiled['cases']if q['mode']==1 and q['owned']==0 and q['face']==1 and q['pose']=='standing'and q['outlines_off'])
 f=q['filters'][0];body=q['body']
 for kind in['wrong-RAM-pointer','modified-header','modified-tile','wrong-source-pointer','modified-immutable-source','wrong-return-C','wrong-return-SP','wrong-return-bank']:
  setup(f,body)
  if kind=='wrong-source-pointer':mem[cfg['ram']['R0']]=(f['source_pointer']+1)&255;attempt(rt.globals().TEST_ENTRY,False)
  elif kind=='modified-immutable-source':
   at=f['source_bank']*8192+f['source_pointer']%8192+1;v=rom[at];rom[at]=v^1;attempt(rt.globals().TEST_ENTRY,False);rom[at]=v
  else:
   rt.globals().TEST_ENTRY();output(body)
   if kind=='wrong-RAM-pointer':mem[cfg['ram']['R0']]=(body['pointer']+1)&255;attempt(rt.globals().TEST_RETURN,False)
   elif kind in['modified-header','modified-tile']:
    at=body['pointer']+(0 if kind=='modified-header'else 1);mem[at]=mem[at]^1;attempt(rt.globals().TEST_RETURN,False)
   elif kind=='wrong-return-C':rt.globals().CB=14;attempt(rt.globals().TEST_RETURN,False)
   else:
    if kind=='wrong-return-SP':rt.execute("state['cpu.sp']=244")
    else:rt.globals().RETURNBANK=1
    rt.globals().TEST_RETURN();assert not rt.globals().TEST_FILTERED()
    rt.execute("state['cpu.sp']=245");rt.globals().RETURNBANK=0;rt.globals().TEST_RETURN();assert rt.globals().TEST_FILTERED()
  results.append(dict(kind=kind,expected='reject/defer',passed=True))
 assert rt.eval('#callbacks')==count
 return dict(passed=True,source_only=True,models=results,positive_models=96,negative_models=8,callbacks=count,no_runtime_registration=True,emulated_writes=0)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 oldproof=json.loads((OLD/'proof.json').read_text());assert sha(OLD/'proof.json')=='68ba89d30f24a873b8af7cf9e782c9a53cc899b099a57b47a65dcf4975822d30';verify_manifest(OLD/'manifest.json');verify_manifest(NEG/'manifest.json')
 old=Path(oldproof['output']);assert json.loads((old/'proof.json').read_text())['passed']is False
 cfg=json.loads((old/'config.json').read_text());oldcfg=copy.deepcopy(cfg);b=scoped_load(PARENT/'candidate.nes');assert sha(PARENT/'candidate.nes')==SHA
 n='PlayerRemoveOutlines';pos=location(b,n);cfg['hooks'][n]=dict(address=address(b,n),physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+3]));cfg['ram']['OutlinePoseBuffer']=address(b,'OutlinePoseBuffer')
 original=(ROOT/'tools/audit/final_samus_hard_gallery_native_v1.lua').read_text();successor=(ROOT/'tools/audit/final_samus_hard_gallery_native_v2.lua').read_text()
 # Only the three explicit observer regions differ. Runtime, mechanics,
 # seeds, controllers, assertions and output schema remain byte-exact.
 oldscript,oldguards=compose(oldcfg);assert oldscript==(old/'run.lua').read_text()
 script,guards=compose(cfg);assert script.count(original)==1;script=script.replace(original,successor)
 reverse=script.replace(successor,original);assert reverse==compose(cfg)[0]
 checkcfg=copy.deepcopy(cfg);del checkcfg['hooks'][n];del checkcfg['ram']['OutlinePoseBuffer'];assert checkcfg==oldcfg and guards==oldguards
 patch=''.join(difflib.unified_diff(original.splitlines(True),successor.splitlines(True),fromfile='native_v1.lua',tofile='native_v2.lua'));(a.output/'observer.patch').write_text(patch,encoding='utf-8')
 put(a.output/'observer-delta.json',dict(passed=True,changes=['Source-qualified PlayerRemoveOutlines entry/actual fixed-return callback authenticates immutable ROM source, filters only attr bit4-tagged parts, admits only actual OutlinePoseBuffer slots0/32/64/96 and exact header/bytes.','Body render admission retains all existing source-pointer/bank/byte checks, now reading source-derived filtered records from witnessed RAM when that genuine owner ran.','One startup callback and one read-only RAM address metadata entry added. No native seed/input/controller/deadline/effect/CHR/SMC/stack/output/schema change.'],config_reverse_exact=True,all_other_script_bytes_reverse_exact=True,original_guard_sha256=sha(old/'inherited-NMI-stack-APU-guards.lua')))
 compiled=controls(b,cfg['body_records']);put(a.output/'compiled-outline-controls.json',compiled)
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(old/('candidate.'+ext),out/('candidate.'+ext))
 put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');(out/'inherited-NMI-stack-APU-guards.lua').write_text(guards,encoding='utf-8')
 assert sha(out/'inherited-NMI-stack-APU-guards.lua')=='6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf'
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 models=observer_models(LuaRuntime,script,cfg,compiled);put(a.output/'outline-observer-models.json',models)
 phases=phase_models(LuaRuntime,script);assert len(phases['models'])==32;put(a.output/'phase-models.json',phases)
 returns=core_tests(LuaRuntime,old_core((ROOT/'tools/audit/final_item_abilities_native.lua').read_text()),(ROOT/'tools/audit/final_item_abilities_static_return_v1.lua').read_text())
 dma=dma_mocks(LuaRuntime,(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=cfg['dma_protocol']))
 put(a.output/'static-controls.json',dict(passed=True,complete_CPU_presentation_cells=96,complete_DrawAll_calls=192,uncached_cached_filtered=96,Lua_models=len(models['models']),positive_models=96,negative_models=8,original_phase_models=32,return_models=returns,DMA_models=dma,callbacks=models['callbacks'],dispatcher_last=True,all_other_mechanics_reverse_exact=True))
 shutil.copytree(OLD/'emulator',a.output/'emulator')
 env=copy.deepcopy(oldproof['environment']);env['emulator']=str(a.output/'emulator/Mesen.exe');env['user_settings_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(Path(env['emulator']))==env['emulator_sha256']and sha(a.output/'emulator/settings.json')==env['worker_settings_sha256']
 put(a.output/'environment.json',env)
 for name in['plans.json','seed-policy.json']:shutil.copy2(OLD/name,a.output/name)
 report=ROOT/'docs/qa/final-samus-hard-gallery-outline-observer-2026-10-26.txt'
 report.write_text('Samus Hard outline observer correction\n26 October 2026. Source/static readiness only; no new launch/grant.\n\nExact ROM '+SHA+' is unchanged. Original native proof '+sha(old/'proof.json')+' stays FALSE: zero completed cases/subphases, first staged update wall374;352 complete256 DMA epochs/374 startFrame records independently exact,35 scoped safe enables. The retained art assertion did not allow the genuine default-off outline path. The partial failure A126/X0/Y0 and known body bank13 match the independently reproduced cached native filter signature; the original low pointer was not logged and is not backfilled.\n\ncharacters.s initializes PlayerOutlinesOff1. Full PlayerGfxHandler→DrawAll→DrawMetasprite→PlayerRemoveOutlines controls now cover standing/crouch/Morph/spin, both facings and all classic tiers plus current Hard starting/Long/Varia:96 CPU setup cells,192 complete DrawAll calls (uncached plus repeated cache). Actual return PC/SP/C-bank and full source/filter bytes are bound. Short stand C02D header44 becomes OutlinePoseBuffer7EBB header20 by removing only six tagged extra-mask records. Original record pixels/attributes are not invented or modified by the observer. These CPU cells do not add native mode/acquisition coverage.\n\nObserver v2 authenticates the immutable source record at the genuine compiled filter entry, records the actual fixed-dispatch return, accepts only the source-owned RAM buffer slots and exact derived header/bytes, then checks them again at the real renderer. Wrong RAM pointer/header/tile/ROM source/C return and wrong return SP/bank controls reject or defer.96 actual uncached/cached positive models and8 negatives pass. One startup callback and one read-only label added; no seed, resource, actor, controller, ability/deadline/effect/CHR/output or existing guard change. Exact reverse normalization proves all other script bytes and config semantics unchanged. Original32 phase,8return and13DMA models pass. No ROM/game/settings/default/Git changes and no automatic retry.\n\nThe next separately granted eight-case/27-subphase B gallery remains controlled use, not acquisition. Complete actor/scene/resource setup and CPU-only exclusions retain the original seed policy. No Hard ability or graphics pass is claimed from the first failed run.\n',encoding='utf-8')
 files={Path(__file__),ROOT/'tools/audit/final_samus_hard_gallery_outline_controls_v2.py',ROOT/'tools/audit/final_samus_hard_gallery_native_v2.lua',ROOT/'tools/audit/final_samus_hard_gallery_run_v1.py',report,OLD/'proof.json',OLD/'manifest.json',NEG/'proof.json',NEG/'manifest.json'}
 files.update(Path(z['path'])for z in json.loads((OLD/'manifest.json').read_text())['bindings']);files.update(q for q in a.output.rglob('*')if q.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));verified=verify_manifest(a.output/'manifest.json')
 command='python -B tools/audit/final_samus_hard_gallery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant'
 ready=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='samus-hard',mode_value=1,maximum_cases=8,maximum_launches=1,maximum_owned_workers=1,retry=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=verified,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,source_controls_sha256=sha(a.output/'static-controls.json'),stable_command=command,source_freeze_sha256=sha(PARENT/'ROOT-source-readiness.json'),previous_FALSE_sha256=sha(old/'proof.json'),observer_only=True,report_sha256=sha(report))
 put(a.output/'proof.json',ready);verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),script_sha256=sha(out/'run.lua'),bindings=verified,stable_command=command),indent=2))

if __name__=='__main__':main()
