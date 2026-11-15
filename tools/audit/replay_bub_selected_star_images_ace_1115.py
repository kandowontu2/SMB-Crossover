"""Three RAM pictures tied to actual completed selected-player OAM draws."""
from functools import lru_cache
from hashlib import sha256
import json

import replay_bub_selected_star_palette_ace_1115 as F

C,R,ROM,B,W,N,PIN=F.C,F.R,F.ROM,F.B,F.W,F.N,F.PIN
DECL='local heroPending,heroLastDraw=nil,nil;local heroDrawRows={}\n'
OBSERVE=r'''
emu.addMemoryCallback(guard(function()
 if not game or r('SelectedCharacter')~=39 or not mapped(HeroDraw.entry,emu.memType.nesWorkRam,HeroDraw.offset)then return end
 local c=emu.getState();if c['cpu.y']~=(identity==1 and 8 or 0)then return end
 assert(c['cpu.x']==(identity==1 and 0x42 or 0x2e),'Actual selected source actor Pair caller')
 assert(not heroPending,'One selected hero Pair in flight')
 local y=c['cpu.y'];local sp=c['cpu.sp'];local ret=read(0x101+sp)+256*read(0x102+sp)+1
 assert(ret==HeroDraw.after,'Actual selected Pair return operand')
 heroPending={Main=updates,entry_SP=sp,return_SP=sp+2,native=read(Pic.Player_SprAttrib),
  star=read(Star.ram.StarInvincibleTimer),postcredit=star and(star.post_credit_returns or 0)or 0,
  original={work(2,0x102+y),work(2,0x106+y)},writes={}}
end),emu.callbackType.exec,HeroDraw.entry)
for slot=0,63 do
 local at=0x202+4*slot
 emu.addMemoryCallback(guard(function(address,value)
  if not heroPending then return end
  local p=heroPending;local k=#p.writes+1;assert(k<=2,'Only two selected Pair OAM attribute stores')
  local want=p.original[k]
  if p.star>0 then want=(want&252)|(p.native&3)
  elseif identity==0 and want&3==3 then want=want&252 end
  assert(value==(want&243),'Actual selected hardware-shadow palette/upper attribute bits')
  p.writes[k]={slot=(address-0x202)//4,attributes=value}
 end),emu.callbackType.write,at)
end
emu.addMemoryCallback(guard(function()
 if not heroPending or not mapped(HeroDraw.after,emu.memType.nesWorkRam,HeroDraw.after_offset)then return end
 local c=emu.getState();local p=heroPending;if c['cpu.sp']~=p.return_SP then return end
 assert(#p.writes==2 and read(Pic.Player_SprAttrib)==p.native,'Completed selected Pair and stable native palette')
 p.parts={}
 for _,part in ipairs(p.writes)do
  local at=0x200+part.slot*4
  p.parts[#p.parts+1]={slot=part.slot,y=read(at),tile=read(at+1),attributes=read(at+2),x=read(at+3)}
 end
 p.original_after={work(2,0x102+(identity==1 and 8 or 0)),work(2,0x106+(identity==1 and 8 or 0))}
 assert(p.original[1]==p.original_after[1]and p.original[2]==p.original_after[2],'Original hero attributes unchanged')
 heroLastDraw=p;heroDrawRows[#heroDrawRows+1]=p;if#heroDrawRows>8 then table.remove(heroDrawRows,1)end
 heroPending=nil
end),emu.callbackType.exec,HeroDraw.after)
'''
PREFLIGHT=r'''
 if request.tag~='S'then
  local want=request.tag=='A0'and 0 or 2;local matched=nil
  -- Physical OAM can lag the newest completed Main. Match the exact two
  -- selected parts (including slots/tile/XY) to a completed real draw token;
  -- do not equate a later native cycle write with already DMA'd output.
  for k=#heroDrawRows,1,-1 do
   local p=heroDrawRows[k]
   if p.star>0 and(p.native&3)==want and p.postcredit>=1 and p.postcredit<=25 then
    local equal=true
    for _,part in ipairs(p.parts)do
     local at=part.slot*4
     equal=equal and emu.read(at,emu.memType.nesSpriteRam)==part.y
      and emu.read(at+1,emu.memType.nesSpriteRam)==part.tile
      and emu.read(at+2,emu.memType.nesSpriteRam)==part.attributes
      and emu.read(at+3,emu.memType.nesSpriteRam)==part.x
    end
    if equal then matched=p;break end
   end
  end
  if not matched then visualSeen[request.tag]=nil;return end
  request.actual_hero_draw=matched
 end
'''
ACK=r'''
 if request.tag~='S'then
  local p=assert(request.actual_hero_draw,'Actual DMA-selected completed hero draw')
  local want=request.tag=='A0'and 0 or 2
  assert((p.native&3)==want and#p.parts==2,'Distinct actual native selected palette phase')
  for _,part in ipairs(p.parts)do assert((part.attributes&3)==want,'Physical hero follows consumed native0587 lowbits')end
  row.actual_selected_hero_draw=p
 end
'''


@lru_cache(maxsize=2)
def controller(raw,identity=0):
    old=F.controller(raw,identity,images=True)
    image=C.code(raw);entry,after=0xbdc9,0xbd5f
    assert image[after-0xa000:after-0xa000+4]==bytes.fromhex('4ce2b3ea')
    cfg=dict(entry=entry,offset=3*8192+(entry&8191),after=after,after_offset=3*8192+(after&8191))
    prefix='local HeroDraw='+F.Star.Previous.Witness.Base.Previous.lua(cfg)+'\n'
    text=prefix+old;once=F.Star.once
    text=once(text,'local function finish(',DECL+'local function finish(')
    text=once(text,'local routeStarted=false',OBSERVE+'\nlocal routeStarted=false')
    a="if s.counter_phase==0 and not visualSeen.A0"
    aa="if heroLastDraw and(heroLastDraw.native&3)==0 and not visualSeen.A0"
    b="elseif s.counter_phase==2 and not visualSeen.A2"
    bb="elseif heroLastDraw and(heroLastDraw.native&3)==2 and not visualSeen.A2"
    text=once(text,a,aa);text=once(text,b,bb)
    marker=" assert(visualMode==3,'Actual MMC5 one-KB sprite mode')"
    text=once(text,marker,PREFLIGHT+marker)
    marker2=' visualRows[#visualRows+1]=row'
    text=once(text,marker2,ACK+'\n'+marker2)
    text=once(text,'visual=visualRows','visual=visualRows,selected_draw_tail=heroDrawRows')
    restored=text[len(prefix):].replace(DECL,'',1).replace(OBSERVE+'\n','',1)
    restored=restored.replace(aa,a,1).replace(bb,b,1).replace(PREFLIGHT,'',1).replace(ACK+'\n','',1)
    restored=restored.replace('visual=visualRows,selected_draw_tail=heroDrawRows','visual=visualRows',1)
    assert restored==old,'Exact candidate functional body and prior passive picture facade restored'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def metadata(raw):
    return dict(ROM_SHA256=PIN,controllers=[dict(identity=i,Lua_SHA256=sha256(controller(raw,i).encode()).hexdigest(),
        bytes=len(controller(raw,i).encode()))for i in(0,1)],maximum_RAM_PNGs=3,
        maximum_PNG_bytes=196608,physical_OAM_matches_actual_completed_Pair_tokens=True,
        exact_frozen_controls_and_assertions_restored=True,output_files=0)


if __name__=='__main__':
    raw,_=C.proposal(C.load_current());q=metadata(raw)
    print('RESULT '+json.dumps(q,sort_keys=True,separators=(',',':')),flush=True)
