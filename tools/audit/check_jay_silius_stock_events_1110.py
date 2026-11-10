"""Original Jay stock gun and hurt-service source checks. No files written."""
from collections import Counter
from itertools import product
import json

import check_jay_silius_cold_resident_1110 as J

C, H, N = J.C, J.H, J.N
SOURCE = H.ROOT / 'tools/reference/jay_silius_stock_events_1110.s'
PARENT = 'b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65'
RESIDENT = 'fedcc6eef6d7b6634842872634feee5e3da57517b0c43fd86c07439ac9466454'
VECTOR = 0xb000
RECORDS = slice(0x80, 0xb0)
ORIGINAL_RECORDS = slice(0x3d0, 0x400)
STOP = (0x5b00, 224)
ALIASES = dict(WeaponCooldown=0x52, WeaponSelection=0xb8, DispatchLo=0xf4,
    DispatchHi=0xf5, ScratchDamage=0, ActorXHi=0x10, ActorXLo=0x11, ActorYHi=0x12,
    ActorYLo=0x13, ActorVX=0x14, ActorFlags=0x19, ActorMode=0x1c, ActorHP=0xb0,
    ActorHurt=0x1e, SavedVX=0x504, SavedFlags=0x509, SavedMode=0x50c, SavedHurt=0x50e)
EXTRA_FIELDS = {logical:0xc0b0+i for i,logical in enumerate((0x1e,0x504,0x509,0x50c,0x50e))}
ORIGINAL = ((6,0x81d2,0x81ea),(6,0x844e,0x8480),(6,0x8e39,0x8ea7),
            (6,0xa387,0xa39c),(7,0xc86e,0xc878),(7,0xcd36,0xcd4c),(7,0xea06,0xea6e))


def original_ranges():
    raw = C.Donor.DONOR.read_bytes()
    assert C.digest(raw) == C.Donor.PIN
    result = {}
    for bank,start,end in ORIGINAL:
        off = 16+bank*16384+(start&16383)
        result[f'{bank}:{start:04X}..{end:04X}'] = C.digest(raw[off:off+end-start])
    return result


def resident(donor):
    from deliver_dkjr_four_pipe_1110 import Fix

    predecessor = J.pinned_parent()
    current = Fix.proposal(predecessor)[0]
    assert C.digest(current) == PARENT
    _,trial,program,linked,runtime,stage,cookie,gate,extra,decoder,layout = J.proposal(predecessor,donor)
    out = bytearray(current)
    changes = 0
    for i,(old,new) in enumerate(zip(predecessor,trial['raw'],strict=True)):
        if old != new:
            assert current[i] == old, ('DK/Jay overlap', i)
            out[i] = new
            changes += 1
    assert changes == 3307 and C.digest(out) == RESIDENT
    return dict(trial,raw=bytes(out),b031_source=current),program,linked,runtime,stage,cookie,gate,extra,decoder,layout


def bindings(linked,origin=VECTOR):
    fields = {**linked['ram'],**EXTRA_FIELDS}
    assert not set(linked['ram'].values()) & set(EXTRA_FIELDS.values())
    assert not set(range(0xc080,0xc0b0)) & set(fields.values())
    symbols = {name:fields[logical] for name,logical in ALIASES.items()}
    for name in ('OriginalFreshButtons','OriginalSoundRequest'):
        symbols[name] = linked['symbols'][name]
    symbols['ShotRecords'] = 0xbfb0
    assert [symbols['ShotRecords']+x for x in (0xd0,0xe0,0xf0)] == [0xc080,0xc090,0xc0a0]
    constants = ''.join(f'{k}=${v:04x}\n' for k,v in symbols.items())
    code = H.assemble(constants+SOURCE.read_text(),{'BINDINGS':(origin,512)})
    return code,fields


def install(m,code):
    data = code['images']['BINDINGS']
    m.ram[3][0x1000:0x1000+len(data)] = data


def host_seed(trial,runtime,code):
    m = C.Common.blank(trial)
    m.raw_page(1,3)
    m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2)
    m.ram[3][:len(runtime)] = runtime
    install(m,code)
    return m


def direct(cpu,pc,registers,observe=None):
    cpu.pc = pc
    cpu.a,cpu.x,cpu.y,cpu.p = registers
    cpu.sp = STOP[1]
    cpu.stPushWord(STOP[0]-1)
    C.Motion.run(cpu,STOP,hook=observe)
    return cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp


def differential(donor,host,fields):
    count = Counter()

    def pair(kind,overrides,record_flags,a,p):
        old = C.Donor.fork(donor)
        old.memory.low_bank = 6
        for addr,value in overrides.items():
            old.memory.ram[addr] = value
        old.memory.ram[ORIGINAL_RECORDS] = bytes(range(48))
        for i,flag in enumerate(record_flags):
            old.memory.ram[0x3d9+16*i] = flag
        m = C.Vector.clone(host)
        for logical,physical in fields.items():
            m.ram[2][physical-0xc000] = old.memory.ram[logical]
        m.ram[2][RECORDS] = old.memory.ram[ORIGINAL_RECORDS]
        before = C.Vector.app(m)
        new = N.NesMPU(memory=m)
        registers = (a,0x93,0x56,p)
        entry = (0x81d2,VECTOR) if kind == 'stock' else (0xea06,VECTOR+3)
        old_regs = direct(old,entry[0],registers)
        new_regs = direct(new,entry[1],registers)
        assert old_regs == new_regs, (kind,overrides,record_flags,old_regs,new_regs)
        for logical,physical in fields.items():
            assert old.memory.ram[logical] == m.ram[2][physical-0xc000], (kind,overrides,hex(logical))
        assert old.memory.ram[ORIGINAL_RECORDS] == m.ram[2][RECORDS], (kind,overrides,record_flags)
        after = C.Vector.app(m)
        assert before[:3] == after[:3] and before[4] == after[4]
        allowed = {addr-0xc000 for addr in fields.values()} | set(range(RECORDS.start,RECORDS.stop))
        assert all(before[3][b] == after[3][b] for b in (0,1,3))
        assert {i for i,(x,y) in enumerate(zip(before[3][2],after[3][2])) if x!=y} <= allowed
        count[kind] += 1

    for mask,flags,(now,previous),cooldown,p in product(range(8),(0,2,8,10,12,14),
            ((0,0),(64,0),(64,64),(0,64)),(0,4),(0x20,0xe1)):
        pair('stock',{0x52:cooldown,0xb8:0,0x19:flags,0x10:6,0x11:0xc7,0x12:10,0x13:0xf5,
                      0x162:now,0x163:previous},[bool(mask & (1<<i)) for i in range(3)],83,p)

    for flags,mode,saved,saved_mode,(hp,damage),p in product((0,1,2,3,16,17), (0,2),
            (0,2,16,18),(0,2),((16,2),(1,2),(31,16),(16,0)),(0x20,0xe1)):
        pair('event',{0x19:flags,0x1c:mode,0xb0:hp,0x509:saved,0x50c:saved_mode},
             (1,2,3),damage,p)

    for selection in (1,2,3,4,5,6,255):
        m = C.Vector.clone(host)
        m.ram[2][:256] = bytes(256)
        m.ram[2][fields[0xb8]-0xc000] = selection
        m.ram[2][fields[0x162]-0xc000] = 64
        prior = tuple(map(bytes,m.ram))
        direct(N.NesMPU(memory=m),VECTOR,(83,71,109,0x20))
        assert prior == tuple(map(bytes,m.ram)), selection
        count['unsupported_row_declines'] += 1
    return dict(count)


def scripted_callers(donor,host,linked,code,fields):
    cases = []
    cuts = Counter()
    reached = set()
    event_pcs = {i['pc'] for i in code['instructions'] if i['pc'] >= code['symbols']['TerrainEvent']}
    for flags,mode,saved,saved_mode in ((0,0,0,0),(2,0,0,0),(16,0,0,0),(0,2,0,0),
            (1,0,0,0),(1,0,2,0),(1,0,16,0),(1,0,0,2)):
        old = C.Donor.fork(donor)
        old.memory.low_bank = 6
        # Original scripted projection clips the low relative X and invokes
        # the event while its genuine offscreen flag is already set.
        inputs = {0xba:1,0x10:0x20,0x11:0,0x12:0x0a,0x13:0xf0,0xb0:16,
                  0x30:0,0x31:0,0x32:0,0x33:0,0x19:flags,0x1c:mode,
                  0x509:saved,0x50c:saved_mode,0x53:2}
        for logical,value in inputs.items():
            old.memory.ram[logical] = value
        m = C.Vector.clone(host)
        N.put(m,NmiDisable=255)
        for logical,physical in fields.items():
            m.ram[2][physical-0xc000] = old.memory.ram[logical]
        paths = [[],[]]

        def original(c):
            if c.pc == 0xea06:
                paths[0].append((c.a,c.x,c.y,c.p))

        def relocated(c):
            if c.pc == VECTOR+3:
                paths[1].append((c.a,c.x,c.y,c.p))
            if c.pc in event_pcs and c.pc not in reached:
                reached.add(c.pc)
                for kind in ('NMI','IRQ'):
                    q,d = C.Vector.clone(m,c)
                    before = tuple(map(bytes,q.ram)),tuple(q.rawtags)
                    assert C.Vector.isr(q,d,kind) == 'returned'
                    assert before == (tuple(map(bytes,q.ram)),tuple(q.rawtags)),(kind,hex(c.pc))
                    cuts[kind] += 1

        r = (83,71,109,0x30)
        assert direct(old,0x81ea,r,original) == direct(N.NesMPU(memory=m),
            linked['symbols']['JayPositionSetup'],r,relocated)
        assert paths[0] == paths[1] and len(paths[0]) == 1 and paths[0][0][0] == 16,paths
        for logical,physical in fields.items():
            assert old.memory.ram[logical] == m.ram[2][physical-0xc000],hex(logical)
        final = old.memory.ram
        accepted = not (saved&16 or saved_mode&2) if flags&1 else not (flags&16 or mode&2)
        assert (final[0xb0],final[0xd1],final[0xd0],final[0x53],final[0x1f]) == (
            (0,0x23,2,1,1) if accepted else (16,0x24,3,1,1))
        cases.append(dict(flags=flags,mode=mode,saved_flags=saved,saved_mode=saved_mode,
                          HP=final[0xb0],sound=final[0xd1]))
    return dict(cases=cases,real_vector_cuts=dict(cuts))


def packed_budget(runtime,linked,layout):
    origin = 0xa000+len(runtime)
    code,_ = bindings(linked,origin)
    joined = bytearray(runtime+code['images']['BINDINGS'])
    sites = []
    for i in linked['instructions']:
        if i['op'] == 'JSR' and i['operand'] in (VECTOR,VECTOR+3):
            pc, old = i['pc'],i['operand']
            at = pc-0xa000
            assert joined[at:at+3] == b'\x20'+J.u16(old)
            joined[at+1:at+3] = J.u16(origin+old-VECTOR)
            sites.append(pc)
    assert len(sites)==4,sites
    encoded = len(J.pack(bytes(joined)))
    # Optimistic: append directly after the movement and keep the existing
    # decoder/trampoline size, without billing the changed B admission yet.
    total = encoded+layout['stage']['decoder']+layout['stage']['trampoline']
    assert total>2048
    return dict(relocated_calls=[hex(pc) for pc in sites],adjacent_origin=hex(origin),
                runtime_bytes=len(joined),encoded_bytes=encoded,current_format_total=total,
                overflow_bytes=total-2048)


def with_fire(trial,runtime,extra):
    saved_pad = J.W.address(trial,'SavedJoypadBits')
    assert saved_pad < 256
    guard_prefix = bytes((0xa5,saved_pad,0x29,0x40,0xd0))
    assert runtime.count(guard_prefix) == 1
    guard = runtime.index(guard_prefix)
    disp = runtime[guard+5]
    assert 0xa000+guard+6+(disp if disp<128 else disp-256) == extra['symbols']['Unsupported']
    return runtime[:guard]+b'\xea'*6+runtime[guard+6:]


def opening(trial,runtime,cookie,extra,code,fields,*,detached=True):
    m = C.menu(trial,1,{'images':{}})
    pc_entry = extra['symbols']['PrivateUpdate']
    pc_publish = extra['symbols']['PublishPosition']
    code_pcs = {i['pc'] for i in code['instructions']}
    code_bytes = code['images']['BINDINGS']
    patched_runtime = with_fire(trial,runtime,extra) if detached else runtime
    pads = [0]*4+([64]*8+[0]*2)*4
    calls, reports, cuts, seen = Counter(), [], Counter(), set()
    attached = False
    field = lambda logical: m.ram[2][fields[logical]-0xc000]

    for _ in range(700):
        active = tuple(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine')) == (1,3,8)
        if active and len(reports) == len(pads):
            break
        m.controller_pad = pads[len(reports)] if active else 0

        def observe(memory,cpu):
            nonlocal attached
            if memory.rawtags[1] != 3:
                return
            pc = cpu.pc
            if pc == pc_entry and not attached:
                assert C.Common.headers(m) == (cookie,)*2 and bytes(m.ram[3][:len(runtime)]) == runtime
                assert not any(m.ram[2][RECORDS]) and not any(m.ram[2][0xb0:0xb5])
                # The binding lacks a source-funded carrier. Attach it only
                # in this detached CPU fixture, after real cold verification.
                if detached:
                    m.ram[3][:len(runtime)] = patched_runtime
                    install(m,code)
                assert bytes(m.ram[3][0x1000:0x1000+len(code_bytes)]) == code_bytes
                attached = True
            if pc in (VECTOR,VECTOR+3,pc_entry,pc_publish):
                calls[hex(pc)] += 1
            if pc in code_pcs and pc not in seen:
                seen.add(pc)
                for kind in ('NMI','IRQ'):
                    q,d = C.Vector.clone(m,cpu)
                    before = tuple(map(bytes,q.ram)),tuple(q.rawtags)
                    C.Vector.isr(q,d,kind)
                    assert before == (tuple(map(bytes,q.ram)),tuple(q.rawtags)),(kind,hex(pc))
                    cuts[kind] += 1

        C.Game.frame(m,observe)
        if active:
            assert attached
            shots = bytes(m.ram[2][RECORDS])
            reports.append(dict(now=field(0x162),previous=field(0x163),cooldown=field(0x52),
                live=sum(bool(shots[i]) for i in (9,25,41)),sound=field(0xd1)))
    assert len(reports)==len(pads) and calls[hex(VECTOR)]==len(pads)
    assert not calls[hex(VECTOR+3)] and calls[hex(pc_publish)] == len(pads)
    rising = [i for i,r in enumerate(reports) if r['now']==64 and r['previous']==0]
    births = [i for i,r in enumerate(reports) if r['live']>(reports[i-1]['live'] if i else 0)]
    assert rising==[4,14,24,34] and births==rising[:3], (rising,births,reports)
    for i in births:
        assert reports[i]['cooldown']==4 and reports[i]['sound']==0x12
        assert [r['cooldown'] for r in reports[i+1:i+6]] == [3,2,1,0,0]
    assert reports[-1]['live']==3 and not any(N.get(m,'JnShotKind',i) for i in range(6))
    assert C.Common.headers(m)==(cookie,)*2 and N.get(m,'NumberofLives')==2
    return dict(ordinary_Main=len(reports),genuine_entries=dict(calls),real_new_B_edges=rising,
                spawn_epochs=births,full_pool_refusals=1,native_Mike_shots=0,real_vector_cuts=dict(cuts),
                native_position=[N.get(m,n) for n in ('Player_X_Position','Player_Y_Position')],
                private_attachment='after genuine cold, detached RAM only' if detached else 'native cold copy')


def main():
    donor = C.actual_donor()
    trial,_,linked,runtime,_,cookie,_,extra,_,layout = resident(donor)
    code,fields = bindings(linked)
    host = host_seed(trial,runtime,code)
    print('Jay original bindings paired',pairs:=differential(donor,host,fields),flush=True)
    print('Jay scripted caller paired',script:=scripted_callers(donor,host,linked,code,fields),flush=True)
    data = code['images']['BINDINGS']
    print(json.dumps(dict(passed=True,parent=PARENT,resident=RESIDENT,original_ranges=original_ranges(),
        source=C.digest(SOURCE.read_bytes()),binding_size=len(data),binding_sha=C.digest(data),
        addresses={k:hex(code['symbols'][k]) for k in ('WeaponInput','TerrainEvent')},
        prior_cold_spare=layout['stage']['spare'],carrier=packed_budget(runtime,linked,layout),
        paired=pairs,scripted_callers=script,opening=opening(trial,runtime,cookie,extra,code,fields),
        ROM_written=False,generated_files=0,Mesen=False),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
