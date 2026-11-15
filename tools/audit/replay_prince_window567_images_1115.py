"""Strict graphics567 ordinary Goomba/Mushroom images and accepted pickup."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import compose_prince_window567_1115 as Compose
import current_prince_body_research_ae66_1114 as Current
import compose_dk_private_sprite_window7_1114 as DK
import compose_shared_world_chr_reset_1114 as Reset
import replay_shared_world_sprite_images_1114 as Previous

R,ROM,W,N,Frozen=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.Frozen
PIN=Compose.CANDIDATE
IDENTITIES={'prince':Previous.IDENTITIES['prince']}


@lru_cache(maxsize=1)
def bindings(raw,key='prince'):
    assert key=='prince'and sha256(raw).hexdigest()==PIN
    parent=Compose.inverse(raw);current=Current.normalize(parent,kind='bt-service-ae66')
    reference421=Reset.inverse(DK.inverse(current.reference1daca))
    c=deepcopy(Previous.bindings(reference421,key));c['sha']=PIN
    for hook in c['hooks'].values():
        if'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
    for row in c['records'].values():
        at=16+row['offset'];assert raw[at:at+len(row['bytes'])]==bytes(row['bytes'])
    head,chunks,sizes=Compose.Packet.extract(raw)
    c['prince_cookie']=list(raw[Compose.Packet.COOKIE:Compose.Packet.COOKIE+16])
    c['prince_packet']=dict(cookie=bytes(c['prince_cookie']).hex(),header_SHA256=sha256(head).hexdigest(),
        chunk_SHA256=[sha256(part).hexdigest()for part in chunks],compressed_lengths=list(sizes))
    labels=json.loads((R/'build/prince-actor-1101-v1/native-labels-v153.json').read_text())
    pc=labels['PpNativePickup'];c['private_pickup']=dict(pc=pc,bank=2,bytes=list(chunks[1][pc-0xc800:pc-0xc800+12]))
    bundle=dict(W.Symbols.bundle(),raw=raw)
    for name in('FloateyNum_Control','StarInvincibleTimer'):c['ram'][name]=W.address(bundle,name)
    return c


@lru_cache(maxsize=1)
def controller(raw,key='prince'):
    c=bindings(raw,key);assert sha256(Previous.TEMPLATE.read_bytes()).hexdigest()==Previous.TEMPLATE_SHA
    text=Previous.TEMPLATE.read_text(encoding='utf-8')
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    change("local phase,changedAt='settle',0","local phase,changedAt='settle',0\nlocal pickup")
    change('  shots=shots,first=first,mushroom_birth=birth,events=events,input_changes=inputs,terminal=state(),',
           '  shots=shots,first=first,mushroom_birth=birth,accepted_pickup=pickup,events=events,input_changes=inputs,terminal=state(),')
    change("  scope='Existing graphics observation only; no correct-art, collision, full-stage, performance or pixel-visibility acceptance.'",
           "  scope='Natural graphics567 Goomba/Mushroom and actual accepted pickup; no full-stage or performance claim.'")
    change(" if C.key=='prince'then\n  if phase=='settle'", """ if C.key=='prince'then
  if #shots>=2 then
   assert(r('StarInvincibleTimer')==0,'No natural Star in first Mushroom route')
   setPad(pickup and 0 or 1)
   if pickup and pickup.returned and commits-pickup.commit>=25 and completed-pickup.completed>=25 then
    assert(pickup.accepted and s.prince_hp==pickup.after.prince_hp and s.lives==2,'Actual accepted pickup and living25 return continuation')
    finish(true,'Prince window567 natural images and accepted Mushroom pickup')
   end
   return
  end
  if phase=='settle'""")
    change('hook(C.hooks.GameLoop,function()',r'''emu.addMemoryCallback(guard(function()
 local h=C.private_pickup;local map=emu.convertAddress(h.pc)
 if not map or map.memType~=emu.memType.nesWorkRam or map.address~=h.bank*8192+(h.pc&8191)then return end
 for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact current private pickup')end
 local cpu=emu.getState();local slot=cpu['cpu.x'];local a=actor(slot)
 if #shots<2 or a.flag~=1 or a.id~=46 or a.kind~=0 or a.state<128 then return end
 assert(not pickup,'Single actual Mushroom collector')
 local sp=cpu['cpu.sp'];local ret=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 pickup={slot=slot,before=state(),actor=a,entry_sp=sp,return_pc=ret,return_sp=(sp+2)&255,commit=commits,completed=completed}
 emu.addMemoryCallback(guard(function()
  if not pickup or pickup.returned then return end
  local now=emu.getState();if now['cpu.sp']~=pickup.return_sp then return end
  local flags=now['cpu.ps']or now['cpu.p'];assert(type(flags)=='number','Actual collector return flags')
  pickup.returned=true;pickup.after=state();pickup.carry=flags&1;pickup.floatey_control=r('FloateyNum_Control',slot)
  pickup.erased=r('Enemy_Flag',slot)==0
  pickup.accepted=pickup.carry==1 and pickup.erased and pickup.floatey_control==6
  assert(pickup.accepted,'Actual private pickup C1/nativeerase/floatey6')
 end),emu.callbackType.exec,ret)
end),emu.callbackType.exec,C.private_pickup.pc)
hook(C.hooks.GameLoop,function()''')
    change("target=a;capture('first-natural-mature-Mushroom',a);break", "target=a;capture('first-natural-mature-Mushroom',a);switch('collect',1);break")
    change("  if#shots==2 then finish(true,'Two ordinary current421 world-sprite observations')end",'')
    text='local C='+Previous.Frozen.lua(c)+'\n'+text
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text


def metadata(raw,key='prince'):
    c=bindings(raw,key)
    return dict(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        compiled_menu={k:c[k]for k in('name','slot','cycle','owner','role')},prince_packet=c['prince_packet'],
        identity=key,maximum_images=2,maximum_PNG_bytes=65536,actual_private_pickup_return_PC_SP_Carry=True,
        normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen=False)
