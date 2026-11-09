"""Source-linked platform dispatch differential on the exact six-actor base."""

from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import profile_mini_busy_1108_v1 as P
from check_mini_funded_actor_1108_v3 import install,live_stack,registers,run,set_actor,slim_fork
from check_mini_visibility_dispatch_1110_v1 import memory
from check_mini_lift_retention_1110_v1 import camera,setup_main,spawn

R,N = P.R,P.N
BASE = R/'build/mini-sweep-seam-native-1110/candidate.nes'
TRACE = R/'build/mini-retained-peak-1110/capture/instruction-sample.json'
PIN = 'ddd6e71b42aaed99645a54b64b766b4fb3a32aee5c3b55bfe9b7c552000c94b3'
OUT = R/'build/native-platform-dispatch-1110'
SOURCE = R/'tools/reference/native_platform_collision_dispatch_1110_v1.s'
POLICY, BRIDGE, ACTOR = 0xb707,0xb98e,0xb436
OLD_BRIDGE = bytes.fromhex(
    '8d6a01a95c8d6c01a9bf8d6d01a9ba205a01'
    '2053b408488d6a01a9838d6c01a9bf8d6d01a9ba205a01682860')
PROFILE = ('RyuSourceBodyPlatformPrepare','RyuSourceBodyPlatformFinish','Z2LegacyPlatformPrepare',
           'Z2LegacyPlatformFinish','RyuSourceBodyPlatformBasic')


def file_pc(pc):
    return 16+(pc&8191)


def binding(raw):
    bank = raw[16:16+8192]
    assert bank[BRIDGE&8191:(BRIDGE+44)&8191]==OLD_BRIDGE
    assert bank[(POLICY-4)&8191:(POLICY+11)&8191]==bytes.fromhex('205a0160')+b'\xea'*11
    assert bank[0x143f:0x1447]==bytes.fromhex('208eb9ad4a07d003')
    assert bank.count(bytes.fromhex('208eb9'))==1
    b = P.bundle(raw)
    assert P.address(b,'RunLargePlatform')==ACTOR
    assert P.address(b,'RyuSourceBodyLargePlatformBridge')==BRIDGE
    assert P.address(b,'PositionPlayerOnVPlat')+21==POLICY
    prg = raw[16:1048592]
    for pc in range(POLICY,POLICY+11):
        assert all(bytes((op,pc&255,pc>>8)) not in bank for op in (0x20,0x4c))
        assert bytes.fromhex(f'a9{pc&255:02x}8d6c01a9{pc>>8:02x}8d6d01a980') not in prg
    for n in PROFILE:
        assert (P.location(b,n)-16)//8192==58
    cfg,obj,binary = (OUT/f'platform.{ext}' for ext in ('cfg','o','bin'))
    cfg.write_text('MEMORY{P:start=$B707,size=$0B,file=%O;D:start=$B98E,size=$2C,file=%O;}\n'
                   'SEGMENTS{POLICY:load=P,type=ro;DISPATCH:load=D,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
    obj.unlink()
    new = binary.read_bytes()
    assert len(new)==55
    rows = [dict(file_offset=file_pc(pc),physical_PRG=0,CPU_half_open=[pc,pc+len(old)],
                 old_hex=old.hex(),new_hex=after.hex(),role=role)
            for pc,old,after,role in ((POLICY,b'\xea'*11,new[:11],'source-declared platform tail'),
                                       (BRIDGE,OLD_BRIDGE,new[11:],'existing platform collision ingress'))]
    return install(raw,rows),rows


def point(c):
    pc = c.pc
    return (c.memory.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1,pc)


def actor_setup(seed,raw,variant,actor,tag,location,timer,p):
    m = slim_fork(seed)
    x,y,state = {'contact':(110,184,0),'distant':(170,172,0),'leftclip':(4,64,0),
                 'cull':(32,187,0),'suspended':(108,191,128)}[location]
    camera_left = 160 if location=='cull' else 18 if location=='leftclip' else 0
    set_actor(m,slot=5,enemy=actor,x=x,y=y,state=state|tag)
    N.put(m,SelectedCharacter=raw,Z2Variant=variant,RyuSourceBodyProfile=25,TimerControl=timer,
          ScreenLeft_X_Pos=camera_left,ScreenRight_X_Pos=(camera_left+255)&255,
          ScreenRight_PageLoc=(camera_left+255)>>8, Player_X_Position=113,Player_PageLoc=0,
          Player_Y_Position=160,Player_Y_HighPos=1,Player_Y_Speed=4,Player_State=2,
          Player_OffscreenBits=0)
    addr = P.address(m.bundle,'BoundingBox_UL_Corner')
    m[addr:addr+4] = bytes((109,174,122,188))
    at = P.address(m.bundle,'Enemy_BoundBoxCtrl')+5
    m[at] = 5 if tag==0x40 else 6
    m.raw_page(1,128)
    N.put(m,CurrentBank=128,NmiDisable=255)
    c = N.NesMPU(memory=m,pc=ACTOR)
    c.a,c.x,c.y,c.p,c.sp = 0x91,5,71,p,224
    c.stPushWord(0x5aff)
    return c


def end(c):
    return (c.pc,c.sp)==(0x5b00,224)


def state(c):
    return registers(c,0xef),live_stack(c),memory(c.memory)


def actor_cases(images):
    seeds = [P.fixture(b,0,False,False) for b in images]
    savings = Counter()
    traces = Counter()
    scenes = ('contact','distant','leftclip','cull','suspended')
    cases = product(range(42),(0,1),(0x25,0x28),(0,0x40,0x60),scenes,(0,1),(0x20,0x65))
    for raw,variant,actor,tag,where,timer,p in cases:
        # Roster/variant contexts all hit contact/distant. Exact clipped,
        # cull and suspended traces need the collision owners and Mini only.
        if where not in ('contact','distant') and raw not in (0,4,10,11,41):
            continue
        cpus = [actor_setup(seed,raw,variant,actor,tag,where,timer,p) for seed in seeds]
        for side,c in enumerate(cpus):
            def observe(q):
                bank,pc = point(q)
                if bank==186 and pc in (0xbf5c,0xbf83):
                    traces[side,'source_body_wrapper'] += 1
                if bank==128 and pc==0xb453:
                    traces[side,'native_collision'] += 1
            run(c,end,observe)
        a,b = cpus
        left,right = state(a),state(b)
        assert left==right,(raw,variant,actor,tag,where,timer,p,left[:2],right[:2],
                            [i for i,(x,y) in enumerate(zip(left[2],right[2])) if x!=y],
                            [bytes(c.memory[0x15a:0x17b]).hex() for c in cpus])
        savings[raw>=11 and timer==0,a.processorCycles-b.processorCycles] += 1
    assert traces[0,'native_collision']==traces[1,'native_collision']
    assert traces[0,'source_body_wrapper']>traces[1,'source_body_wrapper']
    return dict(cases=sum(savings.values()),savings=[list(k)+[v] for k,v in sorted(savings.items())],
                entries=[[side,name,v] for (side,name),v in sorted(traces.items())])


def scene_seed(b,lifts,actors):
    b['segs']['platform_scan'] = dict(start=str(0xbbcf),ooffs=str(16+24*8192+0x1bcf))
    b['syms']['MiniLiftTick'] = dict(val=str(0xbbcf),seg='platform_scan')
    m = P.fixture(b,actors,False,False)
    if not lifts:
        return m
    setup_main(m,695,0,0,5)
    for index,right in enumerate((528,656,832)[:lifts]):
        spawn(m,right)
        assert m.ram[2][0x30c] == (1<<(index+1))-1
    camera(m,832)
    N.put(m,Player_Y_Position=160,Player_Y_HighPos=1,Player_State=0,
          AreaParserTaskNum=7,ScrollThirtyTwo=0)
    return m


def whole(images):
    checks = []
    for lifts,actors in ((0,0),(1,0),(2,2),(3,0),(3,3)):
        pair = [scene_seed(b,lifts,actors) for b in images]
        differences = []
        for i in range(16):
            for m in pair:
                key = 0 if i<8 else 192
                N.put(m,FrameCounter=(N.get(m,'FrameCounter')+1)&255,SavedJoypadBits=key,
                      SavedJoypad1Bits=key,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
            a,b = [N.invoke(m,'GameCoreRoutine',x=0,y=0) for m in pair]
            assert memory(pair[0])==memory(pair[1]),(lifts,actors,i,a,b)
            assert all(a[n]==b[n] for n in 'AXYP')
            differences.append(a['CPU']-b['CPU'])
        checks.append(dict(lifts=lifts,ordinary_actors=actors,updates=len(differences),
                           saved_cycles=[min(differences),max(differences)]))
    return checks


def sample():
    scene = json.loads(TRACE.read_text())
    f = scene['foreground_opcodes']
    bound = lambda bank,lo,hi:sum(v for k,v in f.items()
                                if k.startswith(f'{bank}:') and lo<=int(k.split(':')[1],16)<hi)
    assert f['0:b98e']==12 and f['58:bf5c']==f['58:bf83']==9
    return dict(scene=scene['scene'],platform_calls=3,
                transport_prepare_finish_exclusive=6*54,
                bank58_noop_wrapper_exclusive=bound(58,0xa000,0xc000),
                bank0_old_bridge_exclusive=bound(0,BRIDGE,BRIDGE+44))


def main():
    raw = BASE.read_bytes()
    assert P.sha(raw)==PIN
    OUT.mkdir(exist_ok=True)
    after,rows = binding(raw)
    images = [P.bundle(b) for b in (raw,after)]
    proof = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                 source_CPU_only=True,ROM_written=False,patches=rows,
                 native_profile=sample(),exact_linked_actor=actor_cases(images))
    print('Exact native platform cohort',proof['exact_linked_actor'],flush=True)
    proof['whole_GameCore'] = whole(images)
    paths = (Path(__file__),SOURCE,TRACE,R/'src/object.s',R/'src/sprite_render.s',
             R/'src/zelda2_link_platform.s',R/'src/ryu_source_body.s',R/'src/mmc5.s')
    proof['bindings'] = {p.relative_to(R).as_posix():P.sha(p.read_bytes()) for p in paths}
    (OUT/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(proof['expected_memory_only_SHA256'],proof['whole_GameCore'],flush=True)


if __name__=='__main__':
    main()
