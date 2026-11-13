"""Ordinary controls from natural sword collection into native enemy combat.

No actor, health, weapon or position fixtures. CPU/Main/NMI only; no physical
cadence or raster claim. Root owns any later Mesen qualification.
"""
from hashlib import sha256
import argparse
import json
from unittest.mock import patch

import check_prince_natural_sword_1113 as P
import prince_original_cpu_1101_v1 as Original


def controller(raw):
    """Pure readonly native Lua: frozen earned prefix, then the same controls."""
    from prince_draw_cache_1113 import current_binding,Packet,EDITS,CANDIDATE
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    assert sha256(raw).hexdigest()==CANDIDATE
    with current_binding(raw):
        text=P.recovery_controller(raw)
    _,chunks,_=Packet.extract(raw)
    store,=[0xa000+i for i in range(len(chunks[0])-2) if chunks[0][i:i+3]==bytes.fromhex('9dcfc6')]
    addresses={name:P.W.address(P.W.Symbols.bundle(),name) for name in
               ('StarInvincibleTimer','FloateyNum_Control')}
    labels=json.loads((P.Base.W.R/'build/prince-actor-1101-v1/native-labels-v153.json').read_text())
    checks='\n'.join(f"  assert(source({pc-0xa000+i},3)=={value},'Cache runtime {pc+i:04X}')"
                     for pc,_old,new in EDITS for i,value in enumerate(new))
    extension=r'''
local combat,combatLast,combatPhase,combatJump,combatParried=nil,-1,'settle',false,false
local function combatState()
  local s=state()
  s.sword=source(0x6ee);s.star=read(@STAR@)
  s.source_x=source(0x60f)+256*source(0x610)
  s.cached_x=source(0x4db)+256*source(0x4dc)
  s.guard_uid=source(0x61c);s.guard_hp=source(0x6d0);s.guard_dead=source(0x6de)
  return s
end
local function combatEvent(name)
  local cpu=emu.getState()
  local e={name=name,commit=commits,state=combatState(),x=cpu['cpu.x'],y=cpu['cpu.y'],pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
  e.stack={};for i=1,12 do e.stack[i]=read(0x100+((e.sp+i)&255)) end
  combat.events[#combat.events+1]=e
  assert(#combat.events<40,'Bounded causal combat trace')
  return e
end
observe(@STORE@,3,function()
  if not combat then return end
  local cpu=emu.getState()
  if cpu['cpu.x']==1 and cpu['cpu.a']==0 and source(0x6d0)==1 then
    local e=combatEvent('original-8725-guard-loss')
    assert(e.state.action==58 and e.state.star==0,'Original attack guard damage')
    combat.loss=e
  end
end)
observe(@PROXY@,2,function()
  if not combat or source(0x6d0)~=0 or source(0x6de)~=85 then return end
  combat.proxy=combatEvent('source-proxy-export')
end)
observe(@CALL@,2,function()
  if not combat or source(0x6d0)~=0 or emu.getState()['cpu.y']~=1 then return end
  combat.call=combatEvent('source-native-kind1')
end)
emu.addMemoryCallback(guarded(function()
  if not combat then return end
  local mapped=emu.convertAddress(0x9af8)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=126*8192+0x1af8 then return end
  local e=combatEvent('native-9AF8')
  local slot=e.x
  assert(combat.loss and combat.proxy and combat.call,'Original guard/export/call causal chain')
  assert(combat.proxy.commit==commits and combat.call.commit==commits,'Same Main deferred delivery')
  assert(e.state.action==58 and e.state.guard_hp==0 and e.state.guard_dead==85 and e.state.star==0,'Source-earned guard death')
  assert(e.state.guard_uid==(128|slot) and combat.loss.state.guard_uid==e.state.guard_uid,'Retained native guard UID')
  assert(read(0x10+slot)==1 and read(0x17+slot)<7 and read(0x1f+slot)&32==0,'Live native sword target')
  combat.kill=e
end),emu.callbackType.exec,0x9af8)
local function combatTick()
  if combatLast==commits then return end
  combatLast=commits
  local s=combatState()
  assert(s.lives==2 and s.hp==combat.initial.hp and s.star==0,'Earned sword combat health/lives, no Star')
  assert(hexHeader(2)==cookie and hexHeader(3)==cookie,'Private cache runtime authentication')
  assert(commits-combat.start<700,'Bounded earned sword combat')
  combat.actions[tostring(s.action)]=true
  if combat.kill then
    local slot=combat.kill.x
    if not combat.post then
      combat.post={state=s,flag=read(0x10+slot),enemy_state=read(0x1f+slot),score=read(@FLOAT@+slot)}
      assert(combat.post.flag==0 or combat.post.enemy_state&32~=0,'Actual native defeat state after Main')
      assert(combat.post.score==1,'Native Goomba defeat score')
    end
    pad=0
    if commits>=combat.kill.commit+12 then
      assert(combatParried and combat.actions['62'] and combat.actions['58'],'Parry then attack')
      combat.parried=true;combat.terminal=s;late.swordCombat=combat
      final=s;finish(true,'Naturally earned sword parry/attack and native Goomba defeat')
    end
    return
  end
  local target
  for slot=0,5 do
    local flag,id,enemyState=read(0x10+slot),read(0x17+slot),read(0x1f+slot)
    local x,y=read(0x76+slot)+256*read(0x5d+slot),read(0xbe+slot)
    if flag>0 and flag<128 and id<21 and enemyState&32==0 and math.abs(y-s.y)<48
      and (not target or math.abs(x-s.x)<math.abs(target.x-s.x))then target={slot=slot,x=x,y=y}end
  end
  pad=0
  if s.sword==2 then
    combatPhase='combat'
    if s.pose==171 and not combatParried then pad=64
    elseif s.action==62 then combatParried=true
    elseif combatParried and target then
      local direction=target.x>=s.x and 1 or 2
      local gap=math.abs(target.x-s.x)
      pad=gap>=(direction==1 and 38 or 32) and direction or 128
    end
  elseif s.action~=91 and s.mode==0 then combatPhase='approach';pad=1
  elseif combatPhase=='approach'then pad=1 end
  if combatPhase=='approach' and s.x>=1352 and s.x<1376 and not combatJump then pad=129;combatJump=true end
  if combatJump and s.x<1440 and combatPhase=='approach'then pad=s.action~=4 and 129 or 1 end
end
local function startSwordCombat()
@CHECKS@
  combat={start=commits,initial=combatState(),events={},actions={}}
  assert(combat.initial.sword==1,'Actual authored flower inventory before combat')
  progress='earned-sword-combat';pad=0
  combatTick()
end
'''
    replacements={'@STAR@':addresses['StarInvincibleTimer'],'@FLOAT@':addresses['FloateyNum_Control'],
                  '@STORE@':store,'@PROXY@':labels['PpNativeProxyOut'],'@CALL@':labels['PpNativeCall'],'@CHECKS@':checks}
    for before,after in replacements.items():extension=extension.replace(before,str(after))
    marker='local function tick()\n'
    assert text.count(marker)==1
    text=text.replace(marker,extension+"\nlocal function tick()\n  if combat then combatTick();return end\n")
    before="finish(true,'Naturally earned mushroom and flower sword');return"
    assert text.count(before)==1
    text=text.replace(before,'startSwordCombat();return')
    marker="assert(#rom==64 and not rom:find('[^0-9a-f]'),'Exact ROM SHA required')"
    assert text.count(marker)==1
    text=text.replace(marker,marker+f"\nassert(rom=='{sha256(raw).hexdigest()}','Exact cache candidate ROM')")
    assert 'emu.write' not in text and 'emu.setState' not in text
    LuaRuntime().compile(text)
    return text


def state(m):
    N=P.N
    s=m.ram[2]
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),action=m.ram[2][0x616],pose=m.ram[2][0x617],
        mode=m.ram[2][0x618],facing=m.ram[2][0x615],sword=m.ram[2][0x6ee],
        health=m.ram[2][0x6cf],lives=N.get(m,'NumberofLives'),
        star=N.get(m,'StarInvincibleTimer'),guard=m.ram[2][0x6e0],
        guard_uid=m.ram[2][0x61c],guard_hp=m.ram[2][0x6d0],
        camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
        source_x=int.from_bytes(s[0x60f:0x611],'little'),source_y=int.from_bytes(s[0x611:0x613],'little'),
        guard_x=int.from_bytes(s[0x61d:0x61f],'little'),guard_y=int.from_bytes(s[0x61f:0x621],'little'),
        guard_facing=s[0x623],guard_action=s[0x624],guard_pose=s[0x625],guard_mode=s[0x626],
        guard_dead_code=s[0x6de],
        source_origin=int.from_bytes(s[0x89:0x8b],'little'),source_index=s[0x4b1],source_phase=s[0xa6],
        cached_x=int.from_bytes(s[0x4db:0x4dd],'little'))


def enemies(m):
    N=P.N
    return [dict(slot=i,id=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i),
        x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
        y=N.get(m,'Enemy_Y_Position',i)) for i in range(6)
        if 0<N.get(m,'Enemy_Flag',i)<128 and N.get(m,'Enemy_ID',i)<21
        and not N.get(m,'Enemy_State',i)&0x20]


def native_snapshot(m):
    N=P.N
    return [dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),
        state=N.get(m,'Enemy_State',i),box=N.get(m,'Enemy_BoundBoxCtrl',i),
        x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
        y=N.get(m,'Enemy_Y_Position',i),y_high=N.get(m,'Enemy_Y_HighPos',i),
        direction=N.get(m,'Enemy_MovingDir',i),x_speed=N.get(m,'Enemy_X_Speed',i),
        y_speed=N.get(m,'Enemy_Y_Speed',i)) for i in range(6)
        if N.get(m,'Enemy_Flag',i) or m.ram[2][0x61c]==128|i]


def donor_cache(snapshot, advance=None):
    rows=[]
    for renderer_prefix in (False,True):
        cpu=Original.machine()
        cpu.memory.switch(4)
        list.__setitem__(cpu.memory,slice(0,2048),snapshot['ram'])
        before=int.from_bytes(bytes(cpu.memory[0x60f:0x611]),'little')
        initial_cache=int.from_bytes(bytes(cpu.memory[0x4db:0x4dd]),'little')
        a,x,y,p=snapshot['registers'][:4]
        if renderer_prefix:
            Original.call(cpu,0xaf57,a=a,x=x,y=y,p=p)
        saved=int.from_bytes(bytes(cpu.memory[0x4db:0x4dd]),'little')
        Original.call(cpu,0xdafa,a=a,x=x,y=y,p=p)
        after=int.from_bytes(bytes(cpu.memory[0x60f:0x611]),'little')
        assert after==(before if renderer_prefix else initial_cache)
        rows.append(dict(original_AF57_prefix=renderer_prefix,before=before,initial_cache=initial_cache,
                         cached=saved,restored=after))
    scheduled=None
    if advance:
        cpu=Original.machine();cpu.memory.switch(4)
        list.__setitem__(cpu.memory,slice(0,2048),advance['ram'])
        Original.call(cpu,0xaf57,**dict(zip(('a','x','y','p'),advance['registers'])))
        cache=bytes(cpu.memory[0x4db:0x4dd])
        list.__setitem__(cpu.memory,slice(0,2048),snapshot['ram'])
        list.__setitem__(cpu.memory,slice(0x4db,0x4dd),cache)
        Original.call(cpu,0xdafa,**dict(zip(('a','x','y','p'),snapshot['registers'][:4])))
        scheduled=dict(pre_animation=advance['state'],restored=int.from_bytes(bytes(cpu.memory[0x60f:0x611]),'little'))
        assert scheduled['restored']==advance['state']['source_x']
    return dict(donor_SHA256=Original.SHA,actual_host_entry=snapshot['state'],
                original_F141_calls_AF57_before_F158=True,cases=rows,
                scheduled_pre_animation_save=scheduled,
                scope='Actual donor4:AF57 and7:DAFA execute on the captured host source RAM. Only reference-machine RAM is initialized; the host route receives ordinary inputs only.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit',type=int,default=1800)
    parser.add_argument('--trace',action='store_true')
    parser.add_argument('--candidate',action='store_true')
    parser.add_argument('--lua',action='store_true',help='Execute the pure readonly native Lua against CPU Main/NMI')
    args=parser.parse_args()
    raw=P.Base.C.ROM.read_bytes()
    from prince_draw_cache_1113 import proposal,current_binding
    if args.candidate:
        raw,layout=proposal(raw)
        print(json.dumps(dict(private_candidate=layout)),flush=True)
    lua=controller(raw) if args.lua else None
    with current_binding(raw):
        if lua:
            model,opening=P.cold(raw)
            with patch.object(P,'recovery_controller',lambda image:lua):
                result=P.route(model,raw,4300,recover=True)
            print(json.dumps(dict(Lua_SHA256=sha256(lua.encode()).hexdigest(),opening=opening,
                result=result,terminal=state(model),enemies=native_snapshot(model),output_files=0)),flush=True)
            assert result['passed'],result
        else:
            run(raw,args)


def run(raw,args):
    m,opening=P.cold(raw)
    prefix=P.route(m,raw,4000,recover=True)
    assert prefix['passed'] and state(m)['sword']==1
    initial=state(m)
    print(json.dumps(dict(prefix=prefix['reason'],ROM_SHA256=sha256(raw).hexdigest(),
        opening=opening,updates=prefix['logical_updates'],initial=initial,enemies=enemies(m))),flush=True)
    points={((P.W.location(m.bundle,name)-16)//8192|128,P.W.address(m.bundle,name)):name
            for name in ('ShellOrBlockDefeat','HuInjury')}
    points[(254,0x9af8)]='NativeDefeatInterior'
    labels=json.loads((P.Base.W.R/'build/prince-actor-1101-v1/native-labels-v153.json').read_text())
    _,chunks,_=P.Replay.Packet.extract(raw)
    # Actual recovered donor5:8725 STA06CF,X; guard admission supplies X1.
    guard_store_pc,=[0xa000+i for i in range(len(chunks[0])-2)
                     if chunks[0][i:i+3]==bytes.fromhex('9dcfc6')]
    for name in ('PpNativeProxyOut','PpNativeCall','PpNativeDeferredKill'):
        points[(2,labels[name])]=name
    source_points={pc:name for name,pc in labels.items() if name in (
        'PpBattle_5_8972','PpBattle_5_8985','PpBattle_5_8999','PpBattle_5_89A1','PpNativeProxyIn')}
    events=[];transitions=[];actions=set();previous=None;parried=False
    draw_trace=[];coordinate_writes=[];last_source=None;retained={};guard_death=None
    phase='settle';jump=False;defeated=False;defeat_tick=None;defeat_post=None
    for tick in range(args.limit):
        s=state(m);active=enemies(m)
        close=[e for e in active if abs(e['y']-s['y'])<48]
        target=min(close,key=lambda e:abs(e['x']-s['x'])) if close else None
        pad=0
        if s['sword']==2:
            phase='combat'
            if s['pose']==171 and not parried:pad=64
            elif s['action']==62:parried=True
            elif parried and target:
                direction=1 if target['x']>=s['x'] else 2
                gap=abs(target['x']-s['x'])
                pad=direction if gap>=(38 if direction==1 else 32) else 128
        elif s['action']!=91 and s['mode']==0:
            phase='approach';pad=1
        elif phase=='approach':pad=1
        if phase=='approach' and 1352<=s['x']<1376 and not jump:
            pad=129;jump=True
        if jump and s['x']<1440 and phase=='approach':pad=129 if s['action']!=4 else 1
        if defeated:pad=0
        m.controller_pad=pad
        def observe(model,cpu):
            nonlocal last_source,guard_death
            source_x=int.from_bytes(model.ram[2][0x60f:0x611],'little')
            if 438<=tick<=444 and last_source and source_x!=last_source['source_x'] and abs(source_x-last_source['source_x'])>32:
                coordinate_writes.append(dict(tick=tick,writer=last_source,state=state(model),enemies=native_snapshot(model)))
            if last_source and last_source['guard_hp']==1 and model.ram[2][0x6d0]==0 and guard_death is None:
                guard_death=dict(tick=tick,writer=last_source,state=state(model),enemies=native_snapshot(model))
            last_source=dict(pc=cpu.pc,bank=model.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc>=0x8000 else -1,
                             source_x=source_x,guard_hp=model.ram[2][0x6d0],A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p)
            if cpu.pc<0x8000:return
            tag=model.rawtags[(cpu.pc-0x8000)//8192]
            if tag==3 and cpu.pc==0xb396 and 'before_dafa' not in retained:
                retained['before_advance']=dict(ram=bytes(model.ram[2][:2048]),state=state(model),
                                                registers=[cpu.a,cpu.x,cpu.y,cpu.p])
            if tag==3 and cpu.pc==0xab1d and 438<=tick<=444 and 'before_dafa' not in retained:
                retained['before_dafa']=dict(ram=bytes(model.ram[2][:2048]),state=state(model),
                                             registers=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp])
            name=points.get((tag,cpu.pc))
            if name and name.startswith('PpNative') and (model.ram[2][0x6d0]!=0 or
                    (name=='PpNativeCall' and cpu.y!=1)):
                name=None
            if name and len(events)<80:
                events.append(dict(tick=tick,name=name,X=cpu.x,offset=P.N.get(model,'ObjectOffset'),
                    pc=cpu.pc,bank=tag,SP=cpu.sp,Y=cpu.y,
                    stack=[model[0x100+((cpu.sp+i)&255)] for i in range(1,13)],
                    state=state(model),enemies=enemies(model)))
            if tag==2 and 438<=tick<=444 and cpu.pc in source_points and len(draw_trace)<35:
                draw_trace.append(dict(tick=tick,pc=cpu.pc,bank=tag,name=source_points[cpu.pc],
                                       registers=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp],
                                       state=state(model),enemies=native_snapshot(model)))
        P.Frames.frame(m,observe)
        after=state(m);actions.add(after['action'])
        key=(phase,after['action'],after['pose'],after['sword'],after['health'])
        if key!=previous:
            if len(transitions)<80:transitions.append(dict(tick=tick,pad=pad,phase=phase,**after))
            previous=key
        assert after['lives']==2 and after['health']>0,dict(tick=tick,state=after,events=events[-4:])
        # The source intentionally sheaths inventory2->1 as its guard dies,
        # before the host's deferred native defeat. Bind the source death and
        # actual native slot instead of requiring drawn mode at the suffix.
        defeats=[e for e in events if e['name'] in ('ShellOrBlockDefeat','NativeDefeatInterior')
                 and e['state']['star']==0 and e['state']['action']==58
                 and e['state']['guard_hp']==0 and e['state']['guard_dead_code']==85
                 and e['state']['guard_uid']==(128|e['X'])
                 and any(enemy['slot']==e['X'] and enemy['id']<7 for enemy in e['enemies'])]
        defeated=bool(defeats)
        if defeated and defeat_tick is None:
            defeat_tick=tick
            slot=defeats[0]['X']
            defeat_post=dict(tick=tick,slot=slot,flag=P.N.get(m,'Enemy_Flag',slot),
                id=P.N.get(m,'Enemy_ID',slot),state=P.N.get(m,'Enemy_State',slot),
                score=P.N.get(m,'FloateyNum_Control',slot),player=after)
            assert defeat_post['flag']==0 or defeat_post['state']&0x20,defeat_post
            assert guard_death and guard_death['state']['guard_uid']==(128|slot)
            assert (guard_death['writer']['bank'],guard_death['writer']['pc'],
                    guard_death['writer']['X'],guard_death['writer']['A'])==(3,guard_store_pc,1,0),guard_death
            assert guard_death['state']['action']==58,guard_death
            assert guard_death['tick']<=tick
            chain=[event['name'] for event in events if event['tick']==tick]
            assert chain.index('PpNativeProxyOut')<chain.index('PpNativeCall')<chain.index('NativeDefeatInterior'),chain
        if defeated and tick>=defeat_tick+12:break
    result=dict(passed=defeated and parried,ROM_SHA256=sha256(raw).hexdigest(),
        prefix_updates=prefix['logical_updates'],continuation_updates=tick+1,
        parried=parried,actions=sorted(actions),events=events,transitions=transitions,
        native_defeat_after_Main=defeat_post,
        original_guard_death_store=guard_death,
        coordinate_writes=coordinate_writes,draw_trace=draw_trace,
        donor_cache=donor_cache(retained['before_dafa'],retained.get('before_advance')) if 'before_dafa' in retained else None,
        terminal=state(m),enemies=enemies(m),runtime_state_injections=0,output_files=0,
        physical_Mesen=False)
    if not args.trace:
        for row in coordinate_writes:
            row.pop('enemies',None)
        result['transitions']=[row for row in transitions if 438<=row['tick']<=460]
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(result,sort_keys=True),flush=True)
    if args.candidate:
        assert result['passed'],result


if __name__=='__main__':main()
