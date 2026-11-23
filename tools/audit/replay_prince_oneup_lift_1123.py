"""Ordinary Prince 1-UP lift controls accepting an authenticated memory overlay.

No image output, Mesen invocation, game-state writes or retained receipts.
The composer supplies the exact four decoded streams and its strict patch list.
"""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import probe_prince_hidden_life_current_1123 as P
import compose_dkjr_shinobi_1123 as DK
import compose_shinobi_pickups_1123 as Shinobi
import install_mega_giant_item_semantics_1123 as Mega

H,W,N,Engine=P.H,P.W,P.N,P.Engine
PIN=Mega.CANDIDATE
CHANGES=((0x6f6,3),(0x6fc,31),(0x13d1,16))


def original(image):
    assert H(image)==PIN
    parent=Shinobi.recover_parent(DK.recover_parent(Mega.recover_parent(image)))
    assert H(parent)==P.CURRENT
    binding=P.authenticate(parent)
    assert P.Packet.extract(image)==P.Packet.extract(parent)
    return parent,binding


def baseline_controller(image):
    parent,_=original(image)
    text=P.controller(parent,'cap')
    assert text.count(P.CURRENT)==2
    text=text.replace(P.CURRENT,PIN)
    P.Base.LuaRuntime().compile(text)
    return text


def patch_fields(row):
    offset=row.get('file_offset',row.get('offset'))
    old=bytes.fromhex(row.get('old_hex',row.get('preimage','')))
    new=bytes.fromhex(row.get('new_hex',row.get('replacement','')))
    assert isinstance(offset,int)and len(old)==len(new)>0
    return offset,old,new


def authenticate(image,overlay):
    assert overlay['passed'] is True and overlay['parent_SHA256']==PIN
    assert H(image)==overlay['expected_memory_only_SHA256']
    parent=bytearray(image);seen=set()
    allowed=[(P.Packet.CHR+page*1024,1024)for page in P.Packet.PAGES]+[(P.Packet.COOKIE,16)]
    for row in overlay['patches']:
        at,old,new=patch_fields(row)
        assert any(start<=at and at+len(new)<=start+length for start,length in allowed),'Prince carriers/cookie only'
        domain=set(range(at,at+len(new)));assert not seen&domain;seen|=domain
        assert parent[at:at+len(new)]==new
        parent[at:at+len(old)]=old
    parent=bytes(parent);assert H(parent)==PIN
    _,prior=original(parent);before=P.Packet.extract(parent)[1]
    decoded=tuple(map(bytes,overlay['decoded']));assert len(decoded)==4
    import compose_prince_oneup_lift_1123 as Composer
    extracted,_,actual_cookie,_=Composer.extract(image)
    assert tuple(extracted)==decoded and actual_cookie.hex()==overlay['cookie'],'Actual four-stream payload/cookie'
    assert tuple(map(len,decoded[:3]))==tuple(map(len,before))
    assert decoded[1:3]==before[1:3],'Metadata/state unchanged'
    changed={i for i,(a,b)in enumerate(zip(before[0],decoded[0]))if a!=b}
    owned={i for at,size in CHANGES for i in range(at,at+size)}
    assert changed and changed<=owned and all(any(i in changed for i in range(at,at+size))for at,size in CHANGES)
    assert 1<=len(decoded[3])<=1024
    cookie=overlay['cookie'];assert len(cookie)==32 and bytes.fromhex(cookie)[:3]==P.Packet.PREFIX
    assert image[P.Packet.COOKIE:P.Packet.COOKIE+16].hex()==cookie
    lift=overlay.get('lift',dict(id=37,left=1008,width=32,initial_top=192))
    assert tuple(lift[k]for k in('id','left','width','initial_top'))==(37,1008,32,192)
    return parent,decoded,dict(prior,candidate=H(image),cookie=cookie,decoded_SHA256=list(map(H,decoded)),
        RAM3_changes=CHANGES,patch_count=len(overlay['patches']),lift=lift)


LIFT_V1=r'''
stock.lift={placement={stage='1-1',left=1008,center=1024,initial_top=192,width=32,id=37},samples={},contacts=0,moving_contacts=0,attempts=0}
local function liftActor()
 for i=0,5 do
  local a=stockActor(i)
  if a.flag==1 and a.id==37 and a.state==0 and a.high==1 and a.x==1008 then
   a.carry=read(LIFT.ram.PlatformCollisionFlag+i);a.box=read(LIFT.ram.Enemy_BoundBoxCtrl+i)
   assert(a.box==5,'Actual32px native lift rectangle');return a
  end
 end
end
local function liftObserve(s)
 local a=liftActor();if not a then return end
 local l=stock.lift;l.seen=l.seen or{state=s,actor=a}
 local riding=a.carry==a.slot and s.ground==0 and s.y+32==a.y and math.abs(s.foot-a.y)<=1
 l.current=riding;l.actor=a
 if riding and l.last_return~=stock.prince_returns then
  l.contacts=l.contacts+1
  if l.last_y and a.y~=l.last_y then l.moving_contacts=l.moving_contacts+1 end
  l.last_y=a.y;l.last_return=stock.prince_returns
  if #l.samples<20 then l.samples[#l.samples+1]={state=s,actor=a}end
 end
end
stockHook(LIFT.constructor,function(cpu)
 local i=cpu['cpu.x'];if i>=6 then return end
 local a=stockActor(i)
 if a.flag~=1 or a.id~=37 or a.x~=1008 then return end
 local s=stockState();assert(s.world==0 and s.level==0 and s.engine==8,'Ordinary lift admission')
 assert(not stock.lift.birth and a.y==192 and a.high==1,'Single genuine initial lift')
 local left=read(LIFT.ram.ScreenLeft_X_Pos)+256*read(LIFT.ram.ScreenLeft_PageLoc)
 local right=left+255;assert(a.x>right and a.x-right<=32,'Real native constructor while still offscreen')
 local slots={};for j=0,5 do slots[#slots+1]=stockActor(j)end
 stock.lift.birth={state=s,actor=a,camera_left=left,camera_right=right,six_slots=slots}
end)
stockHook(STOCK.head,function(cpu)
 if cpu['cpu.a']~=96 or not stock.active then return end
 stock.lift.head={state=stockState(),tile=96,pointer=read(LIFT.ram.R6)+256*read(LIFT.ram.R7),row=read(LIFT.ram.R2),speed=read(LIFT.ram.Player_Y_Speed)}
 assert(stock.lift.head.pointer==0x300 and stock.lift.head.row==0x60,'Exact native hidden transaction')
 assert(stock.lift.head.speed>=128 and stock.lift.admission,'Actual rising fresh-A head from lift')
end)
local function liftControls(s,age)
 local l=stock.lift;local a=liftActor()
 if stock.phase=='lift-wait-cap'then
  pad=0;assert(a and l.birth,'Actual authored lift before departure')
  if a.y>=176 and a.y<=192 and idle(s)and s.action==0 then
   l.departure=s;stockPhase('lift-cap-A',128)
  end
  assert(age<400,'Bounded native lift departure window');return true
 elseif stock.phase=='lift-cap-A'then
  pad=128
  if s.action==3 then l.cap_admission=s;stockPhase('lift-flight',1)end
  assert(age<120,'Original standing cap A admission');return true
 elseif stock.phase=='lift-flight'then
  pad=s.x<1015 and 1 or s.x>1019 and 2 or 0
  if l.current then l.boarded=s;stockPhase('lift-settle',0)
  elseif age>160 and floor(s)and idle(s)then final=s;finish(false,'Cap departure landed on ground without native lift contact')end
  assert(age<360,'Bounded authentic cap-to-lift flight');return true
 elseif stock.phase=='lift-settle'then
  assert(a,'The real lift remains while settling')
  pad=s.x<1014 and 1 or s.x>1019 and 2 or 0
  local released=read(LIFT.ram.A_B_Buttons)&128==0 and read(LIFT.ram.PreviousA_B_Buttons)&128==0
  local rising=l.previous_top and a.y<l.previous_top
  if l.current and l.moving_contacts>=2 and idle(s)and s.action==0 and released
    and s.x>=1014 and s.x<=1019 and a.y>=164 and a.y<=176 and rising then
   l.attempts=l.attempts+1;assert(l.attempts<=3,'Bounded natural lift jump attempts')
   l.request={state=s,actor=a};stockPhase('lift-jump',128)
  end
  l.previous_top=a.y;assert(age<460,'Bounded original landing/ride/launch');return true
 elseif stock.phase=='lift-jump'then
  pad=l.admission and 0 or 128
  if s.action==3 and not l.admission then l.admission={state=s,actor=a}end
  if age>100 and l.current and idle(s)and s.action==0 then l.admission=nil;stockPhase('lift-settle',0)end
  stock.minimum_y=math.min(stock.minimum_y or s.y,s.y)
  assert(age<240,'Bounded standing jump from native lift');return true
 end
 return false
end
'''


def _control_successor():
    once=P.G.First.once
    text=once(LIFT_V1,"stock.lift={placement=", "stock.lift={strategy='descending120-145',approach={},placement=")
    text=once(text,"local l=stock.lift;l.seen=l.seen or{state=s,actor=a}","""local l=stock.lift;l.seen=l.seen or{state=s,actor=a}
 a.delta=l.previous_actor_y and a.y-l.previous_actor_y or 0;l.previous_actor_y=a.y
 a.native_y_speed=read(LIFT.ram.Enemy_Y_Speed+a.slot);a.native_direction=read(LIFT.ram.Enemy_MovingDir+a.slot)
 if(stock.phase=='lift-flight'or stock.phase=='lift-settle'or stock.phase=='lift-jump')
   and stock.prince_returns%8==0 and l.sample_return~=stock.prince_returns and #l.approach<48 then
  l.sample_return=stock.prince_returns
  l.approach[#l.approach+1]={phase=stock.phase,state=s,actor=a,native_y_speed=read(LIFT.ram.Player_Y_Speed)}
 end""")
    text=once(text,"if a.y>=176 and a.y<=192 and idle(s)and s.action==0 then",
                   "if a.y>=120 and a.y<=145 and a.delta>0 and idle(s)and s.action==0 then")
    return text


LIFT_V2=_control_successor()
LIFT=P.G.First.once(LIFT_V2,'local l=stock.lift;local a=liftActor()',
    '''local l=stock.lift;local a=liftActor()
 if a and l.actor and a.slot==l.actor.slot and a.y==l.actor.y then a.delta=l.actor.delta end''')


def memory_bytes(decoded,pc,size):
    core,meta,state,_=decoded
    # The finalizer copies the staged C65F..C6F9 policy to live C766..C800.
    # See audit_prince_upgrade_reload_1115 and the independently cold-read C7B3.
    if 0xc766<=pc and pc+size<=0xc800:
        at=0xc65f+(pc-0xc766)-0xc100
        return state[at:at+size]
    for start,blob in ((0xa000,core),(0xc800,meta),(0xc100,state)):
        if start<=pc and pc+size<=start+len(blob):return blob[pc-start:pc-start+size]
    raise AssertionError(('Private hook outside decoded regions',hex(pc),size))


def controller(image,overlay,*,policy='descending'):
    assert policy in('descending','v1','v2')
    controls={'descending':LIFT,'v1':LIFT_V1,'v2':LIFT_V2}[policy]
    parent,decoded,binding=authenticate(image,overlay)
    text=baseline_controller(parent);once=P.G.First.once
    text=text.replace(PIN,H(image))
    text=once(text,"local cookie = '"+P.COOKIE+"'","local cookie = '"+overlay['cookie']+"'")
    # Rebuild the exact first-draw readback, changing only explicitly declared
    # source intervals and adding the complete fourth decoded stream.
    line=next(s for s in text.splitlines()if s.startswith('local candidateStaticExtents='))
    table=P.table(text,'local candidateStaticExtents=');rows=[];old_count=0
    for i in range(1,len(table)+1):
        r=table[i];bank,offset=r['bank'],r['offset'];old=bytes(r['bytes'][j]for j in range(1,len(r['bytes'])+1))
        old_count+=len(old);new=bytearray(old)
        if bank==3:
            for at,size in CHANGES:
                for address in range(max(at,offset),min(at+size,offset+len(new))):new[address-offset]=decoded[0][address]
        rows.append(dict(bank=bank,offset=offset,bytes=list(new)))
    assert old_count==4193
    rows.extend(dict(bank=3,offset=at,bytes=list(decoded[0][at:at+size]))for at,size in CHANGES)
    rows.append(dict(bank=1,offset=0,bytes=list(decoded[3])))
    text=once(text,line,'local candidateStaticExtents='+P.Base.lua(rows))
    cfg=P.table(text,'local STOCK=')
    def table_dict(v):
        if hasattr(v,'items'):
            items=list(v.items())
            if items and set(k for k,_ in items)==set(range(1,len(items)+1)):return[table_dict(v[i])for i in range(1,len(items)+1)]
            return{k:table_dict(x)for k,x in items}
        return v
    cfg=table_dict(cfg)
    pickup=cfg['pickup']['pc'];assert pickup==0xc7b3
    data=memory_bytes(decoded,pickup,12)
    assert data.hex()=='adcfc6f031b5344ad032b51f','Actual unchanged owning pickup entry from current cold proof'
    cfg['pickup'].update(pc=pickup,address=2*8192+(pickup&8191),bytes=list(data),private=True)
    for name,h in cfg.items():
        if not isinstance(h,dict)or'pc'not in h:continue
        if h.get('private'):
            data=memory_bytes(decoded,h['pc'],len(h['bytes']));assert data==bytes(h['bytes']),(name,hex(h['pc']))
        else:assert image[16+h['address']:16+h['address']+len(h['bytes'])]==bytes(h['bytes']),name
    old=next(s for s in text.splitlines()if s.startswith('local STOCK='))
    text=once(text,old,'local STOCK='+P.Base.lua(cfg))
    bundle=dict(W.Symbols.bundle(),raw=image)
    pc,at=W.address(bundle,'CheckpointEnemyID'),W.location(bundle,'CheckpointEnemyID')
    fields='PlatformCollisionFlag Enemy_BoundBoxCtrl ScreenLeft_X_Pos ScreenLeft_PageLoc R2 R6 R7 Player_Y_Speed A_B_Buttons PreviousA_B_Buttons'.split()
    if policy!='v1':fields+=['Enemy_Y_Speed','Enemy_MovingDir']
    config=dict(constructor=dict(pc=pc,address=at-16,bytes=list(image[at:at+8]),private=False),ram={name:W.address(bundle,name)for name in fields})
    text=once(text,'local function naturalStockTick()\n','local LIFT='+P.Base.lua(config)+'\n'+controls+'\nlocal function naturalStockTick()\n')
    text=once(text,'local function naturalStockTick()\n local s=stockState()','local function naturalStockTick()\n local s=stockState();liftObserve(s)')
    text=once(text,"stockPhase('cap-fresh-A',128)","stockPhase('lift-wait-cap',0)")
    text=once(text," if stock.phase=='cap-mount'then"," if liftControls(s,age)then return true end\n if stock.phase=='cap-mount'then")
    text=once(text,"if stock.phase~='standing-flight'or", "if stock.phase~='lift-jump'or")
    text=once(text,"if passed then assert(newPacketVerified,'Actual tier2 packet consumer readback required');assert(stock and stock.finished,'Qualified natural item endpoint')end", "if passed then assert(newPacketVerified,'Entire current packet including raw1 verified');assert(stock and stock.finished and stock.lift.birth and stock.lift.contacts>0 and stock.lift.moving_contacts>=2 and stock.lift.admission and stock.lift.head,'Actual native lift carry, fresh A, rising head and completed item endpoint')end")
    text=once(text,'added_helpers=false,','added_helpers=true,')
    # All existing Main-return, original-worker return, positive collector-box,
    # erase, popup11, delayed timer43 INC/cue64 and25-update checks remain.
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    P.Base.LuaRuntime().compile(text)
    return text


def cold(image,overlay):
    authenticate(image,overlay)
    fn=P.clone(P.cold,dict(authenticate=lambda raw:authenticate(raw,overlay),COOKIE=overlay['cookie']))
    return fn(image)


def source(image,overlay,limit=3600,*,policy='descending'):
    text=controller(image,overlay,policy=policy)
    with patch.object(Engine.J,'cold',lambda raw:cold(raw,overlay)),patch.object(Engine.J,'PIN',H(image)):
        return Engine.run(image,limit,text=text)


def source_trace(image,overlay,limit=3600):
    """Read actual native platform gates around a reached descending crossing.

    The Lua and ordinary inputs remain V3 byte-identical. This watches the CPU
    executing those instructions; it does not alter any bus value or caller.
    """
    authenticate(image,overlay)
    bundle=dict(W.Symbols.bundle(),raw=image)
    names=('LargePlatformCollision','CheckPlayerVertical','PlayerCollisionCore',
           'RyuPlatformCollisionBridge','ProcLPlatCollisions','ChkForTopCollision',
           'PlatformSideCollisions','SetCollisionFlag','PositionPlayerOnVPlat',
           'RyuSourceBodyPlatformPrepare','RyuSourceBodyPlatformFinish')
    sites={};missing=[]
    for name in names:
        try:pc,at=W.address(bundle,name),W.location(bundle,name)
        except KeyError:missing.append(name);continue
        assert pc>=0x8000
        sites[pc]=(name,128+(at-16)//8192)
    assert {'LargePlatformCollision','ProcLPlatCollisions','PositionPlayerOnVPlat'}<=set(n for n,_ in sites.values())
    fields='Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_Y_Speed Player_State Player_BoundBoxCtrl Enemy_Flag Enemy_ID Enemy_State Enemy_X_Position Enemy_PageLoc Enemy_Y_Position PlatformCollisionFlag ObjectOffset TimerControl GameEngineSubroutine R0 BoundingBox_UL_XPos'.split()
    at={name:W.address(bundle,name)for name in fields}
    game=W.address(bundle,'GameLoop');game_tag=128+(W.location(bundle,'GameLoop')-16)//8192
    rows=[];pending=[];clock=[0]
    base=N.NesMPU

    def tag(model,pc):return model.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None

    def snapshot(cpu,name,event,slot):
        model=cpu.memory
        r=lambda name,index=0:model[at[name]+index]
        px=r('Player_X_Position')+256*r('Player_PageLoc')
        source=model.ram[2]
        boxes=at['BoundingBox_UL_XPos'];enemy=boxes+4*(slot+1)
        return dict(name=name,event=event,Main=clock[0],PC=cpu.pc,SP=cpu.sp,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,
            opcode=model[cpu.pc],maps=list(model.rawtags),slot=slot,
            player=dict(x=px,y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),speed=r('Player_Y_Speed'),
                ground=r('Player_State'),box_control=r('Player_BoundBoxCtrl'),box=[model[boxes+i]for i in range(4)],
                source_foot=source[0x84]+256*source[0x85],source_action=source[0x616],source_pose=source[0x617],
                source_y=source[0x611],source_phase=source[0xa6]),
            actor=dict(flag=r('Enemy_Flag',slot),id=r('Enemy_ID',slot),state=r('Enemy_State',slot),
                x=r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot),
                carry=r('PlatformCollisionFlag',slot),box=[model[enemy+i]for i in range(4)]),
            R=[model[at['R0']+i]for i in range(8)],timer=r('TimerControl'))

    class Spy(base):
        def step(self):
            model=self.memory;pc=self.pc
            if pc==game and tag(model,pc)==game_tag and model[at['GameEngineSubroutine']]==8:clock[0]+=1
            if pending:
                for item in tuple(pending):
                    name,ret,sp,mapping,slot=item
                    if pc==ret and self.sp==sp and tag(model,pc)==mapping:
                        pending.remove(item)
                        if len(rows)<144:rows.append(snapshot(self,name,'return',slot))
            site=sites.get(pc)
            if site and len(rows)<144 and tag(model,pc)==site[1]and model[at['GameEngineSubroutine']]==8:
                slot=model[at['ObjectOffset']]
                if slot<6 and model[at['Enemy_Flag']+slot]==1 and model[at['Enemy_ID']+slot]==37:
                    ax=model[at['Enemy_X_Position']+slot]+256*model[at['Enemy_PageLoc']+slot]
                    px=model[at['Player_X_Position']]+256*model[at['Player_PageLoc']]
                    foot=model.ram[2][0x84]+256*model.ram[2][0x85];top=model[at['Enemy_Y_Position']+slot]
                    if ax==1008 and 1004<=px<=1036 and abs(foot-top)<=6:
                        name=site[0];rows.append(snapshot(self,name,'entry',slot))
                        if name not in('ChkForTopCollision','PlatformSideCollisions','SetCollisionFlag'):
                            ret=(model[0x100+((self.sp+1)&255)]+256*model[0x100+((self.sp+2)&255)]+1)&65535
                            pending.append((name,ret,(self.sp+2)&255,tag(model,ret),slot))
            return super().step()

    with patch.object(N,'NesMPU',Spy):result=source(image,overlay,limit)
    return dict(execution=result,trace=rows,sites={name:hex(pc)for pc,(name,_)in sites.items()},
                missing=missing,unreturned_watches=len(pending),Lua_unchanged=True,outputs=0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compile-only',action='store_true');args=parser.parse_args()
    raw=P.G.ROM.read_bytes()
    def deny(*a,**k):raise AssertionError('Controller-only source probe attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        text=baseline_controller(raw)
        print('PRINCE_LIFT_BASELINE '+json.dumps(dict(passed=True,parent_SHA256=H(raw),controller_SHA256=H(text.encode()),
            lift_policy_SHA256=H(LIFT.encode()),baseline_only=True,candidate_overlay_pending=True,outputs=0),separators=(',',':')),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
