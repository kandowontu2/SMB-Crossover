"""Pure f88 Bub/Bob controller binding; retained natural route, stdout only.

No ROM output, emulator launch, state writes or historical build expansion.
The November 3 route is read from its individually authenticated retained file.
"""
from collections import defaultdict
from hashlib import sha256
import argparse
import json
import re
from unittest.mock import patch
from zipfile import ZipFile

import bub_native_noops_1113 as U
import check_bub_current_budget_1113 as B

PIN = 'f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
LEGACY = 'cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
RECEIPT = 'feb66cc4ec1dbe7929a6c3cff93c054f9b3b1efb5d07b05502a1753aee2a3a7d'
LUA_SHA = {
    (0,'mushroom'):'f848ad7065ecf9a026eeb98b4cc9d12c88231afcadf53bbe6a6d4fc55194c3eb',
    (0,'full11'):'1c764ce0e76923816e6d0d1a079ab6b8549ebfefd41cda00764fc9fa5c2f059b',
    (1,'mushroom'):'e631b0e6c42825f4ba608a3fb6f166213ed3680f8a592e4f975c7ed65163b2a5',
    (1,'full11'):'1d60813d2910cd143ea73e2783c578c428fdbcd0354420d03b2ce3b236daac86',
}


def retained(identity, mode):
    name = ('bub', 'bob')[identity]
    path = B.R / f'build/bub-earned-delivery-1103-v98/downloads-{name}-{mode}/controller.lua'
    cp = B.R / 'docs/qa/checkpoints/2026-11-03/bub-earned-delivery-v99/receipt.json'
    assert sha256(cp.read_bytes()).hexdigest() == RECEIPT
    receipt = json.loads(cp.read_text())
    assert receipt['passed'] and receipt['installed'] and receipt['ROM_SHA256'] == LEGACY
    member=path.relative_to(B.R).as_posix()
    if path.exists():data=path.read_bytes()
    else:
        archive=cp.with_name('inputs.zip')
        assert sha256(archive.read_bytes()).hexdigest()==receipt['archive_SHA256']
        with ZipFile(archive)as z:data=z.read(member)
    assert sha256(data).hexdigest()==receipt['bindings'][member]
    return data.decode().replace('\r\n','\n')


def replace_once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new)


def legacy_route(identity, mode):
    old = retained(identity, mode)
    start = old.index('local obstacles=')
    end = old.index('local log=assert(io.open', start)
    text = old[start:end]
    # Remove diagnostic-only contact snapshots/callbacks. Control decisions and
    # all source support/cooldown/direction tests remain the retained policy.
    a = text.index('-- Same source-contact observer;')
    z = text.index('local full_rearm_target', a)
    text = text[:a] + 'local function full_contact_sample()end\n' + text[z:]
    a = text.index('local function full_write(')
    z = text.index('local function full_fail(', a)
    text = text[:a] + '''local function full_write(ok,why,q)
 routeResult={passed=ok,reason=why,clears=full_clears,pops=q.pops,captures=q.captures,
 launches=q.launches,rides=q.source_bubble_ride_restarts,jumps=q.source_total_jump_starts,
 current_x=full_x(),current_y=r('Player_Y_Position'),part=full_part,index=full_index,
 world=r('WorldNumber'),level=r('LevelNumber'),engine=r('GameEngineSubroutine'),
 helpers_added=false,initial_lives=full_lives,final_lives=r('NumberofLives')}
end
''' + text[z:]
    a = text.index(' full_last=full_base.completed_Main;full_csv=assert(io.open')
    z = text.index(' full_pad={right=true}', a)
    text = text[:a] + ' full_last=full_base.completed_Main\n' + text[z:]
    a = text.index(' if q.completed_Main%8==0 then')
    z = text.index(" if full_part=='grow'", a)
    text = text[:a] + text[z:]
    # Require living settled 1-2, not merely its first active frame.
    a = text.index(" if r('WorldNumber')==0 and r('LevelNumber')==1 and engine==8 then")
    z = text.index(" if r('SelectedCharacter')~=39", a)
    text = text[:a] + ''' if r('WorldNumber')==0 and r('LevelNumber')==1 then
  full_pad={}
  if engine==8 and r('Player_Y_Position')==176 and r('Player_State')==0 then
   if q.completed_Main~=settledLast then settledLast=q.completed_Main;settled=settled+1 end
  else settled=0 end
  if settled>=25 then
   assert(#full_clears==7,'All four pipes and three pits recorded')
   assert(q.pops>0 and q.captures>0 and q.source_bubble_ride_restarts>=6,'Actual natural source trap/pop and earned bubble support')
   full_write(true,'Full nonshortcut 1-1 and 25 living grounded 1-2 Main',q);finish(true,routeResult.reason)
  end
  return
 end
''' + text[z:]
    if mode == 'mushroom':
        a = text.index("local upgrade_diag=assert(io.open")
        z = text.index('local function upgrade_item()', a)
        text = text[:a] + text[z:]
        a = text.index("  local _,b0=full_solid")
        z = text.index('  if #upgrade_rows<96', a)
        text = text[:a] + text[z:]
        a = text.index("  local obs=BUB_OBSERVER.finish();assert(obs.passed")
        z = text.index(" if item then upgrade_phase='collect'", a)
        text = text[:a] + '''  assert(q.captures>0 and q.pops>0,'First natural enemy genuinely trapped and popped')
  routeResult={passed=true,source_flags=flags,native_status=r('PlayerStatus'),
   observed_immature=upgrade_immature,observed_mature=upgrade_mature,
   bump_attempts=upgrade_attempts,captures=q.captures,pops=q.pops,rows=upgrade_rows}
  finish(true,'Natural first question-block mushroom and original bubble combat');return
 end
''' + text[z:]
    assert 'io.open' not in text and 'OUTPUT' not in text
    return text, old


def controller(raw, identity=0, mode='full11'):
    assert identity in (0, 1) and mode in ('full11', 'mushroom')
    assert sha256(raw).hexdigest() == PIN
    parent = U.combined_reverse(raw)
    assert sha256(parent).hexdigest() == B.PIN and U.combined_proposal(parent)[0] == raw
    text = U.controller(raw, identity, combined=True)
    route, old = legacy_route(identity, mode)
    b = B.W.Symbols.bundle(); b['raw'] = raw
    names = set(re.findall(r'\bL\.(\w+)', route)) | set(re.findall(r"\br\(['\"](\w+)['\"]", route))
    names |= {'Player_Y_HighPos', 'PlayerStatus', 'GuestPowerupActive', 'EnemyMetasprite'}
    fields = {n: B.W.address(b, n) for n in sorted(names)}
    attrs = bytes(map(int, re.search(r'local ROUTE_ATTR=\{([\d,]+)\}', old)[1].split(',')))
    assert len(attrs) == 256 and raw[978758:979014] == attrs
    labels = B.bindings(parent)[0]['labels']
    assert labels['BbNativeObserve'] == 0xb89c
    labels = dict(labels, BbNativeProxyCaptureCommit=labels['BbNativeObserve']-2)
    image = b''.join(raw[1048592+p*1024:1048592+(p+1)*1024] for p in B.PAGES)
    points = []
    for n in ('BbOriginal_D36B', 'BbNativeProxyCaptureCommit'):
        pc = labels[n]
        points.append(dict(name=n,pc=pc,offset=3*8192+(pc&8191),data=image[pc-0xa000:pc-0xa000+4].hex()))
    pc = B.W.address(b, 'EnemyStomped'); at = B.W.location(b, 'EnemyStomped')-16
    points.append(dict(name='EnemyStomped',pc=pc,offset=at,data=raw[16+at:20+at].hex()))
    declarations = 'local L=' + lua(fields) + '\nlocal ROUTE_ATTR=' + lua(list(attrs)) + '\n'
    declarations += 'local routePoints=' + lua(points) + '\n'
    declarations += '''local Q={launch={bob=identity}}
local BUB_NATIVE_OBSERVER_CONFIG={ram=L,hooks={}}
local age,settled,settledLast=0,0,-1
local routeResult=nil
local function ram(at)return read(at)end
local function shot()end
local counts={captures=0,pops=0,launches=0,source_bubble_ride_restarts=0,source_total_jump_starts=0,native_enemy_stomps=0}
local tokens,pool={},{}
local function sampleBubble()
 for i=0,14 do local on=work(2,0x88+4*i)~=0;if on and not pool[i]then counts.launches=counts.launches+1 end;pool[i]=on end
 for i=0,5 do
  local at=0x320+16*i;local on=work(2,at)~=0
  if not on and tokens[i]then
   if read(L.Enemy_ID+i)==tokens[i] and read(L.Enemy_State+i)&32~=0 then counts.pops=counts.pops+1 end
   tokens[i]=nil
  end
 end
end
local BUB_OBSERVER={}
function BUB_OBSERVER.summary()local q={passed=true,failures=0,completed_Main=updates};for k,v in pairs(counts)do q[k]=v end;return q end
BUB_OBSERVER.finish=BUB_OBSERVER.summary
for _,h in ipairs(routePoints)do
 if h.name=='BbOriginal_D36B'then
  local bytes={};for k=1,#h.data,2 do bytes[#bytes+1]=tonumber(h.data:sub(k,k+1),16)end
  BUB_NATIVE_OBSERVER_CONFIG.hooks.BbOriginal_D36B={pc=h.pc,physical=h.offset,bytes=bytes}
 end
 emu.addMemoryCallback(guard(function()
  if not game or not active()then return end
  local kind=h.name=='EnemyStomped'and emu.memType.nesPrgRom or emu.memType.nesWorkRam
  if not mapped(h.pc,kind,h.offset)then return end
  for k=1,#h.data,2 do assert(read(h.pc+(k-1)//2)==tonumber(h.data:sub(k,k+1),16),'Actual trap/jump/native contact entry')end
  local x=emu.getState()['cpu.x']
  if h.name=='BbOriginal_D36B'then
   counts.source_total_jump_starts=counts.source_total_jump_starts+1
   if work(2,x+9)~=0 and work(2,x+1)&128~=0 then counts.source_bubble_ride_restarts=counts.source_bubble_ride_restarts+1 end
  elseif h.name=='BbNativeProxyCaptureCommit'then
   assert(x<6 and work(2,0x320+16*x)~=0,'Real source capture commit')
   counts.captures=counts.captures+1;tokens[x]=work(2,0x321+16*x)
  else counts.native_enemy_stomps=counts.native_enemy_stomps+1 end
 end),emu.callbackType.exec,h.pc)
end
'''
    # r() must resolve the additional exact current native labels too.
    declarations = declarations.replace('local L=', 'local L=', 1)
    marker = 'local function r(n)return read(F[n])end'
    text = replace_once(text, marker, "local function r(n)return read(assert(F[n],n))end")
    add_fields = '\n'.join(f'F.{n}={at}' for n,at in sorted(fields.items())) + '\n'
    first_line = text.index('\n') + 1
    text = text[:first_line] + add_fields + text[first_line:]
    a = text.index('local function tick()')
    z = text.index("assert(os.getenv('SMB_STDOUT_ROM_SHA')", a)
    tick = '''local routeStarted=false
local function drive()
 if not game or done then return end
 if not routeStarted then
  if not active()or r('Player_Y_Position')~=176 then return end
  routeStarted=true;full_begin()
 end
 full_tick(finish)
 pad=0;for name,bit in pairs({right=1,left=2,down=4,up=8,start=16,select=32,b=64,a=128})do if full_pad[name]then pad=pad|bit end end
end
local function tick()
 assert(sourceThisMain<=1 and sourceOutside==0,'Every source update belongs to one real Main')
 assert(r('NumberofLives')==2 and work(2,0xc300)==identity,'Living exact Bubble identity')
 assert(header(2)==cookie and header(3)==cookie,'Both complete current source cookies')
 sampleBubble();drive()
end
'''
    text = text[:a] + declarations + route + tick + text[z:]
    text = replace_once(text, 'phases=phases,first_enemy=firstEnemy,terminal=state()',
                        'phases=phases,first_enemy=firstEnemy,terminal=state(),route=routeResult')
    # Phase transitions may complete while engine8's actor is not called.
    text = replace_once(text, "if frame>3000 then finish(false,'Physical bound3000');return end",
                        "if frame>40000 then finish(false,'Physical bound40000');return end\n if game then drive()end")
    # Original compact cadence JSON assumed string-only table keys; routes
    # contain arrays, so bind an array-aware deterministic stdout encoder.
    a = text.index('local function encode(v)')
    z = text.index('local function finish(', a)
    text = text[:a] + '''local function encode(v)
 if type(v)=='table'then local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=encode(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..encode(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
''' + text[z:]
    # finish closes over routeResult declared before its definition.
    text = text.replace('local routeResult=nil\n', '')
    text = replace_once(text, 'local function finish(', 'local routeResult=nil\nlocal function finish(')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    assert not any(v in text for v in ('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[identity,mode]
    return text


def lua(value):
    if isinstance(value, dict):
        return '{' + ','.join('['+json.dumps(k)+']='+lua(v) for k,v in value.items()) + '}'
    if isinstance(value, list):
        return '{' + ','.join(lua(v) for v in value) + '}'
    return json.dumps(value, separators=(',', ':'))


def source_check(raw, identity=0, mode='mushroom', maximum=11000):
    """Run identical Lua decisions on actual CPU Main/NMI after real cold/menu."""
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    text = controller(raw, identity, mode)
    m, startup = B.cold(raw, identity)
    marker = 'local route=coroutine.create(function()\n'
    lo = text.index(marker)+len(marker)
    hi = text.index(" for _,h in ipairs(hooks)do if h.kind=='work'",lo)
    bound = text[:lo]+text[hi:]
    runtime = LuaRuntime(unpack_returned_tuples=True)
    events, callbacks = {}, defaultdict(list)
    ctx = dict(cpu=None,status=None,receipt=None)
    api = runtime.table()
    api.memType = runtime.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2))
    api.callbackType = runtime.table_from(dict(exec=0))
    api.eventType = runtime.table_from(dict(inputPolled=0,endFrame=1))
    api.read = lambda at,kind=0: m[at] if kind==0 else m.ram[at//8192][at%8192] if kind==1 else raw[16+at]
    def convert(pc):
        if pc<0x8000:return None
        tag=m.rawtags[(pc-0x8000)//8192]
        return runtime.table_from(dict(memType=2 if tag&128 else 1,address=(tag&127)*8192+(pc&8191)))
    def cpu_state():
        c=ctx['cpu']
        return runtime.table_from({**{f'cpu.{k}':getattr(c,k) if c else 0 for k in ('pc','sp','a','x','y')},
                                   'cpu.cycleCount':c.processorCycles if c else 0})
    def set_input(pad, port):
        assert port==0
        m.controller_pad=sum(bit for name,bit in (('right',1),('left',2),('down',4),('up',8),
            ('start',16),('select',32),('b',64),('a',128)) if pad[name])
    def emit(value):
        if value.startswith('SMB_NATIVE_RECEIPT '):ctx['receipt']=json.loads(value.removeprefix('SMB_NATIVE_RECEIPT '))
    api.convertAddress,api.getState,api.setInput=convert,cpu_state,set_input
    api.addMemoryCallback=lambda fn,kind,pc:callbacks[pc].append(fn)
    api.addEventCallback=lambda fn,kind:events.setdefault(kind,fn)
    api.stop=lambda status:ctx.update(status=status)
    runtime.globals().emu,runtime.globals().print=api,emit
    runtime.globals().os.getenv=lambda name:PIN if name=='SMB_STDOUT_ROM_SHA' else None
    runtime.execute(bound)
    Base=B.N.NesMPU
    class Observed(Base):
        def step(self):
            ctx['cpu']=self
            for fn in callbacks.get(self.pc,()):fn()
            return super().step()
    with patch.object(B.N,'NesMPU',Observed):
        for epoch in range(maximum):
            events[0]();B.frame(m,whole_pass=True);events[1]()
            if ctx['status'] is not None:break
            if epoch%500==499:print(json.dumps(dict(event='route_progress',identity=identity,mode=mode,epoch=epoch+1,state=B.state(m))),flush=True)
    result=dict(passed=ctx['status']==0,identity=identity,mode=mode,ROM_SHA256=PIN,
        controller_SHA256=sha256(text.encode()).hexdigest(),startup=startup,
        scheduler_passes=epoch+1,receipt=ctx['receipt'],output_files=0,
        scope='Actual cold/menu then identical Lua controls through genuine CPU Main/NMI. No actor/position/health/ability seeds. Source scheduler counts are not physical cadence.')
    assert result['passed'],result
    return result


def cold_contracts(raw):
    """Declared forced-blank cold/readback fixtures, separate from route runs."""
    import check_bubble_bobble_common_cold_1102_v4 as C
    from check_ff_head_lifetime_irq_1110 import clone
    parent=U.combined_reverse(raw)
    assert sha256(parent).hexdigest()==B.PIN
    b=B.W.Symbols.bundle();b['raw']=raw
    manager=raw[16+65*8192+0xe00:16+65*8192+0xe14]
    assert manager==bytes.fromhex('08488a489848a900f00808488a489848a90148a2')
    # Bind current compact entry; the old v97 harness's AE0B starts at PHA,
    # skipping current PHP at AE0A and is not a valid current call target.
    retire_pc=0xae0a
    code=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024] for p in B.PAGES)
    cookie=raw[16+65*8192+0xfea:16+65*8192+0xffa]
    assert cookie.hex()=='a72702dac1da2fc79faa02b5b5381392'
    def ready():
        m=C.ready(b);B.N.put(m,SelectedCharacter=39)
        return m
    rows=[]
    for name,fault in (('cold',None),('code-readback',(3,2048)),
                       ('helper-readback',(2,0x1320)),('protected','locked'),
                       ('busy-NMI',None)):
        m=ready()
        if fault=='locked':m.protection=[0,0]
        elif fault:m.corrupt_at=fault
        scratch=bytes(m[3:11]);maps=m.rawtags[:]
        result=C.call(m,0xae00,nmi=name=='busy-NMI')
        assert bytes(m[3:11])==scratch and m.rawtags==maps
        if fault:assert not result['P']&1 and m.ram[2][0x1fe0]!=167
        else:
            assert result['P']&1 and bytes(m.ram[3][:0x1fe0])==code[:0x1fe0]
            assert all(bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie for bank in (2,3))
            reads=m.ppu_reads;writes=len(m.ram_writes)
            warm=C.call(m,0xae00)
            assert warm['P']&1 and m.ppu_reads==reads and len(m.ram_writes)==writes
            if name=='cold':loaded=m
        rows.append(dict(case=name,carry=bool(result['P']&1),minimum_SP=result['min_SP'],
                         busy_NMI_cuts=result['disabled_NMI_cuts']))
    poisoned=0
    for bank in (2,3):
        for off in range(16):
            m=clone(loaded);m.ram[bank][0x1fe0+off]^=1
            before=[bytes(v)for v in m.ram]
            result=C.call(m,0xaee2)
            assert not result['P']&1 and before==[bytes(v)for v in m.ram]
            poisoned+=1
    B.N.put(loaded,SelectedCharacter=0)
    C.call(loaded,retire_pc)
    assert loaded.ram[2][0x1fe0]==loaded.ram[3][0x1fe0]==0
    before=[bytes(v)for v in loaded.ram];C.call(loaded,retire_pc)
    assert before==[bytes(v)for v in loaded.ram]
    return dict(passed=True,ROM_SHA256=PIN,cases=rows,header_poison_rejections=poisoned,
                complete_code_and_two_headers=True,warm_no_copy=True,
                retire_repeat_idempotent=True,output_files=0,
                scope='Explicit cold forced-blank/readback/protection/header-fault fixtures, not naturally corrupted gameplay. Exact code/header load, scratch/maps and existing retire contract.')


def foreign_main(raw, count=32):
    """Combined image compared with actual7ef through genuine foreign cold/Main."""
    parent=U.combined_reverse(raw)
    assert sha256(parent).hexdigest()==B.PIN
    rows=[]
    domains=list(U.ROWS)
    # The shared SMC save/restore table is also used by Steve's cold path.
    # Resolve the actual current Select row rather than copying old slot data.
    inventory=U.Roster.Starts.C.inventory(parent)
    extra={row['name']:row for row in inventory['rows']
           if row['name'] in ('JAY MCCRAY','STEVE HERMANN')}
    assert set(extra)=={'JAY MCCRAY','STEVE HERMANN'}
    domains.extend(extra.values())
    for row in domains:
        if row['name'] in ('BUB','BOB'):continue
        models=[];openings=[]
        for image in (parent,raw):
            b=B.W.Symbols.bundle();b['raw']=image
            opening,m=U.Roster.cold(b,row)
            models.append(m);openings.append(opening)
        assert openings[0]==openings[1]
        cycles=[]
        for epoch in range(count):
            cpus=[];cost=[]
            for m in models:
                m.controller_pad=0 if epoch<4 else 1 if epoch<12 else 128 if epoch<15 else 64 if epoch<24 else 0
                seen=[]
                cost.append(B.frame(m,lambda _m,c:seen.__setitem__(slice(None),[c])))
                cpus.append(seen[0])
            U.compare(*models,*cpus)
            cycles.append(cost[0]-cost[1])
        result=dict(name=row['name'],actual_cold_and60opening_equal=True,
                    complete_additional_Main_NMI=count,CPU_saved=[min(cycles),max(cycles)],terminal=B.state(models[1]))
        rows.append(result)
        print(json.dumps(dict(event='combined_foreign_pair',**result)),flush=True)
    return dict(passed=True,ROM_SHA256=PIN,models=rows,
                complete_AXYP_SP_RAM_SMC_maps=True,output_files=0)


def bindings(raw):
    """Canonical metadata and unchanged route body independent of key order."""
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    runtime=LuaRuntime()
    bundle=B.W.Symbols.bundle();bundle['raw']=raw
    cases=[]
    for identity in (0,1):
        for mode in ('mushroom','full11'):
            text=controller(raw,identity,mode)
            match=re.search(r'^local L=(.*)$',text,re.M)
            fields=dict(runtime.eval(match[1]).items())
            assert all(at==B.W.address(bundle,name) for name,at in fields.items())
            assert not re.search(r'\b(?:i?pairs|next)\s*\(\s*L\s*\)',text)
            backward=lua(dict(reversed(sorted(fields.items()))))
            assert fields==dict(runtime.eval(backward).items())
            alternate=text[:match.start(1)]+backward+text[match.end(1):]
            assert text[:match.start(1)]==alternate[:match.start(1)]
            assert text[match.end(1):]==alternate[match.start(1)+len(backward):]
            runtime.compile(alternate)
            normalized=text[:match.start(1)]+'CANONICAL_FIELD_MAP'+text[match.end(1):]
            cases.append(dict(identity=identity,mode=mode,Lua_bytes=len(text.encode()),
                SHA256=sha256(text.encode()).hexdigest(),field_values=fields,
                declaration_independent_body_SHA256=sha256(normalized.encode()).hexdigest()))
    return dict(passed=True,ROM_SHA256=PIN,cases=cases,
                only_field_declaration_order_canonicalized=True,
                same_native_addresses_and_control_body=True,output_files=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--identity',type=int,choices=(0,1),default=0)
    p.add_argument('--mode',choices=('full11','mushroom'),default='mushroom')
    p.add_argument('--cpu',action='store_true')
    p.add_argument('--cold',action='store_true')
    p.add_argument('--foreign',action='store_true')
    p.add_argument('--bindings',action='store_true')
    args=p.parse_args()
    image,_=U.combined_proposal(B.ROM.read_bytes())
    if args.bindings:result=bindings(image)
    elif args.cold:result=cold_contracts(image)
    elif args.foreign:result=foreign_main(image)
    elif args.cpu:result=source_check(image,args.identity,args.mode)
    else:
        text=controller(image,args.identity,args.mode)
        result=dict(passed=True,ROM_SHA256=PIN,identity=args.identity,mode=args.mode,
                    controller_SHA256=sha256(text.encode()).hexdigest(),Lua_bytes=len(text.encode()),output_files=0)
    print(json.dumps(result,separators=(',',':')),flush=True)
