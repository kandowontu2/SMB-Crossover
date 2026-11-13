"""Current3684 natural healthy Flower/earned vegetable controller, zero artifacts."""
from hashlib import sha256
import argparse
import json
import re
from unittest.mock import patch
from zipfile import ZipFile

import compose_smb2_foreground_current_1113 as Current
import replay_smb2_natural_powerups_1113 as Parent
import check_smb2_natural_powerups_1113 as Runner

PIN=Current.CANDIDATE
SCOPES=('collect','throw','hit')
OLD_LUA='03ef28a9b4ca8dad5c45b67f8a2e81d7c55172f9c6897803ceec8603f1f3ce34'
FROZEN_CONTROLLER=Parent.controller
COLLECT_SHA={
    0:'61c488a3694abd39844beb9889b03218b19d2db4b458f246bea776afb495a546',
    1:'f018c96830cf38ccabc56cd5fd099ad8bd5fa989c3c14c99ec16943609735982',
    2:'372fb776fb3578acee46e357015f630402244dc6849300113710ba49a5b29c28',
    3:'4b440fb673f2d5c9246b40a6297bac2fa24b28846509a6c67bce1bc4fc5362eb',
    4:'04ba3610345595799f375af4ff533b38700e6643402c282dc19cf917d6a2cc78',
    5:'efc6cc3a1c27cdd89a7ea31cff09b3e68ddd4fc25c1087d1b2ef0953f97355ca',
    6:'d9a3f8495393a478da33fe69bd88813f40f3c2df72810ac4cfa7195810179ef4',
    7:'d415b48aa31265f6ee42e4d851c12a54fe118ebdd1db15dc0c3fc8a8cbf448ea',
}
THROW_SHA={
    0:'a2ff609131b32752ed72892944a158c4d2d9ce21f075fe4a7f596719b3c51376',
    1:'608b309f4d7841b232aae068bacd969c15308ba1792d749b7073ca9015116e31',
    2:'58ac25649bd6333f45edea9139e7b6bf6a88942fbc8fc95119aad1714fbe9f6c',
    3:'26ca992bc434446e4e115107062c909002dec97c0a7b7cbd151a61263dc7e4c6',
    4:'b4e4aa2ef067df6a961a3d7ec34bea51366c4a870edfcae8f8bd4bef0cad9dd0',
    5:'f861c9fb465dc575c841e1ba2c2925a4a1a7d9ee62237ab4f8311c8d9ea06ee0',
    6:'3e0b555eb58728a82cd8a96b998dc5aedb8f2e65c4142f85dc0693b8063b0213',
    7:'c80525a4570a0c57f9d2f9f199bbb55ecf39edb7c024de46bf68b579ec1f10ab',
}

OBSERVERS=r'''
emu.addMemoryCallback(guard(function()
 if not game or not currentHook('S2BeginLift')or natural.phase~='vegetable-pull'then return end
 natural.pull_entry={s=state(),source=sourceState(),item=vegetable(emu.getState()['cpu.x'])}
 assert(r('S2Vegetables')==3 and r('S2Air')==0 and r('S2Fresh')&64~=0,'Actual freshB supported reserve pull')
end),emu.callbackType.exec,F.S2BeginLift)
emu.addMemoryCallback(guard(function()
 if not game or not currentHook('S2ObjectHit')then return end
 local a=vegetable(emu.getState()['cpu.x'])
 if a.kind==50 and a.projectile~=0 then natural.object_hit={item=a,s=state(),source=sourceState()}end
end),emu.callbackType.exec,F.S2ObjectHit)
emu.addMemoryCallback(guard(function()
 if not game or not currentHook('ShellOrBlockDefeat')or not natural.object_hit then return end
 if updates-natural.object_hit.s.updates>1 then return end
 local c=emu.getState();local sp=c['cpu.sp'];local a=actor(c['cpu.x'])
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local q={before=a,s=state(),source=sourceState(),return_sp=(sp+2)&255,return_pc=pc}
 emu.addMemoryCallback(guard(function()
  if natural.hit or emu.getState()['cpu.sp']~=q.return_sp then return end
  q.after=actor(a.slot);q.source_after=sourceState()
  assert(a.id==6 and a.flag==1 and a.state&32==0,'Actual live native Goomba target')
  assert(q.after.flag==0 or q.after.state&32~=0,'Actual native vegetable defeat transition')
  natural.hit=q
 end),emu.callbackType.exec,pc)
end),emu.callbackType.exec,F.ShellOrBlockDefeat)
'''

DRIVE=r'''
local function vegetable(slot)
 return{slot=slot,state=read(F.S2ObjectState+slot),kind=read(F.S2ObjectType+slot),host=read(F.S2ObjectHost0+slot),
  projectile=read(F.S2ObjectProjectile+slot),lift=read(F.S2ObjectLift+slot),
  x=read(F.S2X+1+slot)+256*read(F.S2Page+1+slot),y=read(F.S2Y+1+slot),vx=read(F.S2VX+1+slot),vy=read(F.S2VY+1+slot)}
end
local function drive()
 local s=state();local own=sourceState()
 if CPU_CONTROLLER_OPENING and CPU_FLOWER_MAIN_LIMIT and updates>=CPU_FLOWER_MAIN_LIMIT then finish(false,'Source logical Flower route bound');return end
 assert(r('SelectedCharacter')==25 and r('S2Variant')==identity and s.ready==178,'Actual SMB2/Doki identity and owner')
 assert(s.lives==2 and own.S2Health==31 and own.S2MaxHealth==0 and own.S2Size==0,'Healthy initial source form and both lives')
 assert(updates<2600,'Finite ordinary Flower/vegetable route')
 if not active()then pad=0;return end
 assert(s.world==0 and s.level==0,'Unmodified authored1-1')
 if not natural.opening then natural.opening={s=s,source=own}end
 if updates%60==0 then
  natural.recent=natural.recent or{};natural.recent[#natural.recent+1]={phase=natural.phase,s=s,source=own,pad=pad}
  if #natural.recent>8 then table.remove(natural.recent,1)end
 end
 if natural.phase=='approach'then
  pad=1
  if natural.hold>0 then natural.hold=natural.hold-1;pad=129
  elseif own.S2Air==0 and own.S2Held&128==0 then
   for slot=0,5 do local a=actor(slot)
    if a.flag==1 and a.id<21 and a.state<32 and a.x-s.x>0 and a.x-s.x<48 then natural.hold=23;pad=129;break end
   end
  end
  if s.x>=326 then newPhase('settle')end
 elseif natural.phase=='settle'then
  pad=settle(328)
  if own.S2Air==0 and s.y<160 then newPhase('head-floor-left');pad=2
  elseif own.S2Air==0 and s.x>=328 and s.x<=329 and own.S2VX==0 and own.S2Held&128==0 then newPhase('head');natural.hold=23;pad=128 end
 elseif natural.phase=='head-floor-left'then
  pad=settle(300)
  if own.S2Air==0 and s.y>=160 and math.abs(s.x-300)<=1 and own.S2VX==0 then newPhase('settle');pad=1 end
 elseif natural.phase=='head'then
  pad=0
  if natural.hold>0 then natural.hold=natural.hold-1;pad=128
  elseif own.S2Air==0 and own.S2Held&128==0 then natural.hold=23;pad=128 end
 elseif natural.phase=='flower-left'then
  pad=settle(300)
  if own.S2Air==0 and math.abs(s.x-300)<=1 and own.S2VX==0 and own.S2Held&128==0 then newPhase('flower-charge');pad=4 end
 elseif natural.phase=='flower-charge'then
  assert(own.S2Air==0,'Original Down charge remains supported')
  pad=4
  if r('S2Charge')>=60 and own.S2Held&128==0 then
   natural.launch={s=s,source=own,charge=r('S2Charge')};newPhase('flower-jump');pad=129
  end
 elseif natural.phase=='flower-jump'then
  pad=settle(329)
  if updates-natural.since<90 then pad=pad|128 end
  if updates-natural.since>100 and own.S2Air==0 then newPhase('flower-left');pad=2 end
 elseif natural.phase=='resume'then
  pad=0
  if updates-natural.since>=60 then
   assert(#natural.pickups==1 and own.S2Vegetables==3,'Earned Flower reserve retained through60 updates')
   if flowerScope=='collect'then finish(true,'Natural healthy Flower, reserve+3, native mature collector/effects and60resumed updates');return end
   newPhase('vegetable-pull');pad=0
  end
 elseif natural.phase=='vegetable-pull'then
  pad=0
  if own.S2Air==0 and own.S2Held&64==0 then pad=64 end
  if own.S2Holding~=0 then
   assert(own.S2Vegetables==2,'One successful original reserve allocation spent')
   natural.lift={s=s,source=own,item=vegetable(r('S2HeldIndex'))};newPhase('vegetable-carry');pad=0
  end
 elseif natural.phase=='vegetable-carry'then
  pad=0
  if own.S2Holding~=0 and own.S2State==0 and own.S2Timer==0 and updates-natural.since>=30 then
   natural.carried={s=s,source=own,item=vegetable(r('S2HeldIndex'))}
   assert(natural.carried.item.kind==50 and natural.carried.item.host==255 and natural.carried.item.state~=0,'Original source vegetable held record')
   if flowerScope=='throw'then newPhase('vegetable-throw');pad=64 else newPhase('vegetable-travel')end
  end
 elseif natural.phase=='vegetable-travel'then
  traversalDrive();pad=pad&191
  for slot=0,5 do local a=actor(slot);local gap=a.x-s.x
   if a.flag==1 and a.id==6 and a.state<32 and gap>=24 and gap<=72 and math.abs(a.y-s.y)<=16 and own.S2Air==0 then
    natural.target={item=a,s=s,source=own};newPhase('vegetable-throw');pad=64;break
   end
  end
 elseif natural.phase=='vegetable-throw'then
  pad=0
  if own.S2Holding==0 then
   for slot=0,2 do local a=vegetable(slot)
    if a.state~=0 and a.projectile~=0 then natural.thrown={s=s,source=own,item=a};break end
   end
   if natural.thrown then
    assert(own.S2Vegetables==2,'Throw does not consume another reserve')
    newPhase('vegetable-flight')
   elseif natural.hit then newPhase('vegetable-flight')end
  end
 elseif natural.phase=='vegetable-flight'then
  pad=0
  if flowerScope=='throw'and updates-natural.since>=30 then finish(true,'Natural Flower reserve, original vegetable pull/carry/freshB throw and30normal updates');return end
  if natural.hit and updates-natural.since>=30 then finish(true,'Natural Flower reserve and original vegetable native enemy defeat');return end
  assert(updates-natural.since<180,'Bounded actual vegetable flight/contact')
 else error('Unknown Flower route phase '..natural.phase)end
 if not natural.birth then
  for slot=0,5 do local a=actor(slot)
   if a.flag==1 and a.id==46 then
    assert(a.kind==1 and own.S2Vegetables==0 and #natural.injuries==0,'Documented healthy initial Flower choice')
    natural.birth={item=a,s=s,source=own};newPhase('flower-left');pad=2;break
   end
  end
 end
end
'''


def frozen_base(raw):
    assert sha256(raw).hexdigest()==PIN
    import bub_native_noops_1113 as Bub
    public=Current.inverse(raw);base=Bub.combined_reverse(public)
    assert sha256(base).hexdigest()==Parent.PIN
    return base


def controller(raw,variant=4,scope='collect'):
    assert scope in SCOPES and 0<=variant<8
    base=frozen_base(raw);text=FROZEN_CONTROLLER(base,variant,'healthy-flower-birth')
    old=Parent.SOURCE.read_text();assert sha256(old.encode()).hexdigest()==OLD_LUA
    callbacks=old[:old.index('local function drive()')]
    for before,after in(
        ("a.kind==0 and a.state>=128,'Actual mature natural Mushroom collector'","a.kind==1 and a.state>=128,'Actual mature natural Flower collector'"),
        ("q.before.S2Health==15 and q.before.S2MaxHealth==0,'Naturally injured initial health at collection'","q.before.S2Health==31 and q.before.S2MaxHealth==0 and q.before.S2Vegetables==0,'Natural healthy initial collector'"),
        ("q.after.S2Health==47 and q.after.S2MaxHealth==1 and q.after.S2Vegetables==0,'Original max-heart increment/full heal'","q.after.S2Health==31 and q.after.S2MaxHealth==0 and q.after.S2Vegetables==3,'Original Flower reserve+3 without max-heart grant'")):
        callbacks=Parent.Root.once(callbacks,before,after)
    driver=DRIVE
    if scope=='hit':
        driver=Parent.Root.once(driver,"natural.target={item=a,s=s,source=own};newPhase('vegetable-throw');pad=64;break",
            "natural.target={item=a,s=s,source=own};newPhase('vegetable-aim');pad=2;break")
        driver=Parent.Root.once(driver," elseif natural.phase=='vegetable-throw'then",r'''
 elseif natural.phase=='vegetable-aim'then
  local vx=own.S2VX;if vx>=128 then vx=vx-256 end
  pad=vx>0 and 2 or vx<0 and 1 or 0
  if vx==0 then natural.aim={s=s,source=own};newPhase('vegetable-face');pad=1 end
 elseif natural.phase=='vegetable-face'then
  pad=1
  if own.S2Held&1~=0 and own.S2VX<8 then newPhase('vegetable-throw');pad=64 end
 elseif natural.phase=='vegetable-throw'then''')
    if scope!='collect':driver=Parent.Root.once(driver,'local function drive()',OBSERVERS+'\nlocal function drive()')
    text=Parent.Root.once(text,old,callbacks+driver)
    names=('S2Charge','S2HeldIndex','S2X','S2Y','S2Page','S2ObjectState','S2ObjectType',
        'S2ObjectHost0','S2ObjectProjectile','S2ObjectLift')
    W=Parent.Root.Base.W;b=dict(W.Symbols.bundle(),raw=raw)
    text=Parent.Root.once(text,'local F={','local F={'+','.join(n+'='+str(W.address(b,n))for n in names)+',')
    if scope!='collect':
        hooks=('S2BeginLift','S2ObjectHit','ShellOrBlockDefeat')
        text=Parent.Root.once(text,'local F={','local F={'+','.join(n+'='+str(W.address(b,n))for n in hooks)+',')
        extra=[]
        for name in hooks:
            at=W.location(b,name)
            extra.append(name+'={offset='+str(at-16)+',hex="'+raw[at:at+12].hex()+'"}')
        text=Parent.Root.once(text,'local itemHooks={','local itemHooks={'+','.join(extra)+',')
    assert text.count(Parent.PIN)==1
    for name in('NativeRarePlayerHeadCollisionCore','S2MainPrepare','S2MainPickup'):
        at=W.location(b,name);assert raw[at:at+12]==base[at:at+12]
    text=f'local flowerScope={json.dumps(scope)}\n'+text.replace(Parent.PIN,PIN)
    Parent.Root.Base.LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    if scope=='collect':assert sha256(text.encode()).hexdigest()==COLLECT_SHA[variant]
    if scope=='throw':assert sha256(text.encode()).hexdigest()==THROW_SHA[variant]
    return text


def source_run(raw,variant=4,scope='collect',limit=2600):
    factory=lambda image,v,mode:controller(image,v,scope)
    runtime=Parent.Root.Base.LuaRuntime
    def bounded_runtime(*args,**kwargs):
        lua=runtime(*args,**kwargs);lua.globals().CPU_FLOWER_MAIN_LIMIT=limit-2
        return lua
    with patch.object(Parent,'controller',factory),patch.object(Runner,'PIN',PIN),patch.object(Parent.Root.Base,'LuaRuntime',bounded_runtime):
        return Runner.run_controller(raw,variant,'natural-flower-'+scope,limit)


def semantics(raw):
    """Bind actual original item/reserve/lift/throw code, without state fixtures."""
    from compose_metal_head_bridge_1112 import assemble_segments
    from check_smb2_pipe_priority_1113 import normalized,ARCHIVE
    assert sha256(raw).hexdigest()==PIN
    W=Parent.Root.Base.W;b=dict(W.Symbols.bundle(),raw=raw);rows={}
    prefix='build/doki-current-component-1101-v1/src/'
    with ZipFile(ARCHIVE)as z:
        for filename,names in(('smb2_roster_core.s',('S2GiveItem',)),
            ('smb2_roster_terrain.s',('S2GroundInteraction',)),
            ('smb2_roster_objects.s',('S2BeginLift','S2ObjectHit'))):
            data=z.read(prefix+filename);source=data.decode()
            for name in names:
                body=source.split('.proc '+name+'\n',1)[1].split('.endproc',1)[0]
                tokens=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',body))
                constants={n:W.address(b,n)for n in tokens if n in b['syms']}
                constants['CHARACTER_SMB2_ROSTER']=25
                body=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\+([0-9]+)\b',
                    lambda m:'$%04x'%(constants[m[1]]+int(m[2])),body)
                code=assemble_segments('.segment "ORIGINAL"\n'+normalized(body),{'ORIGINAL':W.address(b,name)},constants)[0]['ORIGINAL']
                at=W.location(b,name);assert raw[at:at+len(code)]==code,(name,'Actual current source mismatch')
                rows[name]=dict(member=filename,member_SHA256=sha256(data).hexdigest(),bytes=len(code),file=at)
        native=z.read(prefix+'smb2_roster_native.inc')
    assert sha256(native).hexdigest()=='c929f894f8d6f4723e6371d140c85fef76de47eb9f53bff0af6b544325f80cb0'
    windows=[]
    for name,hexcode in(
        ('S2N8C57','ad'+W.address(b,'S2Charge').to_bytes(2,'little').hex()+'c93cb0'),
        ('S2N8E05','2c'+W.address(b,'S2Fresh').to_bytes(2,'little').hex()+'50'),
        ('S2N8E4E','ce'+W.address(b,'S2Holding').to_bytes(2,'little').hex()),
        ('S2N8E9D','9d'+W.address(b,'S2ObjectProjectile').to_bytes(2,'little').hex())):
        code=bytes.fromhex(hexcode);at=W.location(b,name);assert raw[at:at+len(code)]==code
        windows.append(dict(name=name,file=at,hex=hexcode))
    return dict(passed=True,ROM_SHA256=PIN,whole_source_routines=rows,original_charge_and_freshB_throw_windows=windows,
        health_initial=31,healthy_native_kind=1,Flower_reserve_increment=3,reserve_cap=9,
        successful_pull_spend=1,vegetable_type=50,vegetable_native_owner=255,vegetable_hitbox=2,
        new_game_bytes=0,state_seeds=0,outputs=0,Mesen_run=False)


def compact(q):
    receipt=q['receipt']or{};natural=receipt.get('natural',{})
    result={k:q[k]for k in('passed','ROM_SHA256','variant','mode','controller_SHA256','seconds',
        'logical_Main_NMI_iterations','terminal','state_or_actor_seeds','outputs','Mesen_run')}
    result.update(reason=receipt.get('reason'),all_returned_Main=receipt.get('all_returned_Main'),
        opening=natural.get('opening'),heads=natural.get('heads'),prepares=natural.get('prepares'),birth=natural.get('birth'),
        original_charge_launch=natural.get('launch'),pickups=natural.get('pickups'),
        pull_entry=natural.get('pull_entry'),lift=natural.get('lift'),carried=natural.get('carried'),
        target=natural.get('target'),aim=natural.get('aim'),thrown=natural.get('thrown'),object_hit=natural.get('object_hit'),hit=natural.get('hit'),
        recent=natural.get('recent')if not q['passed']else None,
        natural_scene_unmodified=q['natural_scene_unmodified'],physical_native_claim=False)
    if q['passed']:
        def position(row):
            return {k:row[k]for k in('x','y','updates')if k in row}
        for key in('opening','original_charge_launch','pull_entry','lift','carried','target','aim','thrown','object_hit','hit'):
            row=result.get(key)
            if row and's'in row:row=dict(row,s=position(row['s']));result[key]=row
            if row:
                for field in('source','source_after'):
                    if field in row:row[field]={k:v for k,v in row[field].items()if k in('S2Health','S2MaxHealth','S2Vegetables','S2Holding','S2State','S2Timer')}
        for key in('heads','prepares','pickups'):
            rows=result.get(key)or{}
            result[key]={i:{k:(position(v)if k=='s'else{k1:v1 for k1,v1 in v.items()if k1 in('S2Health','S2MaxHealth','S2Vegetables','S2Size')}if k in('source','before','after')else v)
                for k,v in row.items()if k not in('return_pc','return_sp')}for i,row in rows.items()}
        if result.get('birth'):result['birth']={'item':result['birth']['item'],'s':position(result['birth']['s'])}
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='4')
    p.add_argument('--scope',choices=SCOPES,default='collect');p.add_argument('--cpu',action='store_true')
    p.add_argument('--semantics',action='store_true')
    p.add_argument('--limit',type=int,default=2600);args=p.parse_args()
    raw=Runner.Flag.ROM.read_bytes();assert sha256(raw).hexdigest()==PIN
    if args.semantics:
        print(json.dumps(semantics(raw),separators=(',',':')),flush=True)
        raise SystemExit(0)
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=compact(source_run(raw,variant,args.scope,args.limit))if args.cpu else dict(ROM_SHA256=PIN,variant=variant,scope=args.scope,
            controller_SHA256=sha256(controller(raw,variant,args.scope).encode()).hexdigest(),outputs=0,Mesen_run=False)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Natural Flower controller must satisfy its actual collector scope'
