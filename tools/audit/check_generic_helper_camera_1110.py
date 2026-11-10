"""Qualify generic helper births and injury retry on exact f003, in memory."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_enemy_ordinary_dispatch_irq_1110 as IRQ
import profile_mini_busy_1108_v1 as P
from check_helper_camera_admission_1110_v1 import bank_at, geometry, patch
from check_mini_funded_actor_1108_v3 import install, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_lift_admission_async_1108_v1 import final, live, tags
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at, lag_pcs
from check_mini_visibility_dispatch_1110_v1 import memory


R, N = P.R, P.N
BASE = R/'build/mini-helper-powered-injury-native-1110/candidate.nes'
PIN = 'f003b378b0e5bd862403eae71f267d8c33a3b06e9270548ae20b1d9f6b2f9979'
PACKED = R/'build/wwf-helper-stable-1102-v2/proposed.bin'
FOOTER = R/'build/helper-camera-admission-1110/proof.json'
SOURCE = R/'tools/reference/generic_helper_camera_1110.s'
SPANS = (('HELPER_LOOP',0xad2b,0xad63),('HELPER_NEXT',0xadcd,0xadd3),
         ('HELPER_MARGIN',0xadd4,0xae22),('HELPER_FOOTER',0xb31a,0xb32a))
LOAD, TICK, MARGIN, CTOR = 0xab65,0xad0b,0xadd4,(130,0xa74f)
HP = slice(0x7382,0x73dd)
ACTOR_FIELDS = ('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc',
                'Enemy_Y_Position','Enemy_Y_HighPos','Enemy_BoundBoxCtrl','PlatformCollisionFlag')


def link(before, out):
    packed = PACKED.read_bytes()
    assert len(packed) == 0xb2a
    for _,lo,hi in SPANS[:-1]:
        at = bank_at(26,lo)
        assert before[at:at+hi-lo] == packed[lo-0xa800:hi-0xa800]
    footer = json.loads(FOOTER.read_text())
    assert footer['passed'] and footer['symbols']['DpPlatformEnd']==0xb31a
    assert bytes.fromhex(footer['patches'][2]['new_hex'])[-16:]==b'\xea'*16
    assert before[bank_at(26,0xb31a):bank_at(26,0xb32a)]==b'\xea'*16
    # The current camera-rebased Goku/Karnov path no longer uses this margin.
    bank = before[bank_at(26,0xa000):bank_at(26,0xc000-1)+1]
    assert [i+0xa000 for i in range(len(bank)) if bank.startswith(b'\x20\xd4\xad',i)] == [0xad43]
    assert b'\x4c\xd4\xad' not in bank
    assert before[bank_at(126,0x83c4):bank_at(126,0x83c4)+10] == bytes.fromhex('207b83a200860d2060a2')
    assert before[bank_at(26,0xb134):bank_at(26,0xb134)+12] == bytes.fromhex('ad0260c922f05d4c0badeaea')
    with tempfile.TemporaryDirectory(prefix='link-',dir=out) as name:
        work = Path(name)
        cfg, obj, binary = (work/f'camera.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { '+''.join(f'{n}:start=${lo:04x},size={hi-lo},file=%O;'
                        for n,lo,hi in SPANS)+'}\nSEGMENTS { '+
                       ''.join(f'{n}:load={n},type=ro;' for n,_,_ in SPANS)+'}\n')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        linked = binary.read_bytes()
    rows, used = [],0
    for name,lo,hi in SPANS:
        at = bank_at(26,lo)
        data = linked[used:used+hi-lo]
        rows.append(dict(patch(at,before[at:at+hi-lo],data,name),physical_PRG=26,CPU_half_open=[lo,hi]))
        used += hi-lo
    assert used == len(linked)
    assert rows[1]['old_hex'] == 'eed4734c38ad' and rows[1]['new_hex'] == 'eed4734c3bad'
    after = install(before,rows)
    assert after[bank_at(26,0xad63):bank_at(26,0xadcd)] == before[bank_at(26,0xad63):bank_at(26,0xadcd)]
    return after, rows


def direct(m,pc,visit=None,*,x=0):
    c = cpu_at(m,pc,232,0x21,x=x,y=17)
    run(c,lambda z:(z.pc,z.sp)==(STOP,232),visit)
    return c


def configure(bundle,owner=29,mode=0,alts=0,world=0,level=0,area=0x25):
    saved = N.Bus
    N.Bus = IRQ.Q.DispatchBus
    try:
        m = N.fresh(bundle)
    finally:
        N.Bus = saved
    N.put(m,SelectedCharacter=owner,WorldNumber=world,LevelNumber=level,AreaPointer=area,
          CrossoverBehaviorVersion=mode,FmGroups=alts,GameEngineSubroutine=8,TimerControl=0,
          OperMode=1,OperMode_Task=3,GamePauseStatus=0,NmiDisable=255)
    N.invoke(m,'GetAreaDataAddrs')
    m.raw_page(1,154)
    N.put(m,CurrentBank=154)
    direct(m,LOAD)
    assert m[0x7382] == 1 and m[0x7384] == area and m[0x7386] == mode
    return m


def slots(m):
    return tuple(tuple(N.get(m,name,i) for name in ACTOR_FIELDS) for i in range(6))


def occupancy(m,count,free=None):
    for i in range(6):
        fields = (int(i<count and i!=free),6,0,44+i,0,184,1,3,255)
        for name,value in zip(ACTOR_FIELDS,fields,strict=True):
            m[P.address(m.bundle,name)+i] = value


def scan(m,camera,timer=0,engine=8):
    geometry(m,camera,camera+112)
    N.put(m,GameEngineSubroutine=engine,TimerControl=timer)
    hits = Counter()
    c = direct(m,TICK,lambda z:hits.update(((tags(z),z.pc),)))
    assert c.memory.rawtags[1] == 154
    return hits[CTOR]


def signed(value):
    return ((value+32768)&65535)-32768


def margin(old,new):
    seeds = [configure(b) for b in (old,new)]
    counts = Counter()
    distances = (-32768,-513,-257,*range(-57,301),511,512,32767)
    for width,mode,camera,relative in product((2,4,6),(0,1),(0,0xff,0x456,0xfffe),distances):
        flags = []
        for m in seeds:
            geometry(m,camera,0)
            center = (camera+relative)&65535
            m[0x7396],m[0x7399],m[0x73b4],m[0x7386] = center&255,center>>8,width,mode
            c = direct(m,MARGIN)
            assert c.x == 0 and c.y == 17 and m[0x73d6] == (relative&255)
            flags.append((c.a,bool(c.p&1)))
        valid = (-48 if mode else -55) <= signed(relative) <= (288 if mode else 295)
        birth = valid and relative-width*4>=256
        assert flags[0][0] == flags[1][0] == int(valid) and flags[1][1] == birth,(width,mode,camera,relative,flags)
        counts[width*8,mode,birth] += 1
    return [[*key,count] for key,count in sorted(counts.items())]


def foreground(before,after):
    bundles = [P.bundle(raw) for raw in (before,after)]
    stats = Counter()
    # Both modes and all six WWF alternates retain the same record and native
    # constructor, and every potential native free-slot index is exercised.
    for mode,alts in product((0,1),range(6)):
        seeds = [configure(b,mode=mode,alts=alts) for b in bundles]
        assert all(bytes(m[0x7387:0x7388]) == b'\x01' and m[0x738a] == 34 for m in seeds)
        first = 1105+7*mode
        for camera in (first-1,first,1120,1121):
            for free in (0,1,2,3,4,5,None):
                m,n = [slim_fork(seed) for seed in seeds]
                for q in (m,n):
                    occupancy(q,6,free)
                unchanged = slots(n)
                got = [scan(q,camera) for q in (m,n)]
                old_birth = free is not None and camera>=first
                birth = old_birth and camera<=1120
                assert got == [int(old_birth),int(birth)],(mode,alts,camera,free,got)
                if birth:
                    assert slots(n)[free] == (1,0x28,0x40,0x60,5,208,1,6,255)
                assert all(row==unchanged[i] for i,row in enumerate(slots(n)) if not birth or i!=free)
                if old_birth==birth:
                    assert memory(m)==memory(n),(mode,alts,camera,free)
                stats['WWF',bool(birth)] += 1

    # Full throughout the offscreen window then a late free slot. This is a
    # finite allocation negative, without claiming six actors here naturally.
    pressure = [configure(b) for b in bundles]
    for m in pressure:
        occupancy(m,6)
    for camera in range(1105,1121):
        assert [scan(m,camera) for m in pressure] == [0,0]
    for m in pressure:
        m[0x15] = 0
    assert [scan(m,1121) for m in pressure] == [1,0]

    ordinary = [configure(b) for b in bundles]
    for m in ordinary:
        occupancy(m,0)
        assert scan(m,1105)==1
    for camera in (1120,1121,1264,1455,1456):
        for timer,engine in ((0,8),(0xef,10),(1,8),(255,9),(1,11),(1,12)):
            m,n = [slim_fork(seed) for seed in ordinary]
            assert scan(m,camera,timer,engine)==scan(n,camera,timer,engine)==0
            if timer and engine==10:
                assert slots(m)==slots(n) and bytes(m[0x7382:0x73d4])==bytes(n[0x7382:0x73d4])
            else:
                assert memory(m)==memory(n),(camera,timer,engine)
            stats['attached',timer!=0] += 1

    for engine,timer in product(range(16),(1,0xc8,0xc9,0xef,0xf0,255)):
        m,n = [configure(b) for b in bundles]
        assert [scan(q,1112,timer,engine) for q in (m,n)]==[0,int(engine==10)]
        if engine!=10:
            assert memory(m)==memory(n)
        stats['frozen_missing',engine==10] += 1

    # Existing actual mixed vertical/horizontal record selection remains live.
    for m in [configure(b,owner=1,world=1,level=1,area=1) for b in bundles]:
        assert m[0x7387]==2
        assert scan(m,1873)==1 and slots(m)[5][1]==0x28
        assert scan(m,2273)==1 and slots(m)[5][0]==0 and slots(m)[4][1]==0x25
    stats['natural_capacity_unproved',True] = 1
    return dict(counts=[[name,flag,n] for (name,flag),n in sorted(stats.items())],
                margin=margin(*bundles),late_full_pool_control={'old_birth':True,'new_birth':False,'camera':1121})


def engine_setup(bundle,camera,full=False):
    m = configure(bundle)
    geometry(m,camera,camera+112)
    N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,AreaParserTaskNum=7,ScrollThirtyTwo=0,
          GameEngineSubroutine=10,TimerControl=0xef,PlayerStatus=0,PlayerSize=1,
          Player_Y_Position=176,Player_Y_HighPos=1,Player_State=1,Player_X_Speed=0x10,
          Player_XSpeedAbsolute=0x10,Player_X_MoveForce=0,Player_Pos_ForScroll=112,
          Player_Rel_XPos=112,Player_CollisionBits=255,Player_MovingDir=1,PlayerFacingDir=1,
          SavedJoypadBits=1,SavedJoypad1Bits=1,NumberofLives=2,GuestAudioCharacter=0)
    for name in ('Block_Buffer_1','Block_Buffer_2'):
        a = P.address(bundle,name)
        m[a:a+208] = bytes(176)+bytes([0x54])*32
    occupancy(m,6 if full else 0)
    m.raw_page(1,128)
    N.put(m,CurrentBank=128)
    return m


def core(m,visit=None):
    c = cpu_at(m,0x839a,250,0x21)
    run(c,lambda z:(z.pc,z.sp)==(STOP,250),visit)
    return c


def vectors(before,after):
    old,new = [P.bundle(raw) for raw in (before,after)]
    counts,minima,deepest = Counter(),[255,255],{}
    lag,normal = lag_pcs(engine_setup(new,1104))

    def vector(c,kind,record):
        m = c.memory
        saved = (live(c),bytes(m[HP]))
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()

        def observe(z):
            minima[1] = min(minima[1],z.sp)
            key = tags(z),z.pc,tuple(z.memory.rawtags)
            if record and kind=='FF' and not z.p&4 and (key not in deepest or z.sp<deepest[key].sp):
                deepest[key] = fork(z)
                deepest[key].memory.vector_floor = None

        cycles = IRQ.interrupt(c,kind,lag,normal,observe)
        actual = live(c)
        # IRQ.interrupt checked the exact pending-map store pairs if an NMI
        # legitimately published a just-written mapper shadow at this cut.
        assert actual[:1]+actual[4:] == saved[0][:1]+saved[0][4:]
        assert bytes(m[HP]) == saved[1]
        return cycles, memory(m), IRQ.hardware(c)

    def pair(c,kind,label,record=True):
        a,b = fork(c,old),fork(c)
        assert vector(a,kind,False)==vector(b,kind,record),(label,kind,hex(c.pc),tags(c))
        counts[label,kind] += 1
        return b

    scenarios = []
    for label,camera,full,want in (('before_window',1102,False,False),('injury_birth',1104,False,True),
                                   ('injury_last',1119,False,True),('too_late',1120,False,False),
                                   ('six_native_slots',1104,True,False)):
        seen,resume,events = set(),[],[]

        def visit(c):
            tag,pc = tags(c),c.pc
            if (tag,pc) in ((129,0xa9d4),(154,TICK),CTOR,(128,0xa260)):
                events.append((tag,pc,N.get(c.memory,'ScreenLeft_X_Pos')+256*N.get(c.memory,'ScreenLeft_PageLoc')))
            watched = tag==154 and 0xad0b<=pc<0xae40 or tag==154 and 0xb31a<=pc<0xb32a
            key = tag,pc,c.sp,c.p&4
            if not watched or key in seen:
                return
            seen.add(key)
            minima[0] = min(minima[0],c.sp)
            for kind in ('FF','IRQ') if not c.p&4 else ('FF',):
                resume.append(pair(c,kind,label))

        c = core(engine_setup(new,camera,full),visit)
        first = [i for i,event in enumerate(events) if event[:2]==CTOR]
        assert bool(first)==want,(label,events)
        reached = [event for event in events if event[:2]==(154,TICK)]
        assert len(reached)==1 and events[0][:2]==(129,0xa9d4) and reached[0][2]==camera+1,(label,events)
        if first:
            assert first[0]==2 and events[first[0]+1][:2]==(128,0xa260)
            assert 256<=1376-events[first[0]][2]<=271
        for z in resume:
            run(z,lambda q:(q.pc,q.sp)==(STOP,250))
            # The FF handler legitimately advances its own audio bookkeeping.
            assert final(z)==final(c),(label,z.processorCycles)
        scenarios.append(dict(name=label,camera_before=camera,camera_after=reached[0][2],
                              native_constructor=bool(first),interrupt_cuts=len(seen)))

    for c in deepest.values():
        pair(c,'IRQ','nested',False)
    assert deepest and min(minima)>0x7a
    return dict(actual_GameCore=scenarios,cuts=[[name,kind,n] for (name,kind),n in sorted(counts.items())],
                minimum_SP=minima,actual_FF=lag)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    target = out/'proof.json'
    assert not target.exists()
    before = BASE.read_bytes()
    assert P.sha(before)==PIN
    after, rows = link(before,out)
    front = foreground(before,after)
    print('Exact native helper boundaries, capacity negative and active actor controls passed.',flush=True)
    irqs = vectors(before,after)
    refs = (Path(__file__),SOURCE,BASE,PACKED,FOOTER,R/'src/game.s',R/'src/object.s',R/'src/reset.s',
            R/'tools/reference/helper_camera_admission_1110_v1.s')
    report = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                  patches=rows,foreground=front,vectors=irqs,native_required=True,
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(target,report['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
