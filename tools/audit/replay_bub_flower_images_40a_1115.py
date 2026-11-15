"""Two in-memory rendered pictures over the frozen functional Flower route."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_bub_flower_margin_40a_1115 as Previous

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN
PARENT='88a452e94489dea2749403abc193b7c4a2578b7a2e837183a0cf102af3d85b76'
DECL='local visualRows,visualQueue,visualSeen,visualLast={},{},{},nil\n'
OBSERVE=r'''
local visualPpu,visualMode,visualUpper=0,-1,0
local visualBanks={}
for _,at in ipairs({0x2000,0x5101,0x5130,0x5120,0x5121,0x5122,0x5123,0x5124,0x5125,0x5126,0x5127})do
 emu.addMemoryCallback(guard(function(address,value)
  if address==0x2000 then visualPpu=value elseif address==0x5101 then visualMode=value
  elseif address==0x5130 then visualUpper=value&3 else visualBanks[address-0x5120]=(visualUpper<<8)|value end
 end),emu.callbackType.write,at)
end
local function visualObserve()
 if done or not game then return end
 local s=rideState();s.flags=full_state((identity==1 and 0x42 or 0x2e)+2);s.power=r('PlayerStatus')
 local item=nil;local enemies={}
 for i=0,5 do
  local flag=read(L.Enemy_Flag+i);local id=read(L.Enemy_ID+i)
  if flag>0 and flag<128 then
   local a={slot=i,flag=flag,id=id,state=read(L.Enemy_State+i),x=full_x(i),y=read(L.Enemy_Y_Position+i)}
   if id==46 then a.kind=read(L.PowerUpType+i);item=a elseif id==6 or id==0 then enemies[#enemies+1]=a end
  end
 end
 local bubble=nil
 for i=0,14 do
  local kind=work(2,0x88+4*i);local sx=work(2,0x18b+8*i);local sy=work(2,0x188+8*i)
  if kind==2 and sx>=16 and sx<=240 and sy<232 then bubble={slot=i,kind=kind,source_x=sx,source_y=sy};break end
 end
 visualLast={state=s,item=item,enemies=enemies,bubble=bubble}
 local tag=nil
 if item and item.kind==0 and item.state>=128 and not visualSeen.M then tag='M';visualSeen.M=true
 elseif item and item.kind==1 and item.state>=128 and s.flags==1 and bubble and not visualSeen.F then tag='F';visualSeen.F=true end
 if tag then assert(#visualQueue+#visualRows<2,'Maximum two queued pictures');visualQueue[#visualQueue+1]={tag=tag,snapshot=visualLast}end
end
local function visualBase64(bytes)
 local chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
 local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2);local n=(a<<16)|((b or 0)<<8)|(c or 0)
  out[#out+1]=chars:sub((n>>18)+1,(n>>18)+1);local j=(n>>12)&63;out[#out+1]=chars:sub(j+1,j+1)
  j=(n>>6)&63;out[#out+1]=b and chars:sub(j+1,j+1)or'=';j=n&63;out[#out+1]=c and chars:sub(j+1,j+1)or'='
 end
 return table.concat(out)
end
local function visualFrame()
 if#visualQueue==0 then return end
 local request=table.remove(visualQueue,1);assert(#visualRows<2,'Maximum two actual rendered PNGs')
 assert(visualMode==3,'Actual MMC5 one-KB sprite mode')
 local png=emu.takeScreenshot();assert(type(png)=='string'and png:sub(1,8)=='\137PNG\13\10\26\10','Actual in-memory PNG')
 assert(#png<=65536,'Each PNG at most64KB')
 local height=visualPpu&32~=0 and 16 or 8;local oam,patterns,keys={},{},{}
 for slot=0,63 do
  local at=4*slot;local y=emu.read(at,emu.memType.nesSpriteRam)
  if y<240 then
   local tile=emu.read(at+1,emu.memType.nesSpriteRam);local attr=emu.read(at+2,emu.memType.nesSpriteRam);local x=emu.read(at+3,emu.memType.nesSpriteRam)
   local pattern=height==16 and((tile&1)*4096+(tile&254)*16)or((visualPpu&8~=0 and 4096 or 0)+tile*16)
   local window=pattern//1024;local bank=assert(visualBanks[window],'Observed actual sprite bank write')
   local key=tostring(bank)..'/'..tostring(pattern%1024)..'/'..height
   if not keys[key]and#patterns<16 then
    keys[key]=true;local bytes={};for j=0,(height==16 and 31 or 15)do bytes[#bytes+1]=emu.read(bank*1024+pattern%1024+j,emu.memType.nesChrRom)end
    patterns[#patterns+1]={key=key,bank=bank,offset=pattern%1024,height=height,bytes=bytes}
   end
   if#oam<32 then oam[#oam+1]={slot=slot,x=x,y=y,tile=tile,attributes=attr,bank=bank,pattern_key=key}end
  end
 end
 local palette={};for at=0x3f00,0x3f1f do palette[#palette+1]=emu.read(at,emu.memType.nesPpuDebug)end
 local banks={};for i=0,7 do banks[#banks+1]={window=i,bank=visualBanks[i]}end
 local row={tag=request.tag,frame=frame,Main=updates,PNG_bytes=#png,last_completed=request.snapshot,
  Main_pending=pending~=nil,PPUCTRL=visualPpu,CHR_mode=visualMode,CHR_banks=banks,height=height,oam=oam,patterns=patterns,palette=palette}
 visualRows[#visualRows+1]=row
 print('SMB_NATIVE_IMAGE '..visualBase64(png))
end
'''
END='\nemu.addEventCallback(guard(visualFrame),emu.eventType.endFrame)\n'

@lru_cache(maxsize=1)
def controller(raw,identity=0,mode='mushroom'):
    assert identity==0,'Two-picture qualified Bub route only'
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    old=Previous.controller(raw,identity,mode);text=old;once=Previous.once
    text=once(text,'local function finish(',DECL+'local function finish(')
    text=once(text,'if done then return end;done=true',"if done then return end;if ok then assert(#visualRows==2,'Both rendered item scenes captured')end;done=true")
    text=once(text,'natural_flower=flower','natural_flower=flower,visual=visualRows')
    text=once(text,'local routeStarted=false',OBSERVE+'\nlocal routeStarted=false')
    text=once(text,'pending=nil;updates=updates+1;tick()','pending=nil;updates=updates+1;tick();visualObserve()')
    text+=END
    restored=text[:-len(END)].replace(DECL,'',1).replace(OBSERVE+'\n','',1)
    restored=restored.replace("if done then return end;if ok then assert(#visualRows==2,'Both rendered item scenes captured')end;done=true",'if done then return end;done=true',1)
    restored=restored.replace('natural_flower=flower,visual=visualRows','natural_flower=flower',1).replace('tick();visualObserve()','tick()',1)
    assert restored==old,'Byte-exact functional controls/assertions after removing read-only picture facade'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,identity=0):
    text=controller(raw,identity)
    return dict(ROM_SHA256=PIN,identity=identity,controller_SHA256=sha256(text.encode()).hexdigest(),
        parent_factory_SHA256=PARENT,parent_controller_SHA256=sha256(Previous.controller(raw,identity).encode()).hexdigest(),
        controls_and_assertions_byte_exact_after_observer_removal=True,maximum_images=2,maximum_PNG_bytes=65536,
        output_files=0,gameplay_seeds=0,Mesen_run=False,
        scope='MatureMushroom/hero and matureFlower/M-poweredhero/actualfreebubble; actual enemies recorded if present; max16ROMpatternpairs/32visibleOAMrecords per picture')
