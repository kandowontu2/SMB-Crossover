"""Profile-local physical OAM encoding correction; source/mock readiness, no launch."""
from pathlib import Path
import argparse, ast, copy, difflib, hashlib, json, shutil, sys
from final_megaproto_common_source_v2 import D, R, B, SHA
from final_item_abilities_run import lua
from final_item_abilities_remaining731_run_v1 import verify_manifest
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OLD=D/'current0a-mega-common-ready-v5'
NEG=D/'current0a-mega-common-negative-final-v1'
MODULE=R/'tools/audit/final_megaproto_common_dma_oam_v2.lua'
RUNNER=R/'tools/audit/final_megaproto_common_oam_run_v1.py'
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))

MOCK_DMA='''
callbacks={};events={};mem={};hardware={};logs={};state={['cpu.sp']=240,['cpu.pc']=0,['cpu.cycleCount']=0,['ppu.frameCount']=184,['ppu.scanline']=-1,['ppu.cycle']=0,['ppu.spriteRamAddr']=0}
emu={memType={nesDebug=1,nesSpriteRam=2},callbackType={exec=2,write=1},eventType={startFrame=3}}
emu.getState=function()return state end
emu.read=function(a,t)if t==2 then return hardware[a]or 0 else return mem[a]or 0 end end
emu.addMemoryCallback=function(fn,k,lo,hi)callbacks[#callbacks+1]={fn=fn,k=k,lo=lo,hi=hi or lo}end
emu.addEventCallback=function(fn,k)events[k]=fn end
io.open=function()return{write=function(self,s)logs[#logs+1]=s;return self end,flush=function()end}end
function fire(k,a,v)for _,q in ipairs(callbacks)do if q.k==k and a>=q.lo and a<=q.hi then q.fn(a,v)end end end
local C=CFG;local OUTPUT='mock/';local entered,done=true,false;local published=nil;local dma=nil
local function bytes(at,t)local z={};for i=0,255 do z[#z+1]=string.char(emu.read(at+i,t))end;return table.concat(z)end
local function bank(a)return a>=0xe000 and CFG.dma_protocol.bank or 1 end
local function json(v)if v.kind=='completed-DMA-before-render-enable'then completedRow=v end;return'RAW-BEFORE-ASSERT'end
for i,v in ipairs(C.dma_protocol.window_bytes)do mem[C.dma_protocol.window_start+i-1]=v end
for i=0,255 do mem[512+i]=0;hardware[i]=0 end
'''
EXPORT='''
function TEST_PUBLISH()published=bytes(512,emu.memType.nesDebug)end
function TEST_DMA_CREDIT()return dma~=nil end
function TEST_END_FRAME()
 if dma then assert(bytes(0,emu.memType.nesSpriteRam)==oamPhysical(dma),'Committed native publication reaches OAM DMA with exact PPU attribute encoding');dma=nil end
end
'''

def controls(LuaRuntime,text,cfg,bad):
    cases=[]
    def execute(name,body,passes=True):
        rt=LuaRuntime(unpack_returned_tuples=True);rt.execute('CFG='+lua(cfg)+'\n'+MOCK_DMA+text+EXPORT)
        count=rt.eval('#callbacks');rt.execute('emu.write=function()error("Observer mutation")end;emu.addMemoryCallback=function()error("runtime registration")end;emu.removeMemoryCallback=function()error("runtime removal")end')
        ok,error=rt.eval('function()local ok,e=pcall(function()'+body+' end);return ok,tostring(e)end')()
        assert bool(ok)==passes,(name,error);assert rt.eval('#callbacks')==count
        if not passes:assert rt.eval('#logs')>0,name
        cases.append(dict(name=name,passed=True,expected='accept'if passes else'reject',rejection=None if passes else error))
    begin="state['cpu.pc']=CFG.dma_protocol.window_start;fire(1,0x2001,0);fire(1,0x4014,2);"
    transfer="for i=0,255 do state['ppu.spriteRamAddr']=i;fire(1,0x2004,mem[512+i])end;state['ppu.spriteRamAddr']=0;"
    finish="fire(2,CFG.dma_protocol.complete_pc,0);"
    for off in [2,34,254]:
        for tags in [0,4,8,12,16,20,24,28]:
            execute(f'attr{off}_ignored_tags_{tags:02x}',f'mem[{512+off}]={tags};TEST_PUBLISH();'+begin+transfer+finish+'assert(TEST_DMA_CREDIT());events[3]();TEST_END_FRAME();assert(not TEST_DMA_CREDIT());')
    for off in [0,1,3,255]:
        for bit in [4,8,16]:execute(f'nonattr{off}_bit{bit}_not_ignored',f'mem[{512+off}]={bit};'+begin+transfer+finish,False)
    for off in [2,34,254]:
        for bit in [1,2,32,64,128]:execute(f'attr{off}_implemented_bit{bit}_corruption',f'mem[{512+off}]={bit};'+begin+transfer+finish,False)
    for bit in [4,8,16]:execute(f'physical_unimplemented_bit{bit}_must_be_zero',f'hardware[34]={bit};'+begin+transfer+finish,False)
    execute('source_write_must_keep_ignored_tag', 'mem[546]=16;'+begin+transfer.replace('mem[512+i])','(i==34 and 0 or mem[512+i]))')+finish,False)
    execute('raw_publication_tag_difference_does_not_gain_credit','TEST_PUBLISH();mem[546]=16;'+begin+transfer+finish+'assert(not TEST_DMA_CREDIT());events[3]();')
    execute('classified_raw_difference_before_equality','mem[546]=16;'+begin+transfer+finish+'assert(#completedRow.differences==1 and #completedRow.ignored_attribute_differences==1 and #completedRow.implemented_differences==0);assert(completedRow.source[35]==16 and completedRow.hardware[35]==0 and completedRow.writes[35].value==16);')
    execute('wrong_destination_ordinal',begin+transfer.replace("state['ppu.spriteRamAddr']=i;","state['ppu.spriteRamAddr']=(i==242 and 244 or i);")+finish,False)
    execute('missing_write',begin+transfer.replace('i=0,255','i=0,254')+finish,False)
    execute('wrong_start_address',"state['ppu.spriteRamAddr']=8;"+begin+transfer+finish,False)
    execute('wrong_end_address',begin+transfer+"state['ppu.spriteRamAddr']=8;"+finish,False)
    execute('wrong_source_page',begin.replace('0x4014,2','0x4014,3')+transfer+finish,False)
    execute('wrong_post_store_PC',begin.replace("state['cpu.pc']=CFG.dma_protocol.window_start","state['cpu.pc']=CFG.dma_protocol.window_start+1")+transfer+finish,False)
    execute('E005_not_completion',begin+'fire(2,CFG.dma_protocol.obsolete_preDMA_exec_pc,0);'+finish,False)
    execute('rendering_enabled_during_transfer',begin.replace('0x2001,0','0x2001,30')+transfer+finish,False)
    execute('rendering_transient_mid_transfer',begin+transfer.replace("state['ppu.spriteRamAddr']=i;fire", "if i==128 then fire(1,0x2001,30)end;state['ppu.spriteRamAddr']=i;fire")+finish,False)
    scoped="mem[CFG.dma_protocol.scope_ram.DisableScreenFlag]=0;mem[CFG.dma_protocol.scope_ram.CrossoverMenuState]=2;mem[CFG.dma_protocol.scope_ram.OperMode]=0;state['ppu.scanline']=-1;"
    execute('render_enable274_still_accepted',scoped+"state['ppu.cycle']=274;fire(1,0x2001,30)")
    execute('render_enable275_still_rejected',scoped+"state['ppu.cycle']=275;fire(1,0x2001,30)",False)
    execute('changed_start_hardware',begin+transfer+finish+'hardware[7]=1;events[3]();',False)
    execute('changed_endFrame_hardware','TEST_PUBLISH();'+begin+transfer+finish+'hardware[7]=1;TEST_END_FRAME();',False)
    execute('pending_start_remains_pending',begin+'events[3]();'+transfer+finish)
    actual='\n'.join(f'mem[{512+i}]={v};hardware[{i}]={bad["hardware"][i]}'for i,v in enumerate(bad['source']))
    execute('saved_actual_DMA392_physical_encoding',actual+';TEST_PUBLISH();'+begin+transfer+finish+'assert(TEST_DMA_CREDIT());events[3]();TEST_END_FRAME();assert(#completedRow.differences==1 and completedRow.differences[1].offset==34);')
    return dict(passed=True,source_mock_only=True,models=len(cases),cases=cases,no_emulated_observer_writes=True,no_runtime_registration=True,scope='Same actual Lua DMA/publication predicates, controlled inputs only. Source and every actual input remain unmasked; hardware attributes encode E3. No native pass inferred from saved392 interpretation.')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert verify_manifest(OLD/'manifest.json')==934;verify_manifest(NEG/'manifest.json');oldproof=json.loads((OLD/'proof.json').read_text());old=OLD/'native';cfg=json.loads((old/'config.json').read_text());before=(old/'run.lua').read_text();oldmodule=(R/'tools/audit/final_item_abilities_dma731_v1.lua').read_text()+'\n';newmodule=MODULE.read_text()+'\n';assert before.count(oldmodule)==1
 oldend="assert(bytes(0,emu.memType.nesSpriteRam)==dma,'Committed native publication reaches OAM DMA')";newend="assert(bytes(0,emu.memType.nesSpriteRam)==oamPhysical(dma),'Committed native publication reaches OAM DMA with exact PPU attribute encoding')";assert before.count(oldend)==1
 after=before.replace(oldmodule,newmodule).replace(oldend,newend);assert after.replace(newmodule,oldmodule).replace(newend,oldend)==before
 assert before.count('nesSpriteRam')==after.count('nesSpriteRam')
 oldadmission="if entered and not done and published then local s=bytes(v*256,emu.memType.nesDebug);if s==published then dma=s end end";assert oldadmission in after
 rawwrite="assert(wq.value==q.source:byte(i),'Actual DMA reads its exact frozen source byte')";assert rawwrite in after
 guard=(old/'inherited-NMI-stack-APU-guards.lua').read_bytes();assert sha(old/'inherited-NMI-stack-APU-guards.lua')=='6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf';assert guard.decode().replace('\r\n','\n')in after
 # Reverse all collector-only edits too: component, caps, modes and launcher
 # must remain exact rather than relying only on generated Lua equality.
 previous_runner=(R/'tools/audit/final_megaproto_common_run_v1.py').read_text();next_runner=RUNNER.read_text();normalized=next_runner
 substitutions=[
  ('"""Profile-local E3 hardware-oracle successor; one granted native attempt only."""','"""One separately granted exact0a MegaHard common-special gallery; no retries."""'),
  ('\nphysical=lambda s:[v&0xe3 if i%4==2 else v for i,v in enumerate(s)]',''),
  ('completed=starts=enables=literal=ignored=0;last=None;','completed=starts=enables=0;last=None;'),
  ("physical(q['source'])==q['hardware']and not q['implemented_differences']","q['source']==q['hardware']and not q['differences']"),
  ("    rawdiff=[dict(offset=i,source=x,hardware=y)for i,(x,y)in enumerate(zip(q['source'],q['hardware']))if x!=y];assert rawdiff==list(q['differences'])==list(q['ignored_attribute_differences']);literal+=int(not rawdiff);ignored+=len(rawdiff)\n",''),
  ("q['hardware']==physical(last['source'])","q['hardware']==last['source']"),
  ('safe_enables=enables,literal_byte_equal_DMA=literal,ignored_attribute_differences=ignored,physical_encoding_exact_DMA=completed,raw_sha256=','safe_enables=enables,raw_sha256='),
  (";assert ready['profile_local_OAM_encoding']=='attributeE3-v2'",'')]
 for current,previous in substitutions:
  assert normalized.count(current)==1,(current,normalized.count(current));normalized=normalized.replace(current,previous)
 assert normalized==previous_runner
 put(a.output/'collector-controls.json',dict(passed=True,reverse_normalization_exact=True,substitutions=[dict(current=x,previous=y)for x,y in substitutions],all_nonhardware_component_assertions_and_launch_caps_exact=True))
 (a.output/'collector.patch').write_text(''.join(difflib.unified_diff(previous_runner.splitlines(True),next_runner.splitlines(True),fromfile='frozen-original-collector',tofile='profile-local-physical-encoding-collector')),encoding='utf-8')
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 bad=json.loads((D/'current0a-mega-common-negative-v1/first-physical-difference.json').read_text());models=controls(LuaRuntime,newmodule,cfg,bad);put(a.output/'hardware-oracle-controls.json',models)
 startup=[]
 for name,script in [('original',before),('successor',after)]:
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'+script)
  count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535');rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
  for frame in[1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
  assert rt.eval('#callbacks')==count;startup.append(dict(name=name,callbacks=count,dispatcher_last=True,three_inactive_frames=True))
 assert startup[0]['callbacks']==startup[1]['callbacks']==74;put(a.output/'startup-controls.json',dict(passed=True,models=startup))
 (a.output/'observer.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen-original-native-FALSE',tofile='profile-local-physical-encoding')),encoding='utf-8')
 put(a.output/'invariants.json',dict(passed=True,reverse_normalized_script_exact=True,config_byte_exact=True,controller_seeds_caps_mechanics_HUD_art_NMI_IRQ_CHR_banks_stack_APU_unchanged=True,foreground_source_publication_raw_exact=True,DMA_input256_raw_exact=True,hardware_only_attribute_E3=True,raw_differences_retained=True,raw_differences_classified=True,all_other_bytes_physical_raw_exact=True,inherited_guard_sha256=sha(old/'inherited-NMI-stack-APU-guards.lua'),original_global_DMA_module_sha256=sha(R/'tools/audit/final_item_abilities_dma731_v1.lua'),old_script_sha256=sha(old/'run.lua'),new_script_sha256=hashlib.sha256(after.encode()).hexdigest()))
 out=a.output/'native';out.mkdir()
 for ext in['nes','dbg','lbl','map']:shutil.copy2(old/('candidate.'+ext),out/('candidate.'+ext))
 assert sha(out/'candidate.nes')==SHA;shutil.copy2(old/'config.json',out/'config.json');shutil.copy2(old/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua');(out/'run.lua').write_text(after,encoding='utf-8')
 env=copy.deepcopy(oldproof['environment']);runtime=a.output/'emulator';runtime.mkdir()
 for q in Path(env['emulator']).parent.iterdir():
  if q.is_file():shutil.copy2(q,runtime/q.name)
 env['emulator']=str(runtime/'Mesen.exe');env['user_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'MesenCore.dll')==env['core_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];put(a.output/'environment.json',env)
 put(a.output/'plans.json',cfg['cases'])
 report=R/'docs/qa/final-megaproto-common-oam-ready-2026-10-26.txt';report.write_text('MegaHard common gallery: profile-local physical OAM observer successor\nExactprivate0a '+SHA+'. Source/mock only; no native grant or run.\n\nOriginal392 firstFALSE remains frozen. The only hardware interpretation change is attribute bytes2mod4 expected rawsource&E3; all other bytes rawexact. Source-to-published and every256 actual DMA input byte remain UNMASKED exact. Original full rawsource/hardware/differences/write serialization retained; additive implemented/ignored arrays classify raw differences. Actual completed-E008, page/PC/count/ordinal/OAMADDR/mask/deadline guards retained; all hardware-side completion/startFrame/endFrame publication comparisons consistently use physical encoding. Global DMA731v1/inherited6ab7guard and old readies untouched.\n\nReverse-normalized generated script is exact original; same14cases/controller/input/seeds/caps/target/HUD/effect/contact/exhaust/refusal/pool/cleanup/art/physicalCHR/IRQ31/5SMC/banks/SP. Same74fixedcallbacks/finalstaticdispatcher, no runtime registration. Mock controls accept bits2/3/4 only in attribute storage and reject every implemented bit, ignored-bit mutations elsewhere, physical unimplemented bits, rawinput normalization, missing/wrongordinal/address/page/PC, rendering and lateenable. Rawpublication tag difference doesnotgainDMAcredit. Saved392 physical encoding is an OFFLINE model acceptance, not retagged native pass.\n\nOne preparedMegaHard profile/max1launch/no retry/no automaticProto. B-only seeded use, not physical acquisition. Originalbodyvisibility414/415, source-font/color/audio/campaign/globalperformance limits remain. Actual current runtime copied/bound without settings edits. Requires fresh ROOT readiness review/grant.\n',encoding='utf-8')
 files={Path(z['path'])for z in json.loads((OLD/'manifest.json').read_text())['bindings']};files.update({OLD/'proof.json',OLD/'manifest.json',OLD/'ROOT-grant.json',NEG/'proof.json',NEG/'manifest.json',MODULE,RUNNER,Path(__file__),report,Path('C:/Mesen2/settings.json'),Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__)})
 pending=[Path(__file__),RUNNER];seen=set()
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
 files.update({D/'current0a-mega-common-negative-v1/first-physical-difference.json',D/'current0a-mega-common-negative-v1/source-context.json',D/'current3cee-nmi-mask-order-audit-v1/NesPpu.cpp',R/'tools/audit/final_megaproto_common_run_v1.py'});files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json');command='python -B tools/audit/final_megaproto_common_oam_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,profile_local_OAM_encoding='attributeE3-v2',ROM_sha256=SHA,profile='mega-hard-common',mode_value=1,variant=0,maximum_cases=14,maximum_launches=1,maximum_owned_workers=1,retry=False,automatic_other_profiles=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,stable_command=command,source_controls_sha256=sha(a.output/'hardware-oracle-controls.json'),report_sha256=sha(report),lane='B',acquisition=False,original_FALSE_preserved=True));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=count,script_sha256=sha(out/'run.lua'),models=models['models'],stable_command=command),indent=2))
if __name__=='__main__':main()
