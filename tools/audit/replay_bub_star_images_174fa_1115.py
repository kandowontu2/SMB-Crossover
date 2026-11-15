"""Three passive RAM PNGs over the frozen natural Star controls."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_bub_star_174fa_1115 as Previous
import replay_bub_flower_images_40a_1115 as Pictures

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN
PARENT='e3e7d0fed866697dcc1705e4385bcff1ff98556c32074790d4a2f068507f9e7a'
PICTURES='c1616cddfc30edae8cecdaec3d6e5ac567409c0ed8930fcc8273f91590c0a562'
PLAIN=('2b6a634f89912ebca64dbdfa8faa1ce67635c3547468ce92e7399631849a826d',
       'f6937ce1a4f7f7e986bbe748b520d7dccc9bc26f36ce69234c6d14c49ec26010')
once=Previous.once

SCENES=r'''
local function visualObserve()
 if done or not game or not star then return end
 local s=starState();s.counter=read(Pic.FrameCounter);s.native_attributes=read(Pic.Player_SprAttrib)
 s.counter_phase=(s.counter>>1)&3;s.postcollector=star.post_collector_returns or 0;s.postcredit=star.post_credit_returns or 0
 local a=starActor();local oy=identity==1 and 8 or 0
 visualLast={state=s,item=a,camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos'),
  original_attributes={work(2,0x102+oy),work(2,0x106+oy)},
  native_pose_attributes={work(2,0xc3e6),work(2,0xc3e2)}}
 local tag=nil
 if a and a.kind==2 and a.state>=128 and not star.collector and not visualSeen.S then tag='S'
 elseif star.credit and s.postcredit>=1 and s.postcredit<=20 and s.star>0 then
  if s.counter_phase==0 and not visualSeen.A0 then tag='A0'
  elseif s.counter_phase==2 and not visualSeen.A2 then tag='A2'end
 end
 if tag then
  visualSeen[tag]=true;assert(#visualQueue+#visualRows<3,'Maximum three Star scene requests')
  visualQueue[#visualQueue+1]={tag=tag,snapshot=visualLast}
 end
end
'''

ACK=r'''
 local snap=request.snapshot;local sx=snap.state.x-snap.camera;local sy=snap.state.y
 local hero={};for _,p in ipairs(oam)do
  if p.bank==441 and p.x>=sx-16 and p.x<=sx+32 and p.y>=sy-8 and p.y<=sy+48 then hero[#hero+1]=p end
 end
 assert(#hero>=2,'Actual visible private hero OAM in Star picture')
 row.hero_oam=hero;row.capture_counter=read(Pic.FrameCounter);row.capture_native_attributes=read(Pic.Player_SprAttrib)
 row.capture_original_attributes={work(2,0x102+(identity==1 and 8 or 0)),work(2,0x106+(identity==1 and 8 or 0))}
 row.capture_star=read(Star.ram.StarInvincibleTimer);row.capture_postcredit=star.post_credit_returns or 0
 row.sprite_palette0={palette[17],palette[18],palette[19],palette[20]}
 row.sprite_palette3={palette[29],palette[30],palette[31],palette[32]}
 assert(palette[29]==15 and palette[30]==15 and palette[31]==54 and palette[32]==23,'Actual ground-world sprite palette3 preserved under Star')
 if request.tag=='S'then
  assert(snap.item and snap.item.kind==2 and snap.item.state>=128 and snap.state.star==0,'Mature natural Star before physical collector')
 else
  assert(star.credit and row.capture_star>0 and snap.state.postcredit>=1 and snap.state.postcredit<=20,'Actual active Star after credit within25 workers')
 end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    assert identity in(0,1)and mode=='mushroom'
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    assert sha256(Path(Pictures.__file__).read_bytes()).hexdigest()==PICTURES
    old=Previous.controller(raw,identity,mode);assert sha256(old.encode()).hexdigest()==PLAIN[identity]
    bundle=dict(W.Symbols.bundle(),raw=raw)
    fields={n:W.address(bundle,n)for n in('FrameCounter','Player_SprAttrib')}
    prefix='local Pic='+Previous.Previous.Witness.Base.Previous.lua(fields)+'\n'
    text=prefix+old
    observer=Pictures.OBSERVE
    lo=observer.index('local function visualObserve()');hi=observer.index('local function visualBase64(bytes)',lo)
    observer=observer[:lo]+SCENES+'\n'+observer[hi:]
    observer=once(observer,"#visualRows<2,'Maximum two actual rendered PNGs'","#visualRows<3,'Maximum three actual rendered PNGs'")
    observer=once(observer,' visualRows[#visualRows+1]=row',ACK+'\n visualRows[#visualRows+1]=row')
    text=once(text,'local function finish(',Pictures.DECL+'local function finish(')
    finish="if done then return end;if ok then assert(#visualRows==3,'Mature Star and two active counter-phase pictures')end;done=true"
    text=once(text,'if done then return end;done=true',finish)
    text=once(text,'natural_star=star','natural_star=star,visual=visualRows')
    text=once(text,'local routeStarted=false',observer+'\nlocal routeStarted=false')
    text=once(text,'pending=nil;updates=updates+1;tick()','pending=nil;updates=updates+1;tick();visualObserve()')
    text+=Pictures.END
    restored=text[len(prefix):-len(Pictures.END)].replace(Pictures.DECL,'',1).replace(observer+'\n','',1)
    restored=restored.replace(finish,'if done then return end;done=true',1).replace('natural_star=star,visual=visualRows','natural_star=star',1)
    restored=restored.replace('tick();visualObserve()','tick()',1)
    assert restored==old,'Byte-exact frozen functional controls/assertions after removing only passive picture facade'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,identity=0):
    text=controller(raw,identity)
    bundle=dict(W.Symbols.bundle(),raw=raw);path={}
    for name in('CyclePlayerPalettePreload','CyclePlayerPalette','ResetPalStar'):
        at=W.location(bundle,name);path[name]=dict(PC=W.address(bundle,name),file=at,bytes=raw[at:at+24].hex())
    image=Previous.C.code(raw)
    pattern=bytes.fromhex('a9008de7c38de8c38506');assert image.count(pattern)==1
    return dict(ROM_SHA256=PIN,identity=identity,Lua_SHA256=sha256(text.encode()).hexdigest(),
        parent_Lua_SHA256=PLAIN[identity],parent_factory_SHA256=PARENT,byte_exact_observer_removal=True,
        scenes=['mature Star/hero before pickup','active Star after credit/counter phase0','active Star after credit/counter phase2'],
        maximum_images=3,maximum_PNG_bytes=65536,maximum_total_PNG_bytes=196608,output_files=0,
        actual_MMC5_OAM_PPU_palettes_and_ROM_pattern_bytes=True,native_run=False,
        native_palette_path=path,private_Pair_R3_zero_PC=0xa000+image.index(pattern),
        scope='Source compile/binding/removal only; appearance/flashing requires root actual native pictures')
