"""Read-only power-on replay to localize the confirmed Bill movie palette fault."""
from pathlib import Path
import sys,json,shutil,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));import run_mesen
O=R/'build/verification/bill-green-native-i';assert not O.exists();O.mkdir()
P=R/'build/roster-through-2-2/claude-final-video-3-v0-mmc3';m=json.loads((P/'manifest.json').read_text())
cfg=m['config'].copy();cfg.update(limit=15000,out=O.as_posix()+'/',record=False,segmented=False,audit=(O/'audit.lua').as_posix(),replay=(P/'inputs.csv').as_posix(),policy=(P/'policy.lua').as_posix())
lua=lambda v:'nil'if v is None else str(v).lower()if isinstance(v,bool)else json.dumps(v)
(O/'run.lua').write_text('ROSTER_CONFIG={\n'+''.join(f' {k}={lua(v)},\n'for k,v in cfg.items())+'}\ndofile('+json.dumps((P/'harness.lua').as_posix())+')\n',encoding='utf-8')
observer=r'''return function(cfg)
 local base=assert(dofile(ORIGINAL_AUDIT))(cfg)
 local frame=0;local w,t,v,ctrl=0,0,0,0
 local writes=assert(io.open(cfg.out..'ppu-writes.csv','w'))
 writes:write('frame,scanline,dot,pc,bank,address,value,bufferOffset,attrBuffer\n')
 local attrs=assert(io.open(cfg.out..'attributes.csv','w'))
 attrs:write('frame,camera,attributes,palette\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function observe()return frame>=12000 and r('WorldNumber')==0 and r('LevelNumber')==2 end
 emu.addMemoryCallback(function()w=0 end,emu.callbackType.read,0x2002)
 emu.addMemoryCallback(function(a,b)
  if a==0x2000 then ctrl=b;t=(t&0xf3ff)|((b&3)<<10)
  elseif a==0x2005 then
   if w==0 then t=(t&0x7fe0)|(b>>3);w=1 else t=(t&0x0c1f)|((b&7)<<12)|((b&0xf8)<<2);w=0 end
  elseif a==0x2006 then
   if w==0 then t=(t&0xff)|((b&0x3f)<<8);w=1 else t=(t&0x7f00)|b;v=t;w=0 end
  elseif a==0x2007 then
   if observe()then
    local s=emu.getState()
    writes:write(table.concat({frame+1,s['ppu.scanline'],s['ppu.cycle'],s['cpu.pc'],r('CurrentBank'),v&0x3fff,b,r('VRAM_Buffer1_Offset'),r('AttributeBuffer')},',')..'\n')
   end
   v=(v+((ctrl&4)~=0 and 32 or 1))&0x7fff
  end
 end,emu.callbackType.write,0x2000,0x2007)
 local last
 return {failure=base.failure,frame=function(f)
  frame=f;base.frame(f)
  if observe()then
   local aa,pa={},{}
   for _,a in ipairs({0x23c0,0x27c0})do for n=0,63 do aa[#aa+1]=string.format('%02x',emu.read(a+n,emu.memType.nesPpuDebug))end end
   for n=0,31 do pa[#pa+1]=string.format('%02x',emu.read(0x3f00+n,emu.memType.nesPpuDebug))end
   local now=table.concat(aa)..table.concat(pa)
   if now~=last then
    attrs:write(table.concat({f,r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),table.concat(aa),table.concat(pa)},',')..'\n');last=now
   end
  end
 end,finish=function()base.finish();writes:close();attrs:close()end}
end
'''
observer=observer.replace('ORIGINAL_AUDIT',json.dumps((P/'audit.lua').as_posix()))
(O/'audit.lua').write_text(observer,encoding='utf-8')
before=hashlib.sha256((P/'smb-crossover-mmc3.nes').read_bytes()).hexdigest();assert before==m['rom_sha256']
exitcode=run_mesen.run(O/'run.lua',P/'smb-crossover-mmc3.nes',timeout=120,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
result=json.loads((O/'result.json').read_text())if(O/'result.json').exists()else None
summary=dict(rom_sha256=before,input_sha256=hashlib.sha256((P/'inputs.csv').read_bytes()).hexdigest(),exit=exitcode,result=result,scope='Bounded ordinary-input replay of existing Bill movie. Memory inspection only; no RAM/register writes or gameplay alteration. Frame-limit exit is expected, not a full clear.')
if result:
 assert result['frames']==15000 and result['failure']=='frame limit'
 assert (O/'trace.csv').read_bytes()==b'\n'.join((P/'trace.csv').read_bytes().splitlines()[:15001])+b'\n'
 summary['trace_literal_to_movie_prefix']=True
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary),flush=True)
