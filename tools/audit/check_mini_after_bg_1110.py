"""Source-bind the raw-41 no-op in the actual native post-terrain router."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import check_mini_lift_seen_fast_1110 as Lift
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_lift_admission_async_1108_v1 import tags
from check_mini_visibility_dispatch_1110_v1 import memory


A,L,M,N,R = Lift.A,Lift.L,Lift.M,Lift.N,Lift.R
BASE,PIN = Lift.BASE,Lift.PIN
SOURCE = R/'tools/reference/mini_after_bg_1110_v1.s'
FUNDING = R/'tools/reference/thomas_hot_render_1031_v3.s'
FIRE = R/'tools/reference/mini_mario_empty_draw.s'
ROUTE = bytes.fromhex('0848ad0260c922f035c90ad01dade55f2944c940d01468288d6a01'
                      'a9518d6c01a9b48d6d01a9d54c5a0168288d6a01a99e8d6c01a9bb'
                      '8d6d01a9cf4c5a0168288d6a01a96c8d6c01a9b48d6d01a99d4c5a01')
FIRE_PREFIX = bytes.fromhex('a9c78d4c01a9838de5734c7ab5')
CALL,RETURN = 0xa173,0xa176
ENTRY,HELPER = 0xb438,0xb497


def offset(bank,pc):
    return 16+8192*bank+(pc&8191)


def build(out):
    parent = BASE.read_bytes()
    assert M.sha(parent)==PIN
    b = M.bundle(parent)
    at = lambda bank,pc,n:parent[offset(bank,pc):offset(bank,pc)+n]
    for label,pc in (('HotPlayerGraphics',0xb3c2),('ThPostNativeHot',ENTRY),
                     ('HotNewCharacterDraw',0xb4a4),('MegaMan202AfterBG',RETURN),
                     ('RyuSourceBodyAfterBGBridge',0xe5cc),('CrossoverBehaviorVersion',0x7fe1),
                     ('FmAlts',0x5fe5)):
        assert M.address(b,label)==pc,label
    assert '.res 226-(*-::Name),$ff' in FUNDING.read_text()
    assert '.segment "GFX_FIREBALL"' in FIRE.read_text()
    assert 0xb3c2+226==0xb4a4 and len(ROUTE)==82 and at(66,ENTRY,82)==ROUTE
    assert at(66,0xb48a,26)==FIRE_PREFIX+b'\xff'*13 and HELPER==0xb48a+len(FIRE_PREFIX)
    assert at(1,CALL,3)==bytes.fromhex('20cce5')
    assert at(127,0xe5e9,15)==bytes.fromhex('a9388d6c01a9b48d6d01a9c24c5a01')
    assert at(1,0xa000,9)==bytes.fromhex('8d6201ad450148a942')
    # Public reader is the original entry. All moved branches are internal;
    # the existing fire leaf ends in JMP and the next public entry stays fixed.
    prg = parent[16:16+128*8192]
    bank = at(66,0xa000,8192)
    targets = (0xb44e,0xb462,0xb476,*range(HELPER,0xb4a4))
    for target in targets:
        lo,hi = target&255,target>>8
        assert all(bytes((op,lo,hi)) not in bank for op in (0x20,0x4c)),hex(target)
        assert bytes((0xa9,lo,0x8d,0x6c,1,0xa9,hi,0x8d,0x6d,1,0xa9,0xc2)) not in prg,hex(target)
    cfg,obj,binary = (out/f'after-bg.{ext}' for ext in ('cfg','o','bin'))
    cfg.write_text('MEMORY { ROUTE:start=$B438,size=$6C,file=%O; }\n'
                   'SEGMENTS { DISPATCH:load=ROUTE,type=ro; }\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
    obj.unlink()
    code = binary.read_bytes()
    assert len(code)==108 and code[82:95]==bytes(13)
    assert code[95:]==bytes.fromhex('28ade17ff00338a9298d790160')
    rows = [dict(file_offset=offset(66,pc),physical_PRG=66,CPU_half_open=[pc,pc+len(old)],
                 old_hex=old.hex(),new_hex=new.hex(),role=role)
            for pc,old,new,role in ((ENTRY,ROUTE,code[:82],'existing complete post-terrain router'),
                                    (HELPER,b'\xff'*13,code[95:],'remaining named HotPlayerGraphics tail'))]
    return parent,install(parent,rows),rows


def cpu_at(m,a,x,y,p):
    m[0x5115] = 129
    N.put(m,CurrentBank=129)
    m.writes.clear()
    m.ram_writes.clear()
    c = N.NesMPU(memory=m,pc=CALL)
    c.a,c.x,c.y,c.p,c.sp = a,x,y,p,232
    return c


def stop(c):
    return (c.pc,c.sp)==(RETURN,232)


def check_return(a,b,owner):
    m,n = a.memory,b.memory
    assert registers(a)==registers(b) and live_stack(a)==live_stack(b)
    A.P.compare_memory(m,n)
    assert memory(m)==memory(n) and m.ram_writes==n.ram_writes
    def writes(bus,excluded):
        return [(k,v) for k,v in bus.writes if k not in excluded and not 0x17b<=k<=0x100+a.sp]
    if owner==41:
        assert [v for addr,v in m.writes if addr==0x5115]==[0xc2,0xcf,0xc2,129]
        assert [v for addr,v in n.writes if addr==0x5115]==[0xc2,129]
        assert writes(m,{0x145,0x179,0x5115})==writes(n,{0x145,0x179,0x5115})
    else:
        assert writes(m,())==writes(n,())


def cold_owner(b,owner,variant):
    m = N.fresh(b)
    N.put(m,SelectedCharacter=owner,FmAlts=variant,OperMode=1,FamilyMainCommit=1,
          DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,NumberofLives=2)
    N.invoke(m,'InitScreen')
    N.put(m,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,
          Player_Y_Position=144,Player_Y_HighPos=1,Player_State=0,Player_X_Position=80,
          Player_PageLoc=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=1,SavedJoypadBits=0,
          DisableScreenFlag=0,Mirror_PPUMASK=30,AreaPointer=0x25)
    N.invoke(m,'GetAreaDataAddrs')
    if owner==10:
        # The scene loader publishes both headers. The real motion ingress
        # then invokes the original actor constructor when engine 8 begins.
        assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==167
        N.invoke(m,'ThMovementIngress',x=0,y=0)
    ready = 'ThReady' if owner==10 else 'KrReady'
    assert m.ram[2][M.address(b,ready)&8191]==167,(owner,ready)
    return m


def foreground(before,after):
    bundles = L.bundles(before,after)
    seeds = [N.fresh(b) for b in bundles]
    counts = Counter()

    def case(seeds,owner,version,flags,engine,variant,value,active=None):
        pair = []
        for i,seed in enumerate(seeds):
            m = slim_fork(seed)
            N.put(m,SelectedCharacter=owner,CrossoverBehaviorVersion=version,FmAlts=variant,
                  GameEngineSubroutine=engine,Player_State=0)
            c = cpu_at(m,value,3,151,flags)
            hits = []
            if active is not None:
                target = M.address(m.bundle,active)
            def observe(z):
                if active is not None and tags(z)==3 and z.pc==target:
                    hits.append(z.pc)
            run(c,stop,observe)
            assert active is None or hits==[target],(owner,active,i,hits)
            pair.append(c)
        try:
            check_return(*pair,owner)
        except AssertionError as error:
            raise AssertionError((owner,version,flags,engine,variant,value,
                                  [registers(c) for c in pair])) from error
        if owner==41:
            z = pair[1]
            expected = 41 if version else 0
            assert z.a==z.memory[0x179]==expected and z.p&1==int(bool(version or flags&1))
            assert [z.memory[i] for i in (0x162,0x16a,0x16c,0x16d)]==[0xcf,value,0x9e,0xbb]
        counts['Mini' if owner==41 else active or 'foreign',pair[0].processorCycles-pair[1].processorCycles] += 1

    for owner,version,flags,engine in product((*range(42),42,127,255),(0,1,128),
                                               (0x20,0x21,0x61,0xe4),(7,8,11)):
        case(seeds,owner,version,flags,engine,0,(owner+flags)&255)
    for owner,active,variant in ((10,'ThPostTerrain',0x40),(34,'KrPostTerrain',1)):
        warm = [cold_owner(b,owner,variant) for b in bundles]
        for flags,version,value in product((0x20,0x21,0x61,0xe4),(0,1),(0,167,255)):
            case(warm,owner,version,flags,8,variant,value,active)
    return [[key[0],key[1],n] for key,n in sorted(counts.items())]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    before,after,rows = build(out)
    print('Exact linked after-terrain candidate',M.sha(after),flush=True)
    callbacks = foreground(before,after)
    print('Actual post-terrain native callback pairs',callbacks,flush=True)
    core = A.P.check_full_cpu(before,after,{})
    loop = Lift.Edges.Composed.whole_loop(before,after,{})
    refs = (Path(__file__),SOURCE,FUNDING,FIRE,BASE,R/'src/player.s',R/'src/mmc5.s',
            R/'tools/audit/freeze_mini_fireball_integration_1103.py',out/'after-bg.bin')
    proof = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),ROM_written=False,
                 patches=rows,actual_native_call=[CALL,RETURN],callbacks=callbacks,whole_GameCore=core,
                 whole_GameLoop=loop,bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(M.sha(after),json.dumps(dict(whole_GameCore=core,whole_GameLoop=loop)),flush=True)


if __name__=='__main__':
    main()
