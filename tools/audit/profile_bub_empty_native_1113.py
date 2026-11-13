"""Pure read-only current Bub/Bob cadence controller; root owns native runs."""
from hashlib import sha256
from collections import defaultdict
import json
from unittest.mock import patch

import check_bub_current_budget_1113 as B


def controller(raw, identity=0):
    assert identity in (0, 1) and sha256(raw).hexdigest() == B.PIN
    q, _, binding = B.bindings(raw)
    b = B.W.Symbols.bundle(); b['raw'] = raw
    names = ('CrossoverTitleDrawn', 'DisableScreenFlag', 'CrossoverMenuState',
        'CrossoverMenuIndex', 'SelectedCharacter', 'OperMode', 'OperMode_Task',
        'GameEngineSubroutine', 'NumberofLives', 'Player_X_Position', 'Player_PageLoc',
        'Player_Y_Position', 'GameLoop', 'IdleLoop', 'Enemy_Flag', 'Enemy_ID',
        'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position', 'NmiSkipped')
    fields = {n: B.W.address(b, n) for n in names}
    # Current typed cookie selector, authenticated by the complete manager hash.
    origin=16+65*8192
    assert binding['current_manager_531_SHA256']=='9f844dec3d38577485ff4470be755e20e50be26133968ff1514b8748f246d556'
    at=raw[origin+0xbaf+2]+256*raw[origin+0xbb7+2]
    cookie=raw[origin+at-0xa000:origin+at-0xa000+16]
    init=json.loads((B.R/'build/bub-initial-tier-1103-v87/proposal.json').read_text())
    assert cookie.hex()==init['cookie']=='a72701f3691d419fd9ae7473840ce393'
    image=(B.R/'build/bub-initial-tier-1103-v87/private-image.bin').read_bytes()
    hooks=[]
    for name in ('GameLoop', 'IdleLoop'):
        at=B.W.location(b,name)-16
        count=39 if name=='IdleLoop' else 8
        hooks.append(dict(kind='rom',pc=fields[name],offset=at,data=raw[at+16:at+16+count].hex()))
    idle_code=bytes.fromhex(hooks[1]['data'])
    assert idle_code.hex()=='ad3901f0fbad3a014820d98268cd3a01f0ee20c4edb0e9ad3a014820d98268a9008d3b014cb282'
    returns=[fields['IdleLoop']+i+3 for i in range(len(idle_code)-2)
             if idle_code[i:i+3]==b'\x20'+fields['GameLoop'].to_bytes(2,'little')]
    assert returns==[0x82be,0x82d0]
    for name in ('BbNativeUpdate', 'BbSourceClock', 'BbNativeDraw'):
        pc=q['labels'][name]
        hooks.append(dict(kind='work',pc=pc,offset=3*8192+(pc&8191),data=image[pc-0xa000:pc-0xa000+8].hex()))
    text='local F='+json.dumps(fields,separators=(',',':')).replace('"','').replace(':','=')+'\n'
    text+=f'local identity,expectedRom,cookie={identity},"{B.PIN}","{cookie.hex()}"\n'
    text+='local hooks={' + ','.join('{kind="'+h['kind']+'",pc='+str(h['pc'])+',offset='+str(h['offset'])+',data="'+h['data']+'"}' for h in hooks)+'}\n'
    text+=f'local sourcePc={q["labels"]["BbSourceClock"]}\n'
    text+='local returnPcs={'+','.join(map(str,returns))+'}\n'
    text+=r'''
local frame,updates,sourceUpdates,pad,physicalPolls=0,0,0,0,0
local polled,game,done=false,false,false
local phase,pending,start,last,sourceThisMain='menu',nil,nil,nil,0
local phases={};local firstEnemy=nil
local enteredMain,sourceOutside=0,0;local returns={};local entries={}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n)return read(F[n])end
local function work(bank,at)return emu.read(bank*8192+(at&8191),emu.memType.nesWorkRam)end
local function active()return r('SelectedCharacter')==39 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{frame=frame,updates=updates,source_updates=sourceUpdates,x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),identity=work(2,0xc300)}end
local function encode(v)
 if type(v)=='table'then local out={};for k,x in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(x)end;return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function finish(ok,reason)
 if done then return end;done=true
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=reason,ROM_SHA256=expectedRom,name=identity==0 and 'BUB'or'BOB',controller_only=true,runtime_state_writes=0,capture_files=0,physical_frames=frame,Main_updates=updates,source_updates=sourceUpdates,entered_Main=enteredMain,returned_Main_histogram=returns,entry_return_histogram=entries,source_outside_pending=sourceOutside,phases=phases,first_enemy=firstEnemy,terminal=state()}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function mapped(pc,kind,offset)local a=emu.convertAddress(pc);return a and a.memType==kind and a.address==offset end
local function header(bank)local out={};for at=0x1fe0,0x1fef do out[#out+1]=string.format('%02x',work(bank,at))end;return table.concat(out)end
local function actors()
 local out={}
 for slot=0,5 do local flag=read(F.Enemy_Flag+slot);if flag~=0 then out[#out+1]={slot=slot,flag=flag,id=read(F.Enemy_ID+slot),x=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot),y=read(F.Enemy_Y_Position+slot)}end end;return out
end
local function begin(name,bits)
 phase=name;pad=bits;start={state=state(),polls=physicalPolls,lag=r('NmiSkipped')};last=state()
end
local function close()
 local s=state();assert(s.updates-start.state.updates==s.source_updates-start.state.source_updates,'Every measured source opportunity has a completed Main')
 phases[phase]={physical_frames=s.frame-start.state.frame,Main_updates=s.updates-start.state.updates,source_updates=s.source_updates-start.state.source_updates,input_polled_frames=physicalPolls-start.polls,lag_NMI=(r('NmiSkipped')-start.lag)&255,initial=start.state,terminal=s,empty_actor_windows=true}
end
local function tick()
 local s=state();assert(active() and s.lives==2 and s.identity==identity,'Same living original Bubble identity')
 assert(sourceThisMain==1,'Exactly one original source clock opportunity per completed Main')
 assert(sourceOutside==0,'Every original source opportunity belongs to a tracked Main')
 assert(header(2)==cookie and header(3)==cookie,'Complete two-bank source identity')
 if phase=='settle'then if s.y==176 then begin('idle',0)end
 elseif phase=='idle'or phase=='walk'then
  assert(#actors()==0,'Empty measured scene must contain no live native actors')
  local target=phase=='idle'and 48 or 36
  if updates-start.state.updates>=target then
   close()
   if phase=='idle'then assert(s.x==start.state.x,'Idle retains position');begin('walk',1)
   else assert(s.x>start.state.x+16,'Actual ordinary walk displacement');begin('approach',1)end
  end
 elseif phase=='approach'then
  local list=actors();for _,a in ipairs(list)do if a.id==6 and a.flag>0 and a.flag<128 then firstEnemy={state=s,actor=a};pad=0;finish(true,'Empty idle/walk cadence and separately observed first natural Goomba');return end end
  assert(s.x<240 and updates-start.state.updates<240,'First native enemy approach bound')
 end
end
assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,'Exact current ROM identity')
for _,h in ipairs(hooks)do if h.kind=='rom'then for k=1,#h.data,2 do assert(emu.read(h.offset+(k-1)//2,emu.memType.nesPrgRom)==tonumber(h.data:sub(k,k+1),16),'Current native hook preimage')end end end
emu.addMemoryCallback(guard(function()
 if not game or not active()or not mapped(F.GameLoop,emu.memType.nesPrgRom,hooks[1].offset)then return end
 assert(not pending,'Previous native Main must have a captured return')
 local s=emu.getState();local sp=s['cpu.sp'];pending={pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535,sp=(sp+2)&255};sourceThisMain=0
 local known=false;for _,pc in ipairs(returnPcs)do if pc==pending.pc then known=true end end;assert(known,'Unqualified native Main return caller')
 local key=string.format('%04X/SP%d',pending.pc,pending.sp);entries[key]=(entries[key]or 0)+1;enteredMain=enteredMain+1
end),emu.callbackType.exec,F.GameLoop)
emu.addMemoryCallback(guard(function()
 if game and active()and mapped(sourcePc,emu.memType.nesWorkRam,3*8192+(sourcePc&8191))then sourceUpdates=sourceUpdates+1;sourceThisMain=sourceThisMain+1;if not pending then sourceOutside=sourceOutside+1 end end
end),emu.callbackType.exec,sourcePc)
local function returned()
 if not pending then return end;local c=emu.getState();if c['cpu.pc']~=pending.pc or c['cpu.sp']~=pending.sp then return end
 local key=string.format('%04X/SP%d',pending.pc,pending.sp);returns[key]=(returns[key]or 0)+1
 pending=nil;updates=updates+1;tick()
end
for _,pc in ipairs(returnPcs)do emu.addMemoryCallback(guard(returned),emu.callbackType.exec,pc)end
local function wait(fn)for _=1,1800 do if fn()then return end;coroutine.yield()end;error('Native title/menu/ingress bound')end
local function press(bits)pad=bits;for _=1,4 do coroutine.yield()end;pad=0;for _=1,8 do coroutine.yield()end end
local route=coroutine.create(function()
 wait(function()return frame>=100 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0,'Fresh native menu begins at slot0')
 for _=1,3 do press(4)end;press(1)
 assert(r('CrossoverMenuIndex')==25,'Real D-pad selects visible slot25')
 for _=1,identity+1 do press(32)end;assert(r('SelectedCharacter')==39,'Real Select resolves Bubble source owner')
 press(16);wait(function()return active()end)
 for _,h in ipairs(hooks)do if h.kind=='work'then for k=1,#h.data,2 do assert(emu.read(h.offset+(k-1)//2,emu.memType.nesWorkRam)==tonumber(h.data:sub(k,k+1),16),'Actual cold Bubble runtime code')end end end
 game=true;phase='settle'
end)
emu.addEventCallback(guard(function()polled=true;emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;if polled then physicalPolls=physicalPolls+1 end;polled=false
 if frame>3000 then finish(false,'Physical bound3000');return end
 if coroutine.status(route)~='dead'then local ok,why=coroutine.resume(route);assert(ok,why)end
end),emu.eventType.endFrame)
'''
    # Keep all native state immutable. Only controller peripheral is written.
    assert not any(x in text for x in ('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def cost_controller(raw, identity=0):
    """Add passive inclusive routine costs; retain the frozen baseline API."""
    text=controller(raw,identity)
    b=B.W.Symbols.bundle();b['raw']=raw
    native=('GameLoop','GameCoreRoutine','HuMovement','HuFullBox','HuHead','HuSide',
            'HuVisible','HuWeaponTail','HuDraw','HuUi','X5BounceUiDispatch',
            'DrawAllMetasprites','MetaspriteRenderLoop')
    points=[]
    for name in native:
        if name not in b['syms']:continue
        at=B.W.location(b,name);pc=B.W.address(b,name)
        points.append((name,pc,2,at-16,raw[at:at+8].hex()))
    q,_,_=B.bindings(raw)
    im=(B.R/'build/bub-initial-tier-1103-v87/private-image.bin').read_bytes()
    for name in ('BbNativeUpdate','BbNativeDraw','BbPlayerStep','BbBubbleStep'):
        pc=q['labels'][name]
        points.append((name,pc,3,3*8192+(pc&8191),im[pc-0xa000:pc-0xa000+8].hex()))
    # Include the actual current complete-header helper, not historical labels.
    points.append(('CoCheckCode',0xaee2,2,65*8192+0xee2,raw[16+65*8192+0xee2:16+65*8192+0xeea].hex()))
    declarations='local costPoints={'+','.join(
        '{name="'+n+'",pc='+str(pc)+',kind='+str(kind)+',offset='+str(at)+',data="'+data+'"}'
        for n,pc,kind,at,data in points)+'}\n'
    declarations+='local costs={};local costPending={};local costReturns={}\n'
    before='local function finish(ok,reason)'
    assert text.count(before)==1
    text=text.replace(before,declarations+before)
    before='entered_Main=enteredMain,returned_Main_histogram=returns'
    assert text.count(before)==1
    text=text.replace(before,'inclusive_cycle_profiles=costs,inclusive_costs_include_ISR=true,'+before)
    extra=r'''
-- Every span is inclusive of nested routines and any hardware interrupts.
-- The profile groups cannot be added; each independent function is a lens.
local function costReturn(pc)
 local s=emu.getState();local t=s['cpu.cycleCount'];local keep={}
 for _,p in ipairs(costPending)do
  if pc==p.ret and s['cpu.sp']==p.sp then
   local row=costs[p.phase][p.name];local n=t-p.start
   assert(n>=0,'Monotonic inclusive native cycle clock')
   row.calls=row.calls+1;row.cycles=row.cycles+n;row.maximum=math.max(row.maximum,n)
  else keep[#keep+1]=p end
 end
 costPending=keep
end
for _,point in ipairs(costPoints)do
 local kind=point.kind==2 and emu.memType.nesPrgRom or emu.memType.nesWorkRam
 if point.kind==2 then for k=1,#point.data,2 do assert(emu.read(point.offset+(k-1)//2,kind)==tonumber(point.data:sub(k,k+1),16),'Current cost-profile code')end end
 emu.addMemoryCallback(guard(function()
  if not game or not active()or(phase~='idle'and phase~='walk')or not mapped(point.pc,kind,point.offset)then return end
  local s=emu.getState();local sp=s['cpu.sp'];local ret=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
  costs[phase]=costs[phase]or{};costs[phase][point.name]=costs[phase][point.name]or{calls=0,cycles=0,maximum=0}
  costPending[#costPending+1]={name=point.name,phase=phase,ret=ret,sp=(sp+2)&255,start=s['cpu.cycleCount']}
  if not costReturns[ret]then
   costReturns[ret]=true
   emu.addMemoryCallback(guard(function()costReturn(ret)end),emu.callbackType.exec,ret)
  end
 end),emu.callbackType.exec,point.pc)
end
'''
    before='local function returned()'
    assert text.count(before)==1
    text=text.replace(before,extra+'\n'+before)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw, identity=0, *, lag_cut=False, costs=False,
                 controller_text=None, expected=None):
    """Same Lua after genuine CPU cold/menu; skip duplicate Lua title inputs."""
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    m, startup=B.cold(raw,identity)
    digest=sha256(raw).hexdigest()
    if controller_text is None:
        text=(cost_controller if costs else controller)(raw,identity)
    else:
        assert expected==digest and controller_text.count('"'+digest+'"')==1
        text=controller_text
    marker='local route=coroutine.create(function()\n'
    lo=text.index(marker)+len(marker)
    hi=text.index(' for _,h in ipairs(hooks)do if h.kind==\'work\'',lo)
    bound=text[:lo]+text[hi:]
    lua=LuaRuntime(unpack_returned_tuples=True)
    events, callbacks={},defaultdict(list)
    ctx=dict(cpu=None,status=None,receipt=None,injected=False,outer=0)
    api=lua.table()
    api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType=lua.table_from(dict(exec=0))
    api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def read(at,kind=0):
        return m[at] if kind==0 else m.ram[at//8192][at%8192] if kind==1 else raw[16+at]
    def convert(pc):
        if pc<0x8000:return None
        tag=m.rawtags[(pc-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(pc&8191)))
    def cpu_state():
        c=ctx['cpu']
        return lua.table_from({**{f'cpu.{k}':getattr(c,k) if c else 0 for k in ('pc','sp','a','x','y')},
                               'cpu.cycleCount':c.processorCycles if c else 0})
    def set_input(pad,port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in (('right',1),('left',2),('down',4),('up',8),
            ('start',16),('select',32),('b',64),('a',128)) if pad[name])
    def emit(value):
        if value.startswith('SMB_NATIVE_RECEIPT '):
            ctx['receipt']=json.loads(value.removeprefix('SMB_NATIVE_RECEIPT '))
    api.read,api.convertAddress,api.getState,api.setInput=read,convert,cpu_state,set_input
    api.addMemoryCallback=lambda fn,kind,pc:callbacks[pc].append(fn)
    api.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    api.stop=lambda status:ctx.update(status=status)
    lua.globals().emu,lua.globals().print=api,emit
    lua.globals().os.getenv=lambda name:digest if name=='SMB_STDOUT_ROM_SHA' else None
    lua.execute(bound)
    Base=B.N.NesMPU
    class Observed(Base):
        def step(self):
            ctx['cpu']=self
            if lag_cut and not ctx['injected'] and ctx['outer']>0 and self.pc==0xa152 and m.rawtags[1]==3:
                assert B.N.get(m,'NmiDisable')&128
                ctx['injected']=True
                # Actual busy-NMI vector at an executed original source-clock
                # boundary. No counter, player, actor or ability is supplied.
                self.nmi()
            for fn in callbacks.get(self.pc,()):fn()
            return super().step()
    with patch.object(B.N,'NesMPU',Observed):
        for tick in range(400):
            ctx['outer']=tick
            events[0]();B.frame(m,whole_pass=True)
            events[1]()
            if ctx['status'] is not None:break
    result=dict(passed=ctx['status']==0,name=('BUB','BOB')[identity],startup=startup,
        CPU_Main_NMI=tick+1,receipt=ctx['receipt'],controller_SHA256=sha256(text.encode()).hexdigest(),
        CPU_binding_SHA256=sha256(bound.encode()).hexdigest(),output_files=0,
        actual_busy_NMI_cut=ctx['injected'],
        scope='Actual CPU cold/menu then identical Lua post-ingress controls; model frame counts are not physical cadence. No actor/state seeds.')
    assert result['passed'],result
    if lag_cut:
        assert ctx['injected'] and result['receipt']['returned_Main_histogram'].get('82D0/SP252')==1,result
    return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--cpu',action='store_true')
    p.add_argument('--lag-cut',action='store_true');p.add_argument('--costs',action='store_true');a=p.parse_args()
    raw=B.ROM.read_bytes()
    if a.cpu:
        print(json.dumps([source_check(raw,i,lag_cut=a.lag_cut,costs=a.costs) for i in range(2)]),flush=True)
        raise SystemExit(0)
    cases=[dict(name=('BUB','BOB')[i],bytes=len(t.encode()),SHA256=sha256(t.encode()).hexdigest())
           for i in range(2) for t in (controller(raw,i),)]
    print(json.dumps(dict(passed=True,ROM_SHA256=B.PIN,controllers=cases,output_files=0,
                         scope='Strict binding and Lua syntax only; physical and CPU stream replay remain separate.')))
