"""Small source-only lossless codec/I/O controls; no emulator or input copies."""
from pathlib import Path
import argparse,hashlib,json,random,struct,sys
from final_inventory_compact_capture_v1 import MODULE,FRAME_BYTES,adapt_script,decode,read_virtual,verify
from capture_budget import RUN_BYTES,RUN_FILES
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prefix',required=True,type=Path);p.add_argument('--lua-root',required=True,type=Path);a=p.parse_args();assert a.prefix.parent.is_dir(),'Use an existing directory; no dependency/output trees are cloned';assert not list(a.prefix.parent.glob(a.prefix.name+'.*'))
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 rt=LuaRuntime(unpack_returned_tuples=True,encoding=None);module=MODULE.read_bytes();assert b'emu.'not in module and b'addMemoryCallback'not in module and b'addEventCallback'not in module
 rt.execute(b'M=(function()\n'+module+b'\nend)()')
 rng=random.Random(731);codec=[]
 for n in[1,2,3,127,128,129,255,256,257]:
  for shape in['zero','repeat','noise','mixed']:
   words=[0 if shape=='zero'else 0xff102030 if shape=='repeat'else rng.getrandbits(32)if shape=='noise'or i%17==0 else 0xff000000 for i in range(n)];raw=struct.pack('<'+'I'*n,*words)
   for prior,key in[(None,True),(raw,False),(bytes(x^0x55 for x in raw),False)]:
    mode,payload,check=rt.globals().M.encode(raw,prior,key);assert decode(mode,payload,prior,len(raw))==raw;codec.append(dict(words=n,shape=shape,mode=mode,bytes=len(payload)))
 put(a.prefix.with_suffix('.codec.json'),dict(passed=True,cases=len(codec),rows=codec))
 pre=b'''
files={};opens={};callbacks={};events={};captured={};screen={}
state={['ppu.frameCount']=0,['ppu.scanline']=240,['ppu.cycle']=0,['cpu.cycleCount']=0,['cpu.pc']=57355,['cpu.sp']=225,['cpu.a']=0,['cpu.x']=0,['cpu.y']=0}
io.open=function(path,mode)
 opens[#opens+1]=path;local parts={};local h={}
 function h:write(...)for i=1,select('#',...)do parts[#parts+1]=select(i,...)end;files[path]=table.concat(parts);return self end
 function h:flush()return self end
 function h:close()files[path]=table.concat(parts);return true end
 return h
end
emu={eventType={endFrame=1},callbackType={exec=2},getState=function()return state end,getScreenBuffer=function()return screen end,
convertAddress=function(a)return{address=127*8192+a%8192}end,
addMemoryCallback=function(...)callbacks[#callbacks+1]={...}end,addEventCallback=function(f,k)events[#events+1]=f end,
write=function()error('Emulated observer write')end,setInput=function()error('Controller changed')end}
OUTPUT='mock/'
'''
 rt.execute(pre)
 base=R/'tools/audit/final_item_matrix_progressive.lua';old=base.read_text();first=old.index(' for _,q in ipairs(queue)do\n');last=old.index('end;queue={}',first)+len('end;queue={}')
 named=old[first:last];ppu=(R/'tools/audit/final_item_abilities_pit731_ppu_v1.lua').read_text();failure=(R/'tools/audit/final_item_abilities_failure.lua').read_text()
 json_source=old[old.index('local function json(v)'):old.index('local log=')]
 original='''FINAL_ITEM_PROGRESSIVE={}
local C=FINAL_ITEM_PROGRESSIVE
local phase,updates,done,queue='synthetic',0,false,{}
local function r(n)return 1 end
local function event(kind,q)captured[#captured+1]={kind=kind,name=q.name}end
for i=1,74 do emu.addMemoryCallback(function()end,2,i)end
'''+json_source+failure+'\n'+ppu+'\nemu.addEventCallback(function()\n'+named+'''\nend,emu.eventType.endFrame)
function SET_FRAME(raw,k,last)
 screen={};for at=1,#raw,4 do screen[#screen+1]=string.unpack('<I4',raw,at)end
 state['ppu.frameCount']=k;state['cpu.cycleCount']=k*29780;updates=k;done=last
 queue={{name='case-'..k,update=k,wall=k,status=1}}
 for _,fn in ipairs(events)do fn()end
end
function NAMED(raw,name)
 local f=assert(io.open(OUTPUT..name..'.argb','wb'));f:write(raw);f:close()
end
function BLOB(raw,name)local f=assert(io.open(OUTPUT..name,'wb'));f:write(raw);f:close()end
function SYNTHETIC_FAIL()
 FINAL_ABILITY_PHASE={name='retained-source-assertion',phase='synthetic'}
 return pcall(assert,false,'Synthetic original assertion stays FALSE')
end
function STATS()return FINAL_COMPACT_CAPTURE.stats()end
function FINISH()FINAL_COMPACT_CAPTURE.close()end
'''
 adapted,inserted=adapt_script(original);assert adapted.replace(inserted,'',1)==original
 # Export appended in the same lexical chunk; no callback added by adapter.
 rt.execute(adapted.encode());assert rt.eval(b'#callbacks')==74 and rt.eval(b'#events')==2
 rt.execute(b'emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 frames=[];solid=struct.pack('<I',0xff102030)*(FRAME_BYTES//4);noise=rng.randbytes(FRAME_BYTES)
 shifted=bytearray(noise);shifted[300:304]=b'\x01\x02\x03\xff'
 for k,raw in enumerate([solid,noise,noise,bytes(shifted),solid,solid],1):
  frames.append(raw);rt.globals().SET_FRAME(raw,k,k==6)
 # Hundreds of virtual captures prove there is no corresponding file growth.
 for i in range(300):rt.globals().NAMED(solid,('gallery-%03d'%i).encode())
 rt.globals().NAMED(solid,b'reused-name');rt.globals().NAMED(bytes(shifted),b'reused-name')
 blob=bytes(range(256))*4;rt.globals().BLOB(blob,b'diagnostic-CHR-0242.bin')
 ok,message=rt.globals().SYNTHETIC_FAIL();assert not ok and b'Synthetic original assertion stays FALSE'in message
 rt.globals().FINISH();assert rt.eval(b'#callbacks')==74
 files=rt.globals().files;expected_names=[b'mock/captures.nesppuv1',b'mock/captures-index.jsonl',b'mock/actual-ppu-index.csv',b'mock/ppu-capture-native-result.json',b'mock/first-failure.json'];assert set(files)==set(expected_names)
 container=a.prefix.with_suffix('.synthetic.nesppuv1');index=a.prefix.with_suffix('.synthetic-index.jsonl');fullindex=a.prefix.with_suffix('.synthetic-PPU-index.csv')
 for path,key in[(container,expected_names[0]),(index,expected_names[1]),(fullindex,expected_names[2])]:path.write_bytes(files[key])
 proof=verify(container,index,fullindex);assert proof['full_frames']==6 and proof['decoded_full_sha256']==hashlib.sha256(b''.join(frames)).hexdigest()and proof['named_aliases']==308
 assert read_virtual(container,index,'reused-name.argb')==bytes(shifted)and read_virtual(container,index,'first-failure.argb')==solid and read_virtual(container,index,'diagnostic-CHR-0242.bin')==blob
 negatives=[]
 # Malformed records and wrong indices must fail without touching frozen data.
 import tempfile
 with tempfile.TemporaryDirectory(prefix='compact-source-controls-')as folder:
  temp=Path(folder)
  for name,mutate in [('truncated-header',lambda z:z[:18]),('truncated-payload',lambda z:z[:-1]),('changed-visible-or-ignored-pixel-bit',lambda z:z[:-1]+bytes([z[-1]^1])),('wrong-sequence',lambda z:z[:20]+struct.pack('<I',99)+z[24:])]:
   target=temp/'bad.container';target.write_bytes(mutate(container.read_bytes()))
   try:verify(target,index);rejected=False
   except Exception:rejected=True
   assert rejected,name;negatives.append(dict(name=name,rejected=True))
  for name,mutate in [('missing-physical-index',lambda z:[q for q in z if not(q['type']=='record'and q['record']==1)]),('wrong-alias-target',lambda z:next(q for q in z if q['type']=='alias').__setitem__('record',999)),('changed-source-stamp',lambda z:z[0]['stamp'].__setitem__('ppu_frame',999))]:
   rows=[json.loads(s)for s in index.read_text().splitlines()];changed=mutate(rows);rows=changed if isinstance(changed,list)else rows;target=temp/'bad.index';target.write_text(''.join(json.dumps(q)+'\n'for q in rows))
   try:verify(container,target);rejected=False
   except Exception:rejected=True
   assert rejected,name;negatives.append(dict(name=name,rejected=True))
 # The source contains every original capture/failure assertion byte intact.
 put(a.prefix.with_suffix('.delta.json'),dict(passed=True,whole_input_body_reverse_exact=True,original_failure_assertion_rejected=True,adapter_callbacks_added=0,synthetic_callbacks_before_after=74,controller_calls_added=0,emulated_writes_added=0,source_fragments=[bind(base),bind(R/'tools/audit/final_item_abilities_pit731_ppu_v1.lua'),bind(R/'tools/audit/final_item_abilities_failure.lua')],per_frame_files_created=0,named_capture_files_created=0,diagnostic_CHR_files_created=0,screenshots_created=0,virtual_named_capture_events=309,physical_synthetic_files=5,collector_change='Only full-PPU file reader becomes lossless container decode; native frame/count/mode/order and all other gameplay/DMA predicates remain required. Final deleted original b645/native scripts were not recreated or claimed reverified.'))
 refs=[Path(__file__),MODULE,R/'tools/audit/final_inventory_compact_capture_v1.py',R/'tools/audit/capture_budget.py',Path(sys.modules[LuaRuntime.__module__].__file__),base,R/'tools/audit/final_item_abilities_pit731_ppu_v1.lua',R/'tools/audit/final_item_abilities_failure.lua']+list(a.prefix.parent.glob(a.prefix.name+'.*'))
 put(a.prefix.with_suffix('.manifest.json'),dict(bindings=[bind(q)for q in refs]));put(a.prefix.with_suffix('.proof.json'),dict(passed=True,source_only=True,native_run=False,codec_cases=len(codec),synthetic_full_frames=6,actual_native_frames=0,adapter_test=proof,negative_controls=negatives,body_assertions_reverse_exact=True,one_lossless_container=True,screenshots=0,central_run_byte_cap=RUN_BYTES,central_run_file_cap=RUN_FILES,container_reservation=1500000000,other_evidence_headroom=500000000,manifest_sha256=sha(a.prefix.with_suffix('.manifest.json')),limits='Pure source/mock adapter qualification only. Original generated74-callback b645 fixture and candidate were user-deleted, not restored/relabelled. Fresh exact preparation/central guard/native grant still required.'))
 print(json.dumps(dict(proof=str(a.prefix.with_suffix('.proof.json')),proof_sha256=sha(a.prefix.with_suffix('.proof.json')),manifest_sha256=sha(a.prefix.with_suffix('.manifest.json')),container_bytes=container.stat().st_size,source_only=True),indent=2))
if __name__=='__main__':main()
