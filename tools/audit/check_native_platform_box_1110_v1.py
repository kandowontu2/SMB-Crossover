"""Qualify same-bank native platform motion packets and clipped typed boxes."""

from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import check_native_platform_collision_dispatch_1110_v1 as D
from check_mini_funded_actor_1108_v3 import install,registers,run,slim_fork
from check_mini_visibility_dispatch_1110_v1 import memory

P,N,R = D.P,D.N,D.R
OUT = R/'build/native-platform-box-1110'
BASE = R/'build/mini-lane-audio-native-1110/candidate.nes'
PIN = 'a226894c4f6b97f1b9df248cf1465f1a36037fcc256d8ec703e05d0f077d6746'
TRACE = R/'build/mini-lane-peak-1110/capture/instruction-sample.json'
SOURCE = R/'tools/reference/native_platform_box_1110_v1.s'
MOTION, MOTION_END, GATE, COLD = 0xae6b,0xaeed,0xb057,0xb04b
OLD_ENTRIES = (0xae81,0xae93,0xaea5,0xaea5,0xaeb7,0xaec9,0xaedb)
TARGETS = (0xb49f,0xb642,0xb6be,0xb6be,0xb676,0xb6a0,0xb6ac)
OLD_BOX = bytes.fromhex('e8201a8bcac9fe90034c3b9f8a186901aaa001204e9fb51e2920f009'
                         'b95806186910995a06b95906186908995b064c909f')


def at(pc,bank=26):
    return 16+bank*8192+(pc&8191)


def ingress(raw):
    q = P.bundle(raw)
    assert P.address(q,'HpNativePlatformDispatch')==0xae40
    assert P.address(q,'HpNativePlatformBBoxCold')==COLD
    assert P.address(q,'BoundingBoxCore')==0x9f4e and P.address(q,'CheckRightScreenBBox')==0x9f90
    assert P.address(q,'RunLargePlatform')==D.ACTOR and P.address(q,'YMovingPlatform')==0xb642
    jump = bytes.fromhex('0a a8 68 85 07 68 85 08 c8 b1 07 85 09 c8 b1 07 85 0a 6c 09 00')
    assert raw[at(0x8a09,126):at(0x8a09,126)+len(jump)]==jump
    native_base = at(MOTION)
    assert raw[native_base:native_base+8]==bytes.fromhex('b51738e92420098a')
    table = b''.join(n.to_bytes(2,'little') for n in OLD_ENTRIES)
    assert raw[native_base+8:native_base+22]==table
    for old,target in zip(OLD_ENTRIES,TARGETS):
        packet = bytes.fromhex(f'8d6a01a9{target&255:02x}8d6c01a9{target>>8:02x}8d6d01a9804c5a01')
        assert raw[at(old):at(old)+len(packet)]==packet
    bbox_ctrl = P.location(q,'BoundBoxCtrlData')
    assert raw[bbox_ctrl+20:bbox_ctrl+28]==bytes([0,0,32,13,0,0,48,13])
    assert raw[at(COLD):at(COLD)+len(OLD_BOX)]==OLD_BOX
    call = bytes.fromhex('a9408d6c01a9ae8d6d01a99a205a01')
    prg = raw[16:1048592]
    assert prg.count(call)==1 and 16+prg.index(call)==at(0xb48c,0)
    assert raw[at(0xa2ef,0):at(0xa2fd,0)]==bytes.fromhex('36b4')*7, (
        'Seven real native object table entries')
    assert not any(raw[at(0xa000):at(0xbfff)].count(bytes((op,pc&255,pc>>8)))
                   for op,pc in product((0x20,0x4c),OLD_ENTRIES))


def bind(raw):
    ingress(raw)
    cfg,obj,bin,lbl = (OUT/f'platform-box.{s}' for s in ('cfg','o','bin','lbl'))
    cfg.write_text('MEMORY{M:start=$AE6B,size=$82,file=%O;G:start=$B057,size=5,file=%O;}\n'
                   'SEGMENTS{NATIVE_PLATFORM:load=M,type=ro;BOX_GATE:load=G,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',bin,'-Ln',lbl],check=True)
    obj.unlink()
    new = bin.read_bytes()
    labels = {l.split()[2][1:]:int(l.split()[1],16) for l in lbl.read_text().splitlines()}
    assert len(new)==0x87 and labels['TaggedPlatformBox']>MOTION
    rows = []
    for pc,data,role in ((MOTION,new[:0x82],'stock motion packet tables and tagged platform rectangle'),
                         (GATE,new[0x82:],'existing native box onscreen branch')):
        n = len(data)
        rows.append(dict(file_offset=at(pc),physical_PRG=26,CPU_half_open=[pc,pc+n],
                         old_hex=raw[at(pc):at(pc)+n].hex(),new_hex=data.hex(),role=role))
    return install(raw,rows),rows,labels


def cold_box(seed,slot,x,screen,y,ctrl,tag,p):
    m = slim_fork(seed)
    name = lambda n:P.address(m.bundle,n)
    for field,v in [('Enemy_X_Position',x&255),('Enemy_PageLoc',x>>8),('Enemy_BoundBoxCtrl',ctrl),
                    ('Enemy_State',tag)]:
        m[name(field)+slot] = v
    N.put(m,ObjectOffset=slot,ScreenLeft_X_Pos=screen&255,ScreenLeft_PageLoc=screen>>8,
          ScreenRight_X_Pos=(screen+255)&255,ScreenRight_PageLoc=(screen+255)>>8,
          Enemy_Rel_XPos=(x-screen)&255,Enemy_Rel_YPos=y)
    for i in range(3,11):
        m[i] = 0x81+i
    m.raw_page(1,154)
    N.put(m,CurrentBank=154)
    c = N.NesMPU(memory=m,pc=COLD)
    c.a,c.x,c.y,c.p,c.sp = 0x87,slot,69,p,224
    c.stPushWord(0x5aff)
    return c


def box_cases(images):
    seeds = [P.fixture(b,0,False,False) for b in images]
    savings = Counter()
    for slot,screen,relative,y,ctrl,tag,p in product((0,5),(0x132,0x1f8),
          (-70,-17,-1,0,8,113,125,128,215,253,255,256,287),
          (32,184,253),(4,5,6,7,20),(0x40,0x60),(0x20,0x65)):
        cpus = [cold_box(seed,slot,screen+relative,screen,y,ctrl,tag,p) for seed in seeds]
        for c in cpus:
            run(c,D.end)
        a,b = cpus
        assert D.state(a)==D.state(b),(slot,screen,relative,y,ctrl,tag,p,registers(a),registers(b))
        savings[ctrl,tag,a.processorCycles-b.processorCycles] += 1
    return dict(cases=sum(savings.values()),savings=[list(k)+[n] for k,n in sorted(savings.items())])


def set_named(m,n,i,v):
    m[P.address(m.bundle,n)+i] = v


def motion_cases(images):
    seeds = [P.fixture(b,0,False,False) for b in images]
    result = Counter()
    for who,actor,scene,timer,tag,p in product((0,4,10,41),range(0x24,0x2b),
          ('contact','distant','leftclip','cull'),(0,1),(0,0x40,0x60),(0x20,0x65)):
        if actor==0x24 and tag:
            continue
        cpus = [D.actor_setup(s,who,int(who==4),actor,tag,scene,timer,p) for s in seeds]
        for c in cpus:
            m = c.memory
            if actor==0x24:
                for n,i,v in [('Enemy_State',5,4),('Enemy_Flag',4,1),('Enemy_ID',4,0x24),
                              ('Enemy_State',4,5),('Enemy_X_Position',4,80),
                              ('Enemy_PageLoc',4,0),('Enemy_Y_Position',4,160),
                              ('Enemy_Y_HighPos',4,1),('Enemy_BoundBoxCtrl',4,6),
                              ('PlatformCollisionFlag',4,255)]:
                    set_named(m,n,i,v)
            run(c,D.end)
        a,b = cpus
        old,new = D.state(a),D.state(b)
        assert old==new,(who,actor,scene,timer,tag,p,old[:2],new[:2],
                         [i for i,(x,y) in enumerate(zip(old[2],new[2])) if x!=y])
        result[actor,timer,a.processorCycles-b.processorCycles] += 1
    # Managed helper ownership hits the genuine HpFindActor/HpMotionTick
    # branch, which still returns through its original dispatcher.
    managed = 0
    for actor,timer in product((0x25,0x28),(0,1)):
        cpus = [D.actor_setup(s,29,0,actor,0x40,'contact',timer,0x20) for s in seeds]
        calls = []
        for c in cpus:
            m = c.memory
            for n,i,v in [('HpActorOwner',5,1),('HpActorSlot',0,6),('HpWidth',0,32),
                          ('HpVisible',0,1),('HpKind',0,int(actor==0x25)),('HpCount',0,1),
                          ('HpXLo',0,126),('HpXHi',0,0),('HpY',0,184)]:
                set_named(m,n,i,v)
            count = []
            run(c,D.end,lambda z:count.append(z.pc) if D.point(z)==(154,0xaeed) else None)
            calls.append(len(count))
        assert D.state(cpus[0])==D.state(cpus[1])
        assert calls==[int(timer==0)]*2,(actor,timer,calls)
        managed += 1
    return dict(cases=sum(result.values()),managed_platform_cases=managed,
                savings=[list(k)+[n] for k,n in sorted(result.items())])


def sample(raw):
    trace = json.loads(TRACE.read_text())
    fg = trace['foreground_opcodes']
    assert fg['26:b04b']==6 and fg['26:b05e']==12
    return dict(scene=trace['scene'],tagged_native_box_calls=3,onscreen_box_calls=2,
                stock_motion_calls=3,profile_sha256=P.sha(TRACE.read_bytes()),ROM_SHA256=P.sha(raw))


def main():
    raw = BASE.read_bytes()
    assert P.sha(raw)==PIN
    OUT.mkdir(exist_ok=True)
    after,rows,labels = bind(raw)
    images = [P.bundle(b) for b in (raw,after)]
    q = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
             source_CPU_only=True,ROM_written=False,patches=rows,labels=labels,
             native_peak=sample(raw),native_box=box_cases(images))
    print('Native box',q['native_box'],flush=True)
    q['stock_and_managed_motion'] = motion_cases(images)
    q['whole_GameCore'] = D.whole(images)
    refs = (Path(__file__),SOURCE,TRACE,R/'src/crossover_helpers.s',R/'src/native_platform16.s',
            R/'src/collision.s',R/'src/common.s',R/'src/object.s',Path(D.__file__))
    q['bindings'] = {p.relative_to(R).as_posix():P.sha(p.read_bytes()) for p in refs}
    (OUT/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(q['expected_memory_only_SHA256'],q['stock_and_managed_motion'],q['whole_GameCore'],flush=True)


if __name__=='__main__':
    main()
