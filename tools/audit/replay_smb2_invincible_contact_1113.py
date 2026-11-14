"""Separate UI-earned Inv1 ground Goomba contact; real readonly collision boxes."""
from hashlib import sha256
import json
from pathlib import Path

import replay_smb2_cheat_cold_native_1113 as Full

C=Full.C
W=C.W
FULL_SOURCE='fd5f76bf58f00478e31b181396ee1b33cf40a65ae8d5e40297c462f043f810f7'
FULL_LUA='9f693d9f667bb92bda9f4b8ffb060a7a1b550486e5e12568f67303b00b23f625'
LUA_SHA='da1fd6ad6bb4bab273ec638d84186b50204602f59e400f659aaf1c97eb9226d9'


DRIVER=r'''
local function drive()
 local s=contactSnapshot()
 assert(r('SelectedCharacter')==25 and s.variant==1 and s.ready==178,'Actual live SMB2 Luigi')
 assert(s.cheat==1 and s.star==0,'Only real UI Inv1, never Star')
 assert(s.health==31 and s.lives==2,'Inv1 keeps original health31 and both lives')
 assert(s.world==0 and s.level==0 and s.engine==8,'Ordinary active1-1 contact scope')
 assert(updates<600,'Bounded ordinary walk-through contact prefix')
 if not contact.opening then contact.opening=s end
 if s.x<370 then pad=1;contact.post_updates=0;return end
 pad=0
 assert(contact.positive_contacts>0 and contact.first_overlap,'Actual carry-confirmed live Goomba overlap')
 assert(s.x>contact.first_overlap.enemy.x+20,'Ordinary controls pass the actual enemy contact position')
 assert(s.air==0,'Grounded walk-through, no jump or stomp')
 contact.post_updates=contact.post_updates+1
 if contact.post_updates>=30 then
  contact.finish=s
  finish(true,'UI-earned Inv1 walks through a real Goomba; native boxes overlap, health31/Star0 and30quiet updates');return
 end
end
'''


OBSERVERS=r'''
for _,h in ipairs(contactHooks)do for i=1,#h.hex,2 do
 assert(emu.read(h.offset+(i-1)//2,emu.memType.nesPrgRom)==tonumber(h.hex:sub(i,i+1),16),'Exact native contact observer preimage')
end end
emu.addMemoryCallback(guard(function()
 if not game or not contactMapped(contactPC,contactOffset)then return end
 local c=emu.getState();local slot=c['cpu.x'];if slot<0 or slot>=6 then return end
 local a=contactActor(slot)
 if a.flag~=1 or a.id~=6 or a.state&32~=0 then return end
 assert((c['cpu.ps']or c['cpu.p'])&1==1,'Actual PlayerCollisionCore carry confirmed by native branch')
 local offset=4*(slot+1)
 assert(c['cpu.y']==offset and read(contactFields.R6)==offset,'Actual native Goomba bbox offset')
 local p,e=contactBox(0),contactBox(offset)
 assert(p.left<=p.right and p.top<=p.bottom and e.left<=e.right and e.top<=e.bottom,'Nonwrapping visible native boxes')
 local dx=math.min(p.right,e.right)-math.max(p.left,e.left)
 local dy=math.min(p.bottom,e.bottom)-math.max(p.top,e.top)
 assert(dx>=0 and dy>=0,'Native carry and published rectangle intersection agree')
 contact.touch_contacts=contact.touch_contacts+1
 if dx<=0 or dy<=0 then return end
 local s=contactSnapshot()
 assert(s.health==31 and s.lives==2 and s.cheat==1 and s.star==0 and s.air==0,'Real live ground contact is protected without Star')
 contact.positive_contacts=contact.positive_contacts+1
 if not contact.first_overlap then
  contact.first_overlap={s=s,enemy=a,player_box=p,enemy_box=e,overlap_width=dx,overlap_height=dy,
   cpu_carry=true,slot=slot,camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')}
 end
end),emu.callbackType.exec,contactPC)
'''


def once(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after,1)


def bindings(raw):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    b=dict(W.Symbols.bundle(),raw=raw)
    names=('CheatInvincible','StarInvincibleTimer','Enemy_Y_Position','EnemyOffscrBitsMasked',
           'Enemy_BoundBoxCtrl','BoundingBox_UL_Corner','BoundingBox_LR_Corner','R6','S2Air','S2VX')
    fields={n:W.address(b,n)for n in names}
    assert fields['BoundingBox_LR_Corner']==fields['BoundingBox_UL_Corner']+2
    start,end=W.location(b,'PlayerEnemyCollision'),W.location(b,'CheckForPUpCollision')
    pc,at=W.address(b,'CheckForPUpCollision'),end
    core=W.address(b,'PlayerCollisionCore');obj=W.address(b,'ObjectOffset')
    body=raw[start:end]
    needle=b'\x20'+core.to_bytes(2,'little')+bytes((0xa6,obj))
    assert body.count(needle)==1
    i=body.index(needle)+len(needle)
    assert body[i]==0xb0
    delta=body[i+1]if body[i+1]<128 else body[i+1]-256
    assert W.address(b,'PlayerEnemyCollision')+i+2+delta==pc
    enemy_id=W.address(b,'Enemy_ID')
    first=(bytes((0xb4,enemy_id))if enemy_id<256 else bytes((0xbc,))+enemy_id.to_bytes(2,'little'))
    assert raw[at:at+len(first)]==first
    hooks=[dict(offset=at-16,hex=raw[at:at+12].hex()),
           dict(offset=start-16,hex=body.hex())]
    return fields,hooks,pc,at-16


def rebound(raw):
    assert sha256(Path(Full.__file__).read_bytes()).hexdigest()==FULL_SOURCE
    original=Full.controller(raw);assert sha256(original.encode()).hexdigest()==FULL_LUA
    fields,hooks,pc,at=bindings(raw)
    lua=Full.Previous.Frozen.C.Owner.lua
    declaration='local contactFields='+lua(fields)+'\nlocal contactHooks='+lua(hooks)+'\n'
    declaration+=f'local contactPC,contactOffset={pc},{at}\n'
    declaration+=r'''local contact={positive_contacts=0,touch_contacts=0,post_updates=0,scope='UIInv1 ground Goomba contact only'}
local function contactSnapshot()
 local s=state();s.cheat=read(contactFields.CheatInvincible);s.star=read(contactFields.StarInvincibleTimer)
 s.air=read(contactFields.S2Air);s.vx=read(contactFields.S2VX);return s
end
local function contactBox(offset)
 local at=contactFields.BoundingBox_UL_Corner+offset
 return{left=read(at),top=read(at+1),right=read(at+2),bottom=read(at+3)}
end
local function contactActor(slot)
 return{slot=slot,flag=read(F.Enemy_Flag+slot),id=read(F.Enemy_ID+slot),state=read(F.Enemy_State+slot),
 x=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot),y=read(contactFields.Enemy_Y_Position+slot),
 offscreen=read(contactFields.EnemyOffscrBitsMasked+slot),box_control=read(contactFields.Enemy_BoundBoxCtrl+slot)}
end
local function contactMapped(pc,offset)
 local a=emu.convertAddress(pc);return a and a.memType==emu.memType.nesPrgRom and a.address==offset
end
'''
    text=once(original,'local function finish(ok,why)',declaration+'local function finish(ok,why)')
    text=once(text,'cold_gate=coldTrace,physical_frames=','cold_gate=coldTrace,contact=contact,physical_frames=')
    text=once(text,'partial_endpoint=false,full_stage=ok','partial_endpoint=true,full_stage=false')
    text=once(text,'local function drive()','local function traversalDrive()')
    marker='-- Observe every actual GameLoop return, including the native catch-up caller.'
    text=once(text,marker,DRIVER+'\n'+marker)
    text+='\n'+OBSERVERS
    restored=text[:-len('\n'+OBSERVERS)]
    restored=restored.replace(DRIVER+'\n'+marker,marker,1).replace('local function traversalDrive()','local function drive()',1)
    restored=restored.replace('partial_endpoint=true,full_stage=false','partial_endpoint=false,full_stage=ok',1)
    restored=restored.replace('cold_gate=coldTrace,contact=contact,physical_frames=','cold_gate=coldTrace,physical_frames=',1)
    restored=restored.replace(declaration,'',1)
    assert restored==original,'Frozen full replay changed outside the declared separate contact fork'
    return text


def controller(raw):
    text=rebound(raw)
    Full.Previous.C.D.C.Owner.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(w not in text for w in('emu.write','emu.setState','io.open','takeScreenshot','saveState','loadState'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw):
    text=controller(raw)
    fields,hooks,pc,at=bindings(raw)
    return dict(ROM_SHA256=C.CANDIDATE,controller_SHA256=sha256(text.encode()).hexdigest(),
        full_factory_SHA256=FULL_SOURCE,full_controller_SHA256=FULL_LUA,
        native_contact_PC=pc,native_contact_PRG_offset=at,
        observer_preimages_SHA256=sha256(json.dumps(hooks,sort_keys=True).encode()).hexdigest(),
        contact_fields=fields,separate_contact_scope=True,
        actual_PlayerCollisionCore_carry_and_positive_native_box_intersection_required=True,
        real_UI_Inv1_opening_unchanged=True,full_stage=False,
        health31_lives2_Star0_grounded_walk_and30quiet_updates_required=True,
        actor_position_health_ability_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    parent,_=C.Owner.proposal(C.Owner.D.C.Owner.NIGHTLY.read_bytes());raw,_=C.proposal(parent)
    print(json.dumps(metadata(raw),separators=(',',':')),flush=True)
