"""Compare donor alternate weapon code and a detached Jay host binding."""
from collections import Counter
from itertools import product
import json

import check_jay_silius_stock_draw_dispatch_1111 as Draw

F,J,C,H,N,W = Draw.F,Draw.J,Draw.C,Draw.H,Draw.N,Draw.W
Stock = F.Stock
SOURCE = H.ROOT/'tools/reference/jay_silius_shotgun_1111.s'
PIN = '6cb828b3c97bd287f5fb3421e01a478319bf3615e5f2eeed8a6b7888b15c9657'
LATE_PIN = 'b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576'
COOKIE = bytes.fromhex('a7102007de73e237c21c140b1055419b')
WEAPONS = (0x844e,0x8480,0x84c0,0x85ed,0x8521,0x85a8)
SLOTS = (0xd0,0xe0,0xf0)
SHOT, SUPPORT = 0xb400,0xb800
FIELDS = {0xb1:0xc0be,0xb7:0xc0bf,0x607:0xc0c0,0x608:0xc0c1,0x602:0xc0c2,0x60f:0xc0c3}


def donor_contract():
    raw = C.Donor.DONOR.read_bytes()
    assert C.digest(raw)==C.Donor.PIN
    bus = C.Donor.DonorBus(raw)
    bus.low_bank = 6
    grab = lambda addr,n: bytes(bus[addr+i] for i in range(n))
    assert grab(0x81de,12)==b''.join(map(J.u16,WEAPONS))
    assert grab(0x8518,9)==bytes.fromhex('481a48e65000f0e0d0')
    assert grab(0xd042,2)==J.u16(0xd08f) and grab(0xd08f,8)==J.u16(0xd097)*4
    assert grab(0xd097,5)==bytes((1,0,0,0,0))
    initial, award = grab(0xdcc9,5),grab(0x99cc,5)
    assert initial==bytes.fromhex('02030b0f1f') and award==bytes.fromhex('0108041000')
    return dict(entries=[hex(x) for x in WEAPONS],fresh_mask=initial.hex(),clear_mask=award.hex(),
        pause_select='1:9644',ammo_cost='6:8E20',ammo_drop='7:E82C',spread=grab(0x8518,6).hex())


def natural_donor():
    raw = C.Donor.DONOR.read_bytes()
    cpu,_ = C.Motion.Motion.opening(raw)
    b = cpu.memory
    assert (b.ram[0x170],b.ram[0xb7],b.ram[0xb8],b.ram[0xb1])==(0,2,0,63)
    seen = Counter()
    shots = []

    def frame(pad):
        events = []
        def step():
            bank,pc = b.code_key(cpu.pc)
            name = {(1,0x9644):'select_loop',(1,0x9668):'select_write',(1,0x962c):'exit',
                    (6,0x8093):'live_input',(6,0x84db):'burst'}.get((bank,pc))
            if name:
                events.append(name)
                seen[name] += 1
            if name=='burst':
                shots.append((b.frame,b.ram[0xb1]))
            cpu.step()
        C.Donor.frame(cpu,b,pad,step)
        return events

    frame(8)
    for _ in range(240):
        if 'select_loop' in frame(0):
            break
    else:
        raise AssertionError(('donor pause ingress',b.frame,hex(cpu.pc)))
    for _ in range(240):
        frame(4)
        if b.ram[0xb8]==2:
            break
    else:
        raise AssertionError(('donor pause Select',b.frame,hex(cpu.pc),b.ram[0x608],seen))
    selected = b.frame
    frame(0)
    for i in range(240):
        events = frame(8 if i%12==0 and not seen['exit'] else 0)
        if seen['exit'] and 'live_input' in events:
            break
    else:
        raise AssertionError(('donor resume',b.frame,hex(cpu.pc),seen))
    assert b.ram[0xb8]==2 and b.ram[0xb1]==63
    settled = seen['live_input']+3
    for _ in range(160):
        frame(0)
        if seen['live_input']>=settled:
            break
    else:
        raise AssertionError(('donor pause exit never resumed ordinary input',b.frame,dict(seen)))
    for i in range(80):
        frame(2 if shots or i%6<2 else 0)
        if shots and b.ram[0xb1]==61 and all(b.ram[0x309+x] for x in SLOTS):
            break
    assert len(shots)==1 and b.ram[0xb1]==61,(b.frame,selected,shots,dict(seen),
        b.ram[0xb8],b.ram[0xb1],b.ram[0x162],b.ram[0x163],b.low_bank,hex(cpu.pc))
    records = [bytes(b.ram[0x300+x:0x310+x]) for x in SLOTS]
    assert [(r[4],r[5],r[8],r[15]) for r in records]==[(80,0,0,1),(72,230,0,1),(72,26,0,1)]
    for _ in range(10):
        frame(2)
    assert len(shots)==1 and b.ram[0xb1]==61
    return dict(fresh_mask=2,selected=selected,burst=shots[0],remaining_ammo=61,
                original_three_records=[r.hex() for r in records],held_B_no_repeat=True,trace=dict(seen))


def assemble(trial):
    link = C.Jay.build()
    stock,_ = Stock.bindings(link)
    flight,_,_ = F.code_for(link,{'symbols':{'PublishPosition':0xa834}},stock)
    fields = dict(link['ram'])
    fields.update(FIELDS)
    assert len(set(fields.values()))==len(fields)
    aliases = {name:fields[key] for name,key in dict(WeaponCooldown=0x52,WeaponSelection=0xb8,
        DispatchLo=0xf4,DispatchHi=0xf5,WeaponAmmo=0xb1,WeaponUnlocks=0xb7,
        ScratchDamage=0,ShotOrdinal=0x0f,PadNow=0x162,CameraYHi=0x32,
        QueryY=2,QueryX=3,SelectLock=0x608,PreviousSelection=0x607,SelectionDirty=0x602,
        SelectionDirection=0x60f).items()}
    aliases.update({k:link['symbols'][k] for k in ('OriginalFreshButtons','OriginalSoundRequest','JayHostTile')})
    aliases.update({k:stock['symbols'][k] for k in ('SpawnShot','ApplyShotStance')})
    aliases.update(StockWeaponInput=stock['symbols']['WeaponInput'],StockFlight=flight['symbols']['Flight'],
        StockProject=flight['symbols']['Project'],ShotRecords=0xbfb0,QueryDirection=fields[2]+2,
        NextYLo=0xc0c4,NextYHi=0xc0c5,SideBlocked=0xc0c6,AmmoDropFlags=0xc0c7)
    assert set(range(0xc0c4,0xc0c8)).isdisjoint(fields.values())
    source = ''.join(f'{k}=${v:04x}\n' for k,v in aliases.items())+SOURCE.read_text()
    return H.assemble(source,{'SHOT':(SHOT,512),'SUPPORT':(SUPPORT,512)}),fields,aliases


def stage_seed(trial):
    m = C.menu(trial,1,{'images':{}})
    seed = None
    for _ in range(650):
        m.controller_pad = 0
        def watch(mem,cpu):
            nonlocal seed
            if seed is None and cpu.pc==Stock.VECTOR and m.rawtags[1]==3:
                assert C.Common.headers(m)==(COOKIE,)*2
                seed = C.Vector.clone(m)
        C.Game.frame(m,watch)
        if seed is not None:
            return seed
    raise AssertionError('Actual current stock cold stage did not reach B000')


def attach(m,program):
    for name,pc in (('SHOT',SHOT),('SUPPORT',SUPPORT)):
        data = program['images'][name]
        start = pc-0xa000
        m.ram[3][start:start+len(data)] = data


def donor_input_pairs(donor,seed,program,fields):
    stats = Counter()
    def compare(label,bank,old_pc,params,regs):
        old = C.Donor.fork(donor)
        old.memory.low_bank = bank
        m = C.Vector.clone(seed)
        attach(m,program)
        for key,value in params.items():
            old.memory.ram[key] = value
        for logical,physical in fields.items():
            m.ram[2][physical-0xc000] = old.memory.ram[logical]
        old.memory.ram[0x3d0:0x400] = bytes(48)
        for i in range(3):
            old.memory.ram[0x3d9+i*16] = params.get(0x3d9+i*16,0)
        m.ram[2][0x80:0xb0] = old.memory.ram[0x3d0:0x400]
        if label=='AmmoPickup':
            m.ram[2][0xc7] = old.memory.ram[0x19]
        actor_flags = m.ram[2][fields[0x19]-0xc000]
        a = Stock.direct(old,old_pc,regs)
        b = Stock.direct(N.NesMPU(memory=m),program['symbols'][label],regs)
        assert a==b,(label,params,a,b)
        for logical,physical in fields.items():
            check = 0xc0c7 if label=='AmmoPickup' and logical==0x19 else physical
            assert old.memory.ram[logical]==m.ram[2][check-0xc000],(label,params,hex(logical))
        assert old.memory.ram[0x3d0:0x400]==m.ram[2][0x80:0xb0],(label,params)
        if label=='AmmoPickup':
            assert m.ram[2][fields[0x19]-0xc000]==actor_flags
        stats[label] += 1

    for ammo,buttons,flags,pool in product((0,1,2,3,63),((64,0),(64,64),(0,64)),(0,2,8,10,12),(0,1,2,4)):
        params = {0xb8:2,0xb1:ammo,0x52:0,0x162:buttons[0],0x163:buttons[1],0x19:flags}
        params.update({0x3d9+i*16:int(bool(pool&(1<<i))) for i in range(3)})
        compare('AlternateInput',6,0x81d2,params,(71,87,103,0x31))
    for mask,selection,lock,pad in product((0,2,3,11,15,31),range(6),(0,4),(0,32)):
        compare('PausedSelect',1,0x9644,{0xb7:mask,0xb8:selection,0x608:lock,0x162:pad},(19,25,31,0x30))
    for ammo in (0,1,15,31,47,48,61,62,63):
        compare('AmmoPickup',6,0xe82c,{0xb1:ammo,0x19:31},(1,2,3,0x30))
    return dict(stats)


def donor_flight_pairs(donor,seed,program,fields,aliases):
    report = Counter()
    # Use the real host terrain query and feed its returned class to the
    # donor D002 boundary. Both source CPUs still compute both probes.
    for vx,vy,flags,y in product((0x48,0xb8),(0x1a,0xe6),(1,5),
                                (0xa00,0xafe,0xb00,0xcf0,0xcfe,0xd01,0xeff,0xf00)):
        m = C.Vector.clone(seed)
        attach(m,program)
        old = C.Donor.fork(donor)
        old.memory.low_bank = 6
        for key in (0x30,0x31,0x32,0x33):
            old.memory.ram[key] = m.ram[2][fields[key]-0xc000]
        old.memory.ram[0x300:0x500] = bytes(512)
        initial = bytes((8,0x03,y>>8,y&255,vx,vy,0xe1,0xe2,0,flags,0,0,0,0,0,1))
        m.ram[2][0xa0:0xb0] = initial
        old.memory.ram[0x3f0:0x400] = initial
        queries = []
        ret = None

        def native(c):
            nonlocal ret
            if c.pc==aliases['JayHostTile']:
                assert ret is None
                x,y,d = (c.memory[aliases[k]] for k in ('QueryX','QueryY','QueryDirection'))
                lo,hi = (c.memory[0x100+((c.sp+n)&255)] for n in (1,2))
                ret = (lo+256*hi+1)&0xffff,(c.sp+2)&255,(x,y,d)
            elif ret is not None and (c.pc,c.sp)==ret[:2]:
                queries.append((ret[2],c.a))
                ret = None

        Stock.direct(N.NesMPU(memory=m),program['symbols']['ShotgunFlight'],(0,0xf0,0,0x30),native)
        assert ret is None and len(queries)==2
        assert [r[0][2] for r in queries]==[4 if vx&128 else 6,0 if vy&128 else 2]
        pos = 0

        def original(c):
            nonlocal pos
            if c.pc!=0xd002:
                return False
            (x,y,_),value = queries[pos]
            pos += 1
            assert c.x==2 and (c.memory.ram[3],c.memory.ram[2])==(x,y)
            c.a = value
            c.FlagsNZ(value)
            c.pc = c.stPopWord()+1
            report['blocking_probes' if value else 'clear_probes'] += 1
            return True

        Stock.direct(old,0xc49e,(0,0,0,0x30),original)
        assert pos==2 and old.memory.ram[0x3f0:0x400]==m.ram[2][0xa0:0xb0],(
            vx,vy,flags,y,queries,old.memory.ram[0x3f0:0x400].hex(),m.ram[2][0xa0:0xb0].hex())
        report['full_records'] += 1
    assert report['blocking_probes'] and report['clear_probes']
    return dict(report)


def detached_host_Main(trial,program,fields,aliases):
    m = C.menu(trial,1,{'images':{}})
    m.__class__ = Draw.DmaBus
    m.dma = None
    attach_done = False
    records = []
    prior = []
    calls = Counter()
    for _ in range(650):
        active = tuple(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)
        if active and len(records)==22:
            break
        m.controller_pad = 64 if active and 4<=len(records)<20 else 0
        m.dma = None

        def watch(mem,cpu):
            nonlocal attach_done
            if m.rawtags[1]!=3:
                return
            if cpu.pc==Stock.VECTOR and not attach_done:
                assert C.Common.headers(m)==(COOKIE,)*2
                assert m.ram[3][0x1000:0x1003]==bytes.fromhex('4c06b0')
                assert m.ram[3][0x1247:0x124a]==b'\x20'+J.u16(aliases['StockFlight'])
                attach(m,program)
                m.ram[3][0x1001:0x1003] = J.u16(program['symbols']['AlternateInput'])
                m.ram[3][0x1248:0x124a] = J.u16(program['symbols']['ShotgunFlight'])
                # Declared fixture state from the real donor new-game pause
                # selection. The production SMB pause/pickup route is open.
                for key,value in ((0xb7,2),(0xb8,2),(0xb1,63)):
                    m.ram[2][fields[key]-0xc000] = value
                attach_done = True
            if cpu.pc==program['symbols']['AlternateInput']:
                calls['input'] += 1
            elif cpu.pc==program['symbols']['SpreadFlight']:
                calls['angled_rounds'] += 1

        C.Game.frame(m,watch)
        if active:
            assert attach_done and N.get(m,'NumberofLives')==2
            if prior:
                assert m.dma is not None and sorted(Draw.cells(m.dma))==prior
                assert m.chr_latches[0]==216
            round_state = [bytes(F.slot(m,x)) for x in SLOTS if F.slot(m,x)[9]]
            prior = sorted(bytes((r[7]-8,40,0,r[6]-4)) for r in round_state)
            assert sorted(Draw.cells(m[0x200:0x300]))==prior
            records.append(dict(ammo=m.ram[2][0xbe],rounds=[(r[6],r[7],r[4],r[5]) for r in round_state]))
    assert len(records)==22 and calls['input']==22 and calls['angled_rounds']>0
    assert [r['ammo'] for r in records]==[63]*4+[61]*18
    first = records[4]['rounds']
    assert [(r[2],r[3]) for r in first]==[(80,0),(72,230),(72,26)]
    return dict(scope='detached post-cold binding with directed donor selection',updates=22,first_three_rounds=first,
                no_held_repeat=True,lives=2,private_calls=dict(calls),ammo=records[-1]['ammo'])


def main():
    print('Jay donor weapon contract',donor_contract(),flush=True)
    donor_opening = natural_donor()
    print('Jay actual donor alternate',donor_opening,flush=True)
    raw = H.ROM.read_bytes()
    parent = C.digest(raw)
    assert parent in (PIN,LATE_PIN),parent
    trial = dict(W.Symbols.bundle(),raw=raw)
    program,fields,aliases = assemble(trial)
    print('Jay proposed alternate assembly',program['used'],flush=True)
    seed = stage_seed(trial)
    donor = C.actual_donor()
    pairs = donor_input_pairs(donor,seed,program,fields)
    print('Jay paired alternate inputs',pairs,flush=True)
    flight = donor_flight_pairs(donor,seed,program,fields,aliases)
    print('Jay paired alternate flight',flight,flush=True)
    print(json.dumps(dict(passed=True,donor=donor_opening,assembly=program['used'],
        directed_pairs=pairs,flight_pairs=flight,detached_host_Main=detached_host_Main(trial,program,fields,aliases),
        source=C.digest(SOURCE.read_bytes()),parent=parent,ROM_written=False,Mesen=False,generated_files=0),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
