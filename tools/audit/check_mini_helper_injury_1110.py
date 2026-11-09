"""Qualify strict offscreen Mini lift admission during native injury movement."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_helper_activation_1110 as H
import prepare_mini_helper_activation_native_1110 as Strict
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_lift_admission_async_1108_v1 import tags
from check_mini_visibility_dispatch_1110_v1 import memory


A,L,M,N,R = H.A,H.L,H.M,H.N,H.R
SOURCE = R/'tools/reference/mini_helper_injury_1110.s'
SPANS = (
    ('POWER_DUP',1,0xa45c,19,bytes.fromhex('8d6a01a9278d6c01a9ad8d6d01a9fc205a0160')),
    ('INJURY_JUMP',1,0xa47d,3,bytes.fromhex('4cc3a0')),
    ('SAMUS_DUP',1,0xb7ac,19,bytes.fromhex('8d6a01a9d08d6c01a9a08d6d01a9d2205a0160')),
    ('INJURY_SAVE_C',84,0xb3dd,7,bytes.fromhex('68a868aa682860')),
    ('INJURY_AUTH',84,0xb4ae,31,b'\xea'*31),
    ('INJURY_SCAN',84,0xb5f0,16,bytes.fromhex('bd01019d0501e888d0f69a4cddb3ffff')),
)
WRAPPER_RETURN, CONTROL, INJURY = 0xa46c,0xa0c3,0xa46f
STOP = 0x5b00


def build(before,out):
    assert M.sha(before)==Strict.TARGET
    def raw(bank,pc,length):
        at = H.offset(bank,pc)
        return before[at:at+length]
    for (_,bank,pc,length,old),duplicate in zip(SPANS[:3:2],(0xa51c,0xa650),strict=True):
        assert raw(bank,pc,length)==raw(bank,duplicate,length)==old
    assert raw(1,INJURY,24)==bytes.fromhex('ad4a07c9f0b00ac9c8d0034c08a54cc3a0d018ad0260d013')
    assert raw(84,0xb49f,15)==bytes.fromhex('8d620128205d016820c280ad790160')
    assert raw(126,0x80c2,7)==bytes.fromhex('8da17d8d165160')
    with tempfile.TemporaryDirectory(prefix='link-',dir=out) as name:
        work = Path(name)
        cfg,obj,binary = (work/f'injury.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { '+''.join(f'{n}:start=${pc:04x},size={size},file=%O;'
                         for n,_,pc,size,_ in SPANS)+'}\nSEGMENTS { '+
                       ''.join(f'{n}:load={n},type=ro;' for n,*_ in SPANS)+'}\n',encoding='utf-8')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        linked = binary.read_bytes()
    patches,pos = [],0
    for role,bank,pc,length,old in SPANS:
        assert raw(bank,pc,length)==old and len(old)==length,(role,pc)
        data = linked[pos:pos+length]
        assert len(data)==length
        patches.append(dict(L.patch(before,H.offset(bank,pc),data,role),physical_PRG=bank,
                            CPU_half_open=[pc,pc+length]))
        pos += length
    assert len(linked)==pos
    return install(before,patches),patches


def setup(seed,right,timer,owner=41,held=1,seen=0,full=False,state=1,engine=10):
    m = slim_fork(seed)
    x = right-143
    L.setup_main(m,x,seen,0,5)
    L.camera(m,right)
    N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,TimerControl=timer,
          Player_Y_Position=176,Player_Y_HighPos=1,Player_State=state,PlayerStatus=0,
          Player_X_Speed=0x10,Player_XSpeedAbsolute=0x10,Player_X_MoveForce=0,
          Player_Pos_ForScroll=112,Player_Rel_XPos=112,Player_CollisionBits=255,
          Player_MovingDir=1,PlayerFacingDir=1,SavedJoypadBits=held,SavedJoypad1Bits=held,
          NmiDisable=255)
    m.ram[2][0x300] = 2
    for slot in range(6):
        m[0x10+slot] = int(full)
        m[0x17+slot] = 6
    return m


def camera_right(m):
    return N.get(m,'ScreenRight_X_Pos')+256*N.get(m,'ScreenRight_PageLoc')


def native_at(m,pc,p=0x31):
    m.raw_page(1,129)
    N.put(m,CurrentBank=129)
    cpu = N.NesMPU(memory=m,pc=pc)
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp = 53,0,29,p,248
    cpu.stPushWord(STOP-1)
    return cpu


def drive(seed,right,timer,*,owner=41,held=1,seen=0,full=False,state=1,engine=10,pc=INJURY,p=0x31,
          poison=None):
    m = setup(seed,right,timer,owner,held,seen,full,state,engine)
    c = native_at(m,pc,p)
    points,post = Counter(),None

    def visit(z):
        nonlocal post
        point = tags(z),z.pc
        points[point] += 1
        if point==(129,WRAPPER_RETURN):
            post = (registers(z),memory(m))
        if point==(212,0xb3dd) and poison is not None:
            at,value = poison
            m.ram[2][at] = value

    run(c,lambda z:(z.pc,z.sp)==(STOP,248),visit)
    return c,m,points,post


def foreground(before,after):
    old,new = L.bundles(before,after)
    seeds = [L.fixture(b,0,False,False) for b in (old,new)]
    stats, samples = Counter(),{}
    for index,(minimum,left) in enumerate(zip(H.MINIMA,H.LEFTS,strict=True)):
        prior = (1<<index)-1
        for right,timer,held,state,full in product(range(minimum-3,minimum+9),
                (0xf1,0xf0,0xef,0xe5,0xc9,0xc8),(0,1,0x41),(0,1),(False,True)):
            a,b = [drive(seed,right,timer,held=held,seen=prior,state=state,full=full) for seed in seeds]
            old_c,old_m,old_pts,_ = a
            _,new_m,new_pts,pre = b
            assert camera_right(old_m)==camera_right(new_m)
            reached = 0xc9<=timer<=0xef
            assert bool(old_pts[129,CONTROL])==bool(new_pts[129,CONTROL])==reached
            assert bool(new_pts[152,H.WORKER])==reached
            if reached:
                assert pre is not None and pre[0][:-1]==registers(old_c)[:-1] and pre[0][-1]==old_c.sp-2
                assert pre[1]==memory(old_m),(
                    index,right,timer,held,state,full,pre and pre[0],registers(old_c))
                assert 0<=camera_right(new_m)-right<=3
            else:
                assert pre is None and memory(old_m)==memory(new_m) and registers(a[0])==registers(b[0])
            birth = reached and not full and minimum<=camera_right(new_m)<minimum+8
            assert new_m.ram[2][0x30c]==prior|((1<<index) if birth else 0)
            assert old_m.ram[2][0x30c]==prior
            assert tuple(new_m.rawtags)==tuple(old_m.rawtags)
            if birth:
                slot = new_m.ram[2][0x30b]-1
                assert H.L.snapshot(new_m,slot)[:8]==(*H.LIFT_STATE,left&255,left>>8,192,1,5)
                relative = left-camera_right(new_m)+255
                assert 256<=relative<=263
                samples.setdefault(index,dict(before=right,after=camera_right(new_m),relative=relative,
                                              slot=slot,timer=timer))
            stats['native_injury_boundary',reached,birth] += 1
    assert set(samples)=={0,1,2}
    for owner,timer,p in product(range(41),(0xef,0xc9,0xc8,0xf0),(0x31,0x65)):
        a,b = [drive(seed,856,timer,owner=owner,p=p) for seed in seeds]
        assert b[3] is None and not b[2][212,0xb3dd]
        assert registers(a[0])==registers(b[0]) and memory(a[1])==memory(b[1]),(owner,timer,p)
        stats['foreign_injury',False,False] += 1
    for at,value in ((0x300,0),(0x300,1),(0x1fe0,0),(0x1fe1,40)):
        c,m,points,_ = drive(seeds[1],856,0xef,seen=3,poison=(at,value))
        assert points[212,0xb3dd]==1 and not points[152,H.WORKER]
        assert m.ram[2][0x30c]==3 and not any(m[0x10:0x16])
        assert tuple(m.rawtags)[2]==2 and N.get(m,'CurrentBankC')==2
        stats['C2_poison_rejected',False,False] += 1
    for pc,owner in ((0xa444,0),(0xa444,2),(0xa444,41),(0xa517,41),(0xa650,2),(0xb7ac,2)):
        a,b = [drive(seed,520,0xc4,owner=owner,pc=pc) for seed in seeds]
        assert registers(a[0])==registers(b[0]) and memory(a[1])==memory(b[1]),(hex(pc),owner)
        stats['duplicate_original',False,False] += 1
    return dict(cases=[[kind,move,birth,n] for (kind,move,birth),n in sorted(stats.items())],
                first_post_scroll_births=samples)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    published,before,strict = Strict.bound_image()
    final,patches = build(before,out)
    print('Linked exact injury ingress',M.sha(final),flush=True)
    fg = foreground(before,final)
    cold,_ = A.exact_cold(published,final,strict['exact_changed_code'])
    files = (Path(__file__),SOURCE,Strict.CPU,Strict.IRQ,Strict.KERNEL,
             H.BASE,R/'src/player.s',R/'tools/reference/mini_direct_frame_stack_1110.s')
    proof = dict(passed=True,ROM_written=False,parent_SHA256=Strict.TARGET,
                 published_parent_SHA256=H.PIN,expected_memory_only_SHA256=M.sha(final),
                 patches=patches,combined_patches=strict['patches']+patches,cold=cold,foreground=fg,
                 bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in files})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,memory_SHA256=M.sha(final),foreground=fg)),flush=True)


if __name__=='__main__':
    main()
