"""Ordinary controller access to Steve's two stock 1-1 powerup blocks."""

from collections import Counter,defaultdict
import json
from unittest.mock import patch

import check_jay_silius_scene_lifecycle_1110 as Scene
import check_roster_powerup_continuation_1110 as Frames
import check_steve_shatterhand_live_1111 as Punch
import replay_steve_route_1111 as Route
import steve_armor_idle_1113 as Idle


Native = Idle.Native
N,W = Native.Roster.N,Native.Roster.W
FRAME = Frames.frame


def opening(candidate):
    bundle = W.Symbols.bundle()
    bundle['raw'] = candidate
    m = Scene.menu(bundle,2)
    idle = W.address(bundle,'IdleLoop')
    for update in range(480):
        if Punch.mode(m) == (1,3,8):
            return m,update
        m.controller_pad = 0
        W.clear_logs(m)
        N.consume(m)
        cpu = N.NesMPU(memory=m,pc=idle)
        cpu.sp,cpu.p = 255,0x31
        cpu.stPushWord(0xe33b)
        for _ in range(4_000_000):
            if (cpu.pc,cpu.sp) == (idle+12,252):
                break
            assert m[cpu.pc],('BRK',hex(cpu.pc))
            cpu.step()
        else:
            raise AssertionError(('Steve natural cold frame bound',hex(cpu.pc)))
    raise AssertionError('Steve natural active-stage bound')


class Controller:
    def __init__(self,model):
        self.model = model
        self.updates = 0
        self.events = []
        self.calls = Counter()
        self.targets = {
            (((W.location(model.bundle,name)-16)//8192)|128,W.address(model.bundle,name)):name
            for name in ('JnPreparePickup','JnCollectPickup','HandlePowerUpCollision','JnDefeat','JnInjury')}

    def state(self):
        m = self.model
        return dict(update=self.updates,x=Punch.player(m)[0],y=Punch.player(m)[1],
                    player_state=N.get(m,'Player_State'),source_move=m[0x5c92],
                    health=N.get(m,'JnHealth'),lives=N.get(m,'NumberofLives'),
                    camera=Route.camera(m),pattern=m.ram[2][0x1f1],
                    pending=m.ram[2][0x3fd],robot=m.ram[2][0x1f6],
                    armor=m.ram[2][0x1f2],actor_flag=N.get(m,'Enemy_Flag',5),
                    actor_state=N.get(m,'Enemy_State',5),
                    native_kind=N.get(m,'PowerUpType',5),
                    token=N.get(m,'InvPickup',5),
                    actor_x=N.get(m,'Enemy_X_Position',5)+256*N.get(m,'Enemy_PageLoc',5),
                    actor_y=N.get(m,'Enemy_Y_Position',5))

    def observe(self,m,cpu):
        if cpu.pc < 0x8000:
            return
        bank = m.rawtags[(cpu.pc-0x8000)//8192]
        name = self.targets.get((bank,cpu.pc))
        if name:
            self.calls[name] += 1
            if name != 'JnDefeat':
                extra = {}
                if name == 'JnInjury' and cpu.x < 6:
                    extra = dict(enemy_slot=cpu.x,enemy_id=N.get(m,'Enemy_ID',cpu.x),
                                 enemy_x=N.get(m,'Enemy_X_Position',cpu.x)+256*N.get(m,'Enemy_PageLoc',cpu.x),
                                 enemy_y=N.get(m,'Enemy_Y_Position',cpu.x))
                self.events.append(dict(routine=name,A=cpu.a,X=cpu.x,Y=cpu.y,**extra,**self.state()))

    def frame(self,pad=0,observe=None):
        m = self.model
        m.controller_pad = pad
        health = N.get(m,'JnHealth')
        self.updates += 1
        def visit(model,cpu):
            self.observe(model,cpu)
            if observe:
                observe(model,cpu)
        FRAME(m,visit)
        if N.get(m,'JnHealth') != health:
            self.events.append(dict(routine='native_health_change',before_health=health,**self.state()))
        assert Punch.mode(m) == (1,3,8) and N.get(m,'NumberofLives') == 2,self.state()
        assert N.get(m,'JnHealth') > 0,self.state()

    def existing_frame(self,model,observe=None):
        assert model is self.model
        self.frame(model.controller_pad,observe)

    def walk(self,target):
        for _ in range(240):
            gap = target-Punch.player(self.model)[0]
            if abs(gap) <= 1:
                return
            self.frame(1 if gap > 0 else 2)
        raise AssertionError(('Natural token approach bound',target,self.state()))

    def token(self,block,approach,launch,expected_pattern):
        m = self.model
        before = dict(self.calls)
        self.walk(approach)
        for _ in range(7):
            self.frame()
        reveal = self.state()
        for age in range(62):
            self.frame(128 if age < 9 else 0)
        mature = self.state()
        assert (mature['actor_x'],mature['actor_y'],mature['token'],mature['actor_state']) == (
            block,120,0x8c,128),mature
        self.walk(launch)
        for _ in range(9):
            self.frame()
        takeoff = self.state()
        for age in range(90):
            self.frame(129 if age < 9 else 1)
            if m.ram[2][0x3fd]:
                break
        else:
            raise AssertionError(('Natural token collection bound',block,self.state()))
        contact = self.state()
        assert contact['pending'] == expected_pattern and not contact['actor_flag'] and not contact['token'],contact
        for flight in range(80):
            self.frame()
            if not m.ram[2][0x3fd]:
                break
        else:
            raise AssertionError(('Natural token HUD flight bound',block,self.state()))
        final = self.state()
        assert final['pattern'] == expected_pattern,final
        for routine in ('JnPreparePickup','JnCollectPickup','HandlePowerUpCollision'):
            assert self.calls[routine] > before.get(routine,0),(block,routine,self.calls)
        result = dict(block_world_left=block,block_top=144,reveal=reveal,mature=mature,
                      takeoff=takeoff,contact=contact,collection_updates=age+1,
                      flight_updates=flight+1,final=final)
        print(json.dumps(dict(event='natural_Steve_token',**result),sort_keys=True),flush=True)
        return result


def check(candidate,info, *, first_only=False):
    assert Native.Packet.Entry.digest(candidate) == Native.IDLE_CANDIDATE
    m,startup = opening(candidate)
    assert bytes(m.ram[1][0x1fe0:0x1ff0]) == info['cookie']
    assert tuple(bytes(m.ram[b][0x1fe0:0x1ff0]) for b in (2,3)) == (info['cookie'],)*2
    route = Controller(m)
    _,punch,_ = Native.Live.Wave.incumbent(Idle.reverse(candidate))
    assert Punch.C.Game is Frames and Route.S.C.Game is Frames
    for pad in [0]*6+[64]*12+[0]*6:
        route.frame(pad)
    with patch.object(Frames,'frame',route.existing_frame):
        fight = Punch.natural_goomba(m,dict(symbols=punch))
    assert fight['score'] == 1 and N.get(m,'JnHealth') == 6
    first = route.token(336,329,302,1)
    second = None
    if not first_only:
        with patch.object(Frames,'frame',route.existing_frame):
            crossing = Route.continue_route(m,target=1236,max_updates=2500)
        assert (crossing['x'],crossing['y'],crossing['health']) == (1236,176,6),crossing
        second = route.token(1248,1239,1214,5)
    else:
        crossing = None
    return dict(candidate=Native.IDLE_CANDIDATE,menu_startup_updates=startup,
                controller_updates=route.updates,fight=fight,first=first,crossing=crossing,
                second=second,native_calls=dict(route.calls),native_events=route.events,
                terminal=route.state(),runtime_state_writes=0,new_helpers=0,
                output_files=0,Mesen_run=False,
                scope='Exact unmodified62ba stock1-1. Actual native menu/parser and ordinary controller frames reveal, prepare, mature and collect the authored powerups. Steve transports them as original Alpha tokens.')


NATURAL_TAIL = r'''
local pickupPoints={{left=336,approach=329,launch=302,pattern=1},
  {left=1248,approach=1239,launch=1214,pattern=5}}
local pickupFields={NATURAL_FIELDS}
local function naturalNative(name,callback)
  local at,bank=pickupFields[name],pickupFields[name..'Bank']
  emu.addMemoryCallback(guard(function()
    local mapped=emu.convertAddress(at)
    if active() and mapped and mapped.memType==emu.memType.nesPrgRom
      and mapped.address==bank*8192+(at&8191)then callback()end
  end),emu.callbackType.exec,at)
end
naturalNative('JnPreparePickup',function()
  local slot=emu.getState()['cpu.x']
  assert(slot==5 and read(pickupFields.Enemy_ID+slot)==46,'Actual native powerup preparation')
  local wx=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot)
  assert(wx==pickupPoints[natural.index].left,'Authored question-block actor location')
  natural.preparations=natural.preparations+1
  natural.kinds[natural.index]=read(pickupFields.PowerUpType+slot)
end)
naturalNative('JnCollectPickup',function()
  local slot=emu.getState()['cpu.x']
  assert(slot==5 and read(pickupFields.InvPickup+slot)==0x8c,'Original Alpha token native collection')
  natural.collections=natural.collections+1
end)
local function naturalPhase(nextPhase,bits)
  phase=nextPhase;natural.since=updates;pad=bits
end
local function naturalApproach(target,nextPhase)
  local gap=target-x()
  if math.abs(gap)<=1 then naturalPhase(nextPhase,0)
  else pad=gap>0 and 1 or 2 end
end
local function naturalTick()
  if projections==natural.lastProjection then return end
  natural.lastProjection=projections
  local point=pickupPoints[natural.index]
  local age=updates-natural.since
  local hp=read(0x5f30)
  assert(active() and read(0x75f)==2 and hp>0,'Living Steve stock pickup route')
  if phase=='natural-approach'then
    naturalApproach(point.approach,'natural-settle')
    assert(age<240,'Question-block approach bound')
  elseif phase=='natural-settle'then
    if age>=7 then naturalPhase('natural-reveal',128)end
  elseif phase=='natural-reveal'then
    pad=age<9 and 128 or 0
    if age>=62 then
      local slot=5
      local wx=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot)
      assert(wx==point.left and read(pickupFields.Enemy_Y_Position+slot)==120
        and read(pickupFields.Enemy_State+slot)==128 and read(pickupFields.InvPickup+slot)==0x8c,
        'Actual native emergence and mature Alpha token')
      naturalPhase('natural-return',2)
    end
  elseif phase=='natural-return'then
    naturalApproach(point.launch,'natural-launch-settle')
    assert(age<240,'Collection launch approach bound')
  elseif phase=='natural-launch-settle'then
    if age>=9 then naturalPhase('natural-collect',129)end
  elseif phase=='natural-collect'then
    pad=age<9 and 129 or 1
    if work(2,0xc3fd)>0 then
      assert(work(2,0xc3fd)==point.pattern and read(pickupFields.Enemy_Flag+5)==0
        and read(pickupFields.InvPickup+5)==0,'Native collection erases authored actor')
      naturalPhase('natural-flight',0)
    end
    assert(age<90,'Natural token collection bound')
  elseif phase=='natural-flight'then
    if work(2,0xc3fd)==0 then
      assert(work(2,0xc1f1)==point.pattern,'Original collected pattern committed after HUD flight')
      natural.items=natural.items+1
      if natural.index==1 then
        natural.index=2;beginFull();naturalPhase('natural-traverse',1)
      else
        assert(natural.items==2 and natural.preparations==2 and natural.collections==2,
          'Both authored native powerups earned and collected')
        finish(true,'Steve earns the stock336 and1248 powerups as original Alpha tokens')
      end
    end
    assert(age<80,'Original token HUD flight bound')
  elseif phase=='natural-traverse'then
    if x()>=1236 and read(0xbd)==176 and read(0x1e)==0 then
      naturalPhase('natural-approach',1)
    else fullTick()end
  end
end
'''


def controller(candidate,info):
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    assert Native.Packet.Entry.digest(candidate) == Native.IDLE_CANDIDATE
    lua = Native.controller(candidate,info,mode='full_stage')
    def change(before,after):
        nonlocal lua
        assert lua.count(before) == 1,before
        lua = lua.replace(before,after)
    bundle = W.Symbols.bundle()
    bundle['raw'] = candidate
    fields = {name:W.address(bundle,name) for name in
              ('Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position',
               'Enemy_State','Enemy_Flag','InvPickup','PowerUpType','JnPreparePickup','JnCollectPickup')}
    for name in ('JnPreparePickup','JnCollectPickup'):
        fields[name+'Bank'] = (W.location(bundle,name)-16)//8192
    tail = NATURAL_TAIL.replace('NATURAL_FIELDS',','.join(f'{name}={value}' for name,value in fields.items()))
    change('local full,beginFull,fullTick',
           'local full,beginFull,fullTick\nlocal natural={index=1,since=0,lastProjection=-1,items=0,preparations=0,collections=0,kinds={}}')
    change("      phase='motion-crouch';motionStart=updates;pad=4",
           "      phase='natural-approach';natural.since=updates;pad=1")
    change('local function tick()',tail+"\nlocal function tick()\n  if phase:sub(1,8)=='natural-' then naturalTick();return end")
    change('header(2)==cookie and header(3)==cookie',
           'header(1)==cookie and header(2)==cookie and header(3)==cookie')
    change('right=pad&1~=0,down=pad&4~=0',
           'right=pad&1~=0,left=pad&2~=0,down=pad&4~=0')
    change('"route_crossings":[%s],"route_jumps":[%s]}',
           '"route_crossings":[%s],"route_jumps":[%s],"natural_items":%d,"source_pattern":%d,"native_preparations":%d,"native_collections":%d,"prepare_kinds":[%d,%d]}')
    change('full and table.concat(full.jumps,",") or ""))',
           'full and table.concat(full.jumps,",") or "",natural.items,work(2,0xc1f1),natural.preparations,natural.collections,natural.kinds[1] or -1,natural.kinds[2] or -1))')
    assert 'emu.write' not in lua and 'emu.setState' not in lua
    assert Native.Packet.Entry.digest(DLL.read_bytes()) == DLL_SHA
    LuaRuntime().compile(lua)
    return lua


def controller_cpu(candidate,info, *, limit=2400):
    """Use the native Lua decisions with actual Main/NMI and modeled OAM DMA."""
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    m,startup = opening(candidate)
    text = controller(candidate,info)
    begin = 'local route=coroutine.create(function()\n'
    lo = text.index(begin)+len(begin)
    hi = text.index("  phase='settle'\n",lo)
    bound = text[:lo]+text[hi:]
    lua = LuaRuntime(unpack_returned_tuples=True)
    events,callbacks = {},{0:defaultdict(list),1:defaultdict(list)}
    context = dict(cpu=None,exit=None,receipt=None,sprite=bytes([248])*256)
    emu = lua.table()
    emu.memType = lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesSpriteRam=3))
    emu.eventType = lua.table_from(dict(inputPolled=0,endFrame=1))
    emu.callbackType = lua.table_from(dict(exec=0,write=1))
    def read(at,kind=0):
        if kind == 1:
            return m.ram[at//8192][at%8192]
        if kind == 2:
            return candidate[16+at]
        if kind == 3:
            return context['sprite'][at]
        assert kind == 0,kind
        return m[at]
    def mapped(pc):
        if pc < 0x8000:
            return None
        tag = m.rawtags[(pc-0x8000)//8192]
        return lua.table_from(dict(memType=2 if tag&128 else 1,
                                   address=(tag&127)*8192+(pc&8191)))
    def cpu_state():
        cpu = context['cpu']
        return lua.table_from({f'cpu.{key}':getattr(cpu,key) if cpu else 0
                               for key in ('pc','sp','a','x','y')})
    def set_input(pad,port):
        assert port == 0
        m.controller_pad = sum(bit for name,bit in (
            ('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))
            if pad[name])
    def emit(value):
        if value.startswith('SMB_NATIVE_RECEIPT '):
            context['receipt'] = json.loads(value.removeprefix('SMB_NATIVE_RECEIPT '))
    def add_memory(fn,kind,lo,hi=None):
        for pc in range(lo,lo+1 if hi is None else hi+1):
            callbacks[kind][pc].append(fn)
    emu.read,emu.convertAddress,emu.getState,emu.setInput = read,mapped,cpu_state,set_input
    emu.addEventCallback = lambda fn,kind:events.setdefault(kind,fn)
    emu.addMemoryCallback = add_memory
    emu.stop = lambda code:context.update(exit=code)
    lua.globals().emu,lua.globals().print = emu,emit
    lua.globals().os.getenv = lambda name:Native.IDLE_CANDIDATE if name == 'SMB_STDOUT_ROM_SHA' else None
    lua.execute(bound)
    ParentBus,ParentMPU = type(m),N.NesMPU
    class ObservedBus(ParentBus):
        def __setitem__(self,at,value):
            if isinstance(at,int):
                if at == 0x4014 and value == 2:
                    context['sprite'] = bytes(self[0x200:0x300])
                for fn in tuple(callbacks[1].get(at,())):
                    fn(at,value)
            return super().__setitem__(at,value)
    class ObservedMPU(ParentMPU):
        def step(self):
            context['cpu'] = self
            for fn in tuple(callbacks[0].get(self.pc,())):
                fn()
            return super().step()
    m.__class__ = ObservedBus
    try:
        with patch.object(N,'NesMPU',ObservedMPU):
            for tick in range(limit):
                events[0]()
                FRAME(m)
                events[1]()
                if context['exit'] is not None:
                    break
    finally:
        m.__class__ = ParentBus
    result = dict(passed=context['exit']==0,stopped=context['exit'] is not None,
                  candidate=Native.IDLE_CANDIDATE,menu_startup_updates=startup,
                  controller_updates=tick+1,receipt=context['receipt'],
                  controller_SHA256=Native.Packet.Entry.digest(text.encode()),
                  CPU_binding_SHA256=Native.Packet.Entry.digest(bound.encode()),
                  runtime_state_writes=0,new_helpers=0,output_files=0,Mesen_run=False,
                  scope='Actual native cold/menu/parser and Main/NMI with the readonly Lua controller. Title navigation in Lua is skipped after actual cold ingress. Sprite DMA is modeled by copying native OAM on its actual DMA write.')
    assert result['passed'],result
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-only',action='store_true')
    parser.add_argument('--lua',action='store_true')
    args = parser.parse_args()
    raw = Native.Live.Art.D.HOST.read_bytes()
    if Native.Packet.Entry.digest(raw) == Native.IDLE_CANDIDATE:
        raw = Idle.reverse(raw)
    candidate,info = Idle.proposal(raw)
    result = controller_cpu(candidate,info) if args.lua else check(candidate,info,first_only=args.first_only)
    print(json.dumps(result,sort_keys=True),flush=True)
