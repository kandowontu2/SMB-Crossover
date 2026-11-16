"""Passive native two-live-ball RAM pictures; source compiles only."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_weapon_owner_twoshot_a2_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,C=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.C
BASE_SHA='3944307fe088cc184f8ec82f039140a8c7b80f676bf262f80db53c80298bebae'
BASE_LUA='0b1ead0c3858dd049acf01e6b940264d6aed02990a942fa96e0299ac0a33f6ae'
DECL='local visual={pictures={}}\n'
OBSERVER=r'''
local visualPpu,visualMode,visualUpper=0,-1,0;local visualBanks={}
for _,at in ipairs({0x2000,0x5101,0x5130,0x5120,0x5121,0x5122,0x5123,0x5124,0x5125,0x5126,0x5127})do
 emu.addMemoryCallback(guard(function(address,value)
  if address==0x2000 then visualPpu=value elseif address==0x5101 then visualMode=value
  elseif address==0x5130 then visualUpper=value&3 else visualBanks[address-0x5120]=(visualUpper<<8)|value end
 end),emu.callbackType.write,at)
end
local function visualBase64(bytes)
 local chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2);local n=(a<<16)|((b or 0)<<8)|(c or 0)
  for _,shift in ipairs({18,12})do local j=(n>>shift)&63;out[#out+1]=chars:sub(j+1,j+1)end
  local j=(n>>6)&63;out[#out+1]=b and chars:sub(j+1,j+1)or'=';j=n&63;out[#out+1]=c and chars:sub(j+1,j+1)or'='
 end
 return table.concat(out)
end
emu.addEventCallback(guard(function()
 if stopped or not menuDone or not shots or#visual.pictures>=2 or r('SelectedCharacter')~=41 or r('GameEngineSubroutine')~=8 then return end
 local a,b=ball(0),ball(1);if a.state~=1 or b.state~=1 then return end
 if#visual.pictures==1 and steps<visual.pictures[1].step+4 then return end
 assert(visualMode==3,'Actual MMC5 sprite mode')
 local camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc');local height=visualPpu&32~=0 and 16 or 8
 local oam,patterns,keys,near={},{},{},{{},{}}
 for slot=0,63 do
  local at=4*slot;local y=emu.read(at,emu.memType.nesSpriteRam)
  if y<240 then
   local tile=emu.read(at+1,emu.memType.nesSpriteRam);local attr=emu.read(at+2,emu.memType.nesSpriteRam);local x=emu.read(at+3,emu.memType.nesSpriteRam)
   local pattern=height==16 and((tile&1)*4096+(tile&254)*16)or((visualPpu&8~=0 and 4096 or 0)+tile*16)
   local bank=assert(visualBanks[pattern//1024],'Actual observed sprite bank')
   local key=tostring(bank)..'/'..tostring(pattern%1024)..'/'..height
   local row={slot=slot,x=x,y=y,rendered_y=y+1,tile=tile,attributes=attr,bank=bank,pattern_key=key}
   if#oam<32 then oam[#oam+1]=row end
   for i,e in ipairs({a,b})do if math.abs(x-(e.x-camera))<=12 and math.abs(y+1-e.y)<=20 then near[i][#near[i]+1]=row end end
   if not keys[key]and#patterns<24 then
    keys[key]=true;local bytes={};for j=0,(height==16 and 31 or 15)do bytes[#bytes+1]=emu.read(bank*1024+pattern%1024+j,emu.memType.nesChrRom)end
    patterns[#patterns+1]={key=key,bank=bank,offset=pattern%1024,height=height,bytes=bytes}
   end
  end
 end
 local palette={};for at=0x3f00,0x3f1f do palette[#palette+1]=emu.read(at,emu.memType.nesPpuDebug)end
 local banks={};for i=0,7 do banks[#banks+1]={window=i,bank=visualBanks[i]}end
 local png=emu.takeScreenshot();assert(type(png)=='string'and png:sub(1,8)=='\137PNG\13\10\26\10'and#png<=65536,'Actual bounded RAM PNG')
 visual.pictures[#visual.pictures+1]={frame=frame,Main=mains,step=steps,state=state(),balls={a,b},camera=camera,near_ball_oam=near,oam=oam,
  patterns=patterns,palette=palette,PPUCTRL=visualPpu,CHR_mode=visualMode,CHR_banks=banks,sprite_height=height,PNG_bytes=#png}
 print('SMB_NATIVE_IMAGE '..visualBase64(png))
end),emu.eventType.endFrame)
'''

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    base=Previous.controller(raw,key);assert H(base.encode())==BASE_LUA
    edits=[('if stopped then return end;stopped=true;buttons={}',"if stopped then return end;if ok then assert(#visual.pictures==2,'Both actual two-live-ball RAM pictures')end;stopped=true;buttons={}"),
        ('item=item,two_shot=shots,route=route,','item=item,two_shot=shots,route=route,visual=visual,')]
    text=DECL+base
    for old,new in edits:assert text.count(old)==1;text=text.replace(old,new,1)
    text+='\n'+OBSERVER
    restored=text[len(DECL):-(len(OBSERVER)+1)]
    for old,new in reversed(edits):assert restored.count(new)==1;restored=restored.replace(new,old,1)
    assert restored==base
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    LuaRuntime().compile(text);return text

def functional_receipt(receipt):
    q=deepcopy(receipt);q.pop('visual',None);return q

def metadata(raw,key='flower'):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(text.encode()),parent_factory_SHA256=BASE_SHA,
        parent_controller_SHA256=BASE_LUA,body_and_controls_exact_after_observer_removal=True,only_new_receipt_field='visual',
        maximum_images=2,maximum_PNG_bytes_each=65536,maximum_OAM_records_each=32,maximum_pattern_pairs_each=24,
        source_compile_only=True,screenshot_executed=False,gameplay_seeds=0,output_files=0,Mesen_run=False,
        scope='Two actual native endFrame RAM PNGs with two live fireball slots four original steps apart, observed OAM/CHR/palette. Proximity candidates are passive evidence, not automatic projectile-art attribution or4x4 art claim.')

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
