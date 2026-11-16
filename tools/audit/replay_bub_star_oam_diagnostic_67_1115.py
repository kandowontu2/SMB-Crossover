"""Passive aggregate shadow/physical OAM diagnostic over frozen1399 controls."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import replay_bub_selected_star_palette_prince_1115 as Frozen

C,R,B,W,PIN=Frozen.C,Frozen.R,Frozen.B,Frozen.W,Frozen.PIN
BASE_SHA='1399fcd0b5a9ad0437ac237d2f42693b8644c8d54b11a094f81be4e74e4914e1'
FACTORY_SHA='f73b20f9c03b6ba2c16f88ece6acf9ea71145c9dbfea2f3887ffdc7e2a60550b'
SLOT=R/'build/smb2-flag-native-1113'
DECL='local starOamDiag={frames={},dma={},dma_seq=0,oamaddr=0}\n'
OBSERVE=r'''
do
 local pendingDma=nil;local lastDma=nil
 local function token(p)
  if not p then return nil end
  return{Main=p.Main,native=p.native,postcredit=p.postcredit,parts=p.parts}
 end
 local function parts(p,kind,page)
  local out={};for _,part in ipairs(p.parts)do
   local at=part.slot*4;local function v(i)return kind=='physical'and emu.read(at+i,emu.memType.nesSpriteRam)or read(page*256+at+i)end
   out[#out+1]={slot=part.slot,y=v(0),tile=v(1),attributes=v(2),x=v(3)}
  end;return out
 end
 local function equal(a,b)
  if#a~=#b then return false end
  for k,x in ipairs(a)do local y=b[k];if x.y~=y.y or x.tile~=y.tile or x.attributes~=y.attributes or x.x~=y.x then return false end end
  return true
 end
 local function anywhere(p,ignoreAttr)
  local out={};local complete=true
  for _,part in ipairs(p.parts)do
   local found=nil
   for slot=0,63 do local at=slot*4
    local y=emu.read(at,emu.memType.nesSpriteRam);local tile=emu.read(at+1,emu.memType.nesSpriteRam)
    local attr=emu.read(at+2,emu.memType.nesSpriteRam);local x=emu.read(at+3,emu.memType.nesSpriteRam)
    if y==part.y and tile==part.tile and x==part.x and(ignoreAttr or attr==part.attributes)then
     found={slot=slot,y=y,tile=tile,attributes=attr,x=x};break
    end
   end
   complete=complete and found~=nil;out[#out+1]=found or false
  end;return complete,out
 end
 local function sample(p)
  local shadow=parts(p,'shadow',2);local physical=parts(p,'physical',0)
  local any,anyParts=anywhere(p,false);local pose,poseParts=anywhere(p,true)
  local retained=nil
  for k=#heroDrawRows,1,-1 do local old=heroDrawRows[k]
   if equal(parts(old,'physical',0),old.parts)then retained={Main=old.Main,native=old.native};break end
  end
  local cpu=emu.getState()
  return{frame=frame,Main=updates,pending_Main=pending~=nil,pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],
   current_native=read(Pic.Player_SprAttrib),token=token(p),shadow=shadow,physical_same_slots=physical,
   shadow_matches_token=equal(shadow,p.parts),physical_matches_token=equal(physical,p.parts),
   exact_anywhere=any,exact_anywhere_parts=anyParts,pose_anywhere=pose,pose_anywhere_parts=poseParts,
   retained_same_slot_match=retained,last_dma=lastDma,oamaddr=starOamDiag.oamaddr}
 end
 local function count(group,p,row)
  local key=tostring(p.native&3);local q=group[key]
  if not q then q={samples=0,shadow_match=0,physical_match=0,exact_anywhere=0,pose_anywhere=0,first=row};group[key]=q end
  q.samples=q.samples+1
  q.shadow_match=q.shadow_match+(row.shadow_matches_token and 1 or 0)
  q.physical_match=q.physical_match+(row.physical_matches_token and 1 or 0)
  q.exact_anywhere=q.exact_anywhere+(row.exact_anywhere and 1 or 0)
  q.pose_anywhere=q.pose_anywhere+(row.pose_anywhere and 1 or 0)
 end
 emu.addMemoryCallback(guard(function(_,value)starOamDiag.oamaddr=value end),emu.callbackType.write,0x2003)
 emu.addMemoryCallback(guard(function(_,value)
  if not game or not star or read(Star.ram.StarInvincibleTimer)==0 or not heroLastDraw then return end
  local p=heroLastDraw;if p.star==0 then return end
  starOamDiag.dma_seq=starOamDiag.dma_seq+1
  pendingDma={seq=starOamDiag.dma_seq,frame=frame,Main=updates,page=value,oamaddr=starOamDiag.oamaddr,
   p=p,consumed=parts(p,'shadow',value)}
  lastDma={seq=pendingDma.seq,frame=frame,Main=updates,page=value,token_Main=p.Main,native=p.native}
 end),emu.callbackType.write,0x4014)
 emu.addMemoryCallback(guard(function()
  local h=StarOamBinding.after
  if not pendingDma or not mapped(h.pc,emu.memType.nesPrgRom,h.offset)then return end
  for i=1,#h.data,2 do assert(read(h.pc+(i-1)//2)==tonumber(h.data:sub(i,i+1),16),'Bound actual post-DMA entry')end
  local d=pendingDma;local row=sample(d.p)
  row.DMA={seq=d.seq,frame=d.frame,Main=d.Main,page=d.page,oamaddr=d.oamaddr,consumed=d.consumed}
  row.consumed_matches_token=equal(d.consumed,d.p.parts)
  row.physical_matches_consumed=equal(row.physical_same_slots,d.consumed)
  count(starOamDiag.dma,d.p,row)
  if not starOamDiag.first_dma_mismatch and(not row.consumed_matches_token or not row.physical_matches_consumed)then starOamDiag.first_dma_mismatch=row end
  pendingDma=nil
 end),emu.callbackType.exec,StarOamBinding.after.pc)
 emu.addEventCallback(guard(function()
  if not game or not star or read(Star.ram.StarInvincibleTimer)==0 or not heroLastDraw then return end
  local p=heroLastDraw;if p.star==0 then return end
  local row=sample(p);count(starOamDiag.frames,p,row)
  if not starOamDiag.first_frame_mismatch and(not row.shadow_matches_token or not row.physical_matches_token)then starOamDiag.first_frame_mismatch=row end
 end),emu.eventType.endFrame)
end
'''


def bindings(raw):
    assert sha256(raw).hexdigest()==PIN
    bundle=dict(W.Symbols.bundle(),raw=raw)
    name='PostDmaMaskEnable';pc=W.address(bundle,name);at=W.location(bundle,name)
    return dict(after=dict(pc=pc,offset=at-16,data=raw[at:at+8].hex()))


@lru_cache(maxsize=1)
def baseline(raw,identity=0):
    assert identity==0 and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FACTORY_SHA
    data=(SLOT/'controller.lua').read_bytes()
    if sha256(data).hexdigest()==BASE_SHA:return data.decode()
    # Root may have replaced its two-file slot with this exact diagnostic.
    # Reverse only our explicit passive additions and authenticate1399 again.
    text=data.decode();prefix='local StarOamBinding='+Frozen.Star.Previous.Witness.Base.Previous.lua(bindings(raw))+'\n'
    if text.startswith(prefix):
        restored=text[len(prefix):].replace(DECL,'',1).replace(OBSERVE+'\n','',1)
        restored=restored.replace('selected_draw_tail=heroDrawRows,star_oam_diagnostic=starOamDiag','selected_draw_tail=heroDrawRows',1)
        if sha256(restored.encode()).hexdigest()==BASE_SHA:return restored
    text=Frozen.controller(raw,identity,images=True)
    assert sha256(text.encode()).hexdigest()==BASE_SHA
    return text


@lru_cache(maxsize=1)
def controller(raw,identity=0):
    old=baseline(raw,identity);cfg=bindings(raw)
    prefix='local StarOamBinding='+Frozen.Star.Previous.Witness.Base.Previous.lua(cfg)+'\n'
    text=prefix+old;once=Frozen.Star.once
    text=once(text,'local function finish(',DECL+'local function finish(')
    text=once(text,'local routeStarted=false',OBSERVE+'\nlocal routeStarted=false')
    text=once(text,'selected_draw_tail=heroDrawRows','selected_draw_tail=heroDrawRows,star_oam_diagnostic=starOamDiag')
    restored=text[len(prefix):].replace(DECL,'',1).replace(OBSERVE+'\n','',1)
    restored=restored.replace('selected_draw_tail=heroDrawRows,star_oam_diagnostic=starOamDiag','selected_draw_tail=heroDrawRows',1)
    assert restored==old,'Exact frozen1399 controls, image assertions and observer restored'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    raw=(SLOT/'candidate.nes').read_bytes();text=controller(raw)
    q=dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),bytes=len(text.encode()),
        baseline_Lua_SHA256=BASE_SHA,bindings=bindings(raw),frozen_controls_and_all_assertions_restored=True,
        per_phase_aggregates_only=True,maximum_phase_first_samples=8,maximum_separate_first_mismatches=2,
        new_PNG_requests=0,inherited_maximum_PNGs=3,output_files=0,game_state_writes=0)
    print('RESULT '+json.dumps(q,sort_keys=True,separators=(',',':')),flush=True)
