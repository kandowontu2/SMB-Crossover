"""Two passive native RAM PNGs over the frozen current Flower/dash route.

Source qualification compiles this facade only. Screenshots and physical OAM
are observed by root's native run; no source-model screenshot substitutes.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_celeste_flower_local_dash_00bb_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='528c17f0896d79744058ea6941d41b13f2c600d832629b4141ec16b34a646179'
BASE_LUA='05b6e7c41db900ab6bc8827ee4d83136bdd761483ba945b385af0a7a1a5ec976'
NATIVE_REFERENCE='083deff3a20a0d3a2fe10f6a2e5d8c8acf8729348c7ab12c84b2566ed52782a4'
DECL='local visual={pictures={},wall_jump_observed=false}\n'

OBSERVER=r'''
local visualCfg=__VISUAL_CFG__
local visualPpu,visualMode,visualUpper=0,-1,0
local visualBanks={}
for _,at in ipairs({0x2000,0x5101,0x5130,0x5120,0x5121,0x5122,0x5123,0x5124,0x5125,0x5126,0x5127})do
 emu.addMemoryCallback(guard(function(address,value)
  if address==0x2000 then visualPpu=value elseif address==0x5101 then visualMode=value
  elseif address==0x5130 then visualUpper=value&3 else visualBanks[address-0x5120]=(visualUpper<<8)|value end
 end),emu.callbackType.write,at)
end
local function visualPrivate()
 local q={state=state()};for name,at in pairs(visualCfg.ram)do q[name]=read(at)end;return q
end
emu.addMemoryCallback(guard(function()
 if visual.wall_jump_observed or r('CmTier')~=1 then return end
 local h=visualCfg.wall;local mapped=emu.convertAddress(h.pc)
 if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=h.offset then return end
 for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Actual current CmWallJump')end
 local cpu=emu.getState();local q={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],before=visualPrivate()}
 visual.wall_jump_observed=true;visual.wall_jump=q
 returning(function(t)q.returned={PC=t.pc,SP=t.sp,after=visualPrivate()}end)
end),emu.callbackType.exec,visualCfg.wall.pc)
local function visualBase64(bytes)
 local chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
 local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2);local n=(a<<16)|((b or 0)<<8)|(c or 0)
  for _,shift in ipairs({18,12})do local j=(n>>shift)&63;out[#out+1]=chars:sub(j+1,j+1)end
  local j=(n>>6)&63;out[#out+1]=b and chars:sub(j+1,j+1)or'='
  j=n&63;out[#out+1]=c and chars:sub(j+1,j+1)or'='
 end
 return table.concat(out)
end
local function visualFrame()
 if stopped or not menuDone or not active()or#visual.pictures>=2 then return end
 local a=target(1);local tag
 if#visual.pictures==0 then
  if stock.mature and not stock.collected and a and a.state>=128 then tag='mature Flower and small Celeste' end
 elseif dash.started and dash.moved and r('CmState')==6 and r('CmDashTimer')>0 then tag='active earned dash and small Celeste'end
 if not tag then return end
 assert(r('PlayerSize')==1 and r('CmTier')>=1 and visualMode==3,'Actual small Celeste/MMC5 sprite mode')
 local s=state();local camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc');local heroX,heroTop=s.x-camera,s.y+16
 assert(heroX>=0 and heroX<=240 and heroTop>=0 and heroTop<240,'Visible physical small hero')
 local height=visualPpu&32~=0 and 16 or 8;local oam,hero,patterns,keys={},{},{},{}
 for slot=0,63 do
  local at=4*slot;local y=emu.read(at,emu.memType.nesSpriteRam)
  if y<240 then
   local tile=emu.read(at+1,emu.memType.nesSpriteRam);local attr=emu.read(at+2,emu.memType.nesSpriteRam);local x=emu.read(at+3,emu.memType.nesSpriteRam)
   local pattern=height==16 and((tile&1)*4096+(tile&254)*16)or((visualPpu&8~=0 and 4096 or 0)+tile*16)
   local bank=assert(visualBanks[pattern//1024],'Observed actual sprite bank publication')
   local key=tostring(bank)..'/'..tostring(pattern%1024)..'/'..height
   local q={slot=slot,x=x,y=y,rendered_y=y+1,tile=tile,attributes=attr,bank=bank,pattern_key=key}
   if#oam<32 then oam[#oam+1]=q end
   if bank>=740 and bank<=743 and x+8>=heroX-12 and x<=heroX+28 and y+height>=heroTop-8 and y+1<=heroTop+24 then hero[#hero+1]=q end
   if not keys[key]and#patterns<16 then
    keys[key]=true;local bytes={};for j=0,(height==16 and 31 or 15)do bytes[#bytes+1]=emu.read(bank*1024+pattern%1024+j,emu.memType.nesChrRom)end
    patterns[#patterns+1]={key=key,bank=bank,offset=pattern%1024,height=height,bytes=bytes}
   end
  end
 end
 assert(#hero>0,'Actual visible CM owning OAM near PlayerY+16')
 local palette={};for at=0x3f00,0x3f1f do palette[#palette+1]=emu.read(at,emu.memType.nesPpuDebug)end
 local banks={};for i=0,7 do banks[#banks+1]={window=i,bank=visualBanks[i]}end
 local png=emu.takeScreenshot()
 assert(type(png)=='string'and png:sub(1,8)=='\137PNG\13\10\26\10'and#png<=65536,'Actual bounded in-memory PNG')
 visual.pictures[#visual.pictures+1]={tag=tag,frame=frame,Main=mainReturns,state=s,item=a,PNG_bytes=#png,
  Main_pending=pendingMain~=nil,camera=camera,hero_screen_x=heroX,expected_small_rendered_top=heroTop,
  PPUCTRL=visualPpu,CHR_mode=visualMode,CHR_banks=banks,height=height,hero_oam=hero,oam=oam,patterns=patterns,palette=palette,private=visualPrivate()}
 print('SMB_NATIVE_IMAGE '..visualBase64(png))
end
emu.addEventCallback(guard(visualFrame),emu.eventType.endFrame)
'''


def picture_bindings(raw):
    b=Current.bundle(raw);pc,at=W.address(b,'CmWallJump'),W.location(b,'CmWallJump');bank=(at-16)//8192
    return dict(wall=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192])),
        ram={name:W.address(b,name)for name in('CmGfxBank','CmPalette','CmFootPhysics','CmWallKick','CmStaminaHi','CmStaminaLo','Up_Down_Buttons','Left_Right_Buttons')})


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    base=Previous.controller(raw,'flower');assert digest(base.encode())==BASE_LUA
    observer=OBSERVER.replace('__VISUAL_CFG__',Text.lua(picture_bindings(raw)))
    edits=[('if stopped then return end;stopped=true;buttons={}',"if stopped then return end;if ok then assert(#visual.pictures==2,'Both actual RAM pictures')end;stopped=true;buttons={}"),
        ('M=M,stock=stock,dash=dash,readback=readback','M=M,stock=stock,dash=dash,readback=readback,visual=visual')]
    text=DECL+base
    for old,new in edits:assert text.count(old)==1;text=text.replace(old,new,1)
    text+='\n'+observer
    restored=text[len(DECL):-(len(observer)+1)]
    for old,new in reversed(edits):assert restored.count(new)==1;restored=restored.replace(new,old,1)
    assert restored==base,'Picture observer removal recovers exact native-qualified functional controller'
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    LuaRuntime().compile(text);return text


def functional_receipt(receipt):
    """Remove only the new visual field before comparing native083deff."""
    restored=deepcopy(receipt);restored.pop('visual',None);return restored


def metadata(raw,key='flower'):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,factory_SHA256=digest(Path(__file__).read_bytes()),controller_SHA256=digest(text.encode()),
        parent_factory_SHA256=BASE_SHA,parent_controller_SHA256=BASE_LUA,parent_native_receipt_SHA256=NATIVE_REFERENCE,
        picture_bindings=picture_bindings(raw),controls_and_assertions_byte_exact_after_observer_removal=True,
        only_new_receipt_field='visual',maximum_images=2,maximum_PNG_bytes_each=65536,maximum_OAM_records_each=32,maximum_pattern_pairs_each=16,
        output_files=0,gameplay_seeds=0,Mesen_run=False,actual_rendered_PNGs=False,
        scope='Compile/restoration only. Native endFrame matureFlower+smallCM and moved activeDash+smallCM, physical OAM near PlayerY+16/palette/observed CHR banks; optional one natural tier1 WallJump entry+return, not a success gate')


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
