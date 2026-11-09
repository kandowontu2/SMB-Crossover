"""Qualify the source-funded living Mini graphics ingress on exact 90a8."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import tempfile

import check_mini_box_transport_1110 as Body
import check_native_audio_dirty_clear_1110 as Base
import profile_mini_busy_1108_v1 as P
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_visibility_dispatch_1110_v1 import memory


M,N,R = Base.M,Base.N,Base.R
ROM,PIN = Base.BASE,Base.PIN
SOURCE = R/'tools/reference/mini_player_graphics_visibility_1110_v1.s'
ENTRY,COMMON,END = 0xa2cd,0xa309,0xa392
STOP = 0x5b00
ALIAS = (0xb7bf,0xbff1)
PROFILE = R/'build/mini-90a8-enemy-profile-1110/capture/instruction-sample.json'


def ingress(raw):
    assert Base.code(raw,1,END,6)==bytes.fromhex('2094aa4ca0a3')
    prg = raw[16:16+128*8192]
    refs = []
    for i in range(len(prg)-15):
        p = prg[i:i+15]
        if p[0]==p[5]==p[10]==0xa9 and p[2:5]==b'\x8d\x6c\x01' and p[7:10]==b'\x8d\x6d\x01' and p[11]==129:
            target = p[1]|p[6]<<8
            if ENTRY<=target<END:
                bank,rel = divmod(i,8192)
                refs.append((bank,0xa000+rel,target))
    assert refs==[(9,0xbce0,ENTRY),(62,ALIAS[0],COMMON),(82,ALIAS[1],COMMON),(126,0xa3df,ENTRY)]
    assert Base.code(raw,126,0x83b5,12)==bytes.fromhex('ad450148a9808d45018d1551')
    assert Base.code(raw,126,0x83fb,28)==bytes.fromhex('2019852013a3208fab20d58520518620dfbf8d4401688d45018d1551')
    assert 'farcall PlayerGfxHandler::KmNativeGraphics' in (R/'src/kamikaze_mario_render_v2.inc').read_text()
    assert Base.code(raw,126,0x912b,18)==bytes.fromhex('8d6a01a9ee8d6c01a9b98d6d01a9ce4c5a01')
    assert Base.code(raw,78,0xb9f7,4)==bytes.fromhex('c929f00d')
    return refs


def compose(raw,out):
    source = SOURCE.read_text()
    with tempfile.TemporaryDirectory(prefix='link-',dir=out) as tmp:
        old,a = M.assemble(Path(tmp)/'original','FAST=0\n'+source,ENTRY,END-ENTRY)
        new,b = M.assemble(Path(tmp)/'successor','FAST=1\n'+source,ENTRY,END-ENTRY)
    assert a==b==dict(PlayerGraphics=ENTRY,CommonGraphics=COMMON,GraphicsEnd=END)
    exact = Base.code(raw,1,ENTRY,END-ENTRY)
    assert len(old)==len(new)==END-ENTRY and old==exact,(
        len(old),len(new),[(hex(ENTRY+i),x,y) for i,(x,y) in enumerate(zip(old,exact)) if x!=y][:16])
    row = dict(file_offset=Base.position(1,ENTRY),physical_PRG=1,CPU_half_open=[ENTRY,END],
               role='Living Mini graphics visibility shortcut with original fixed renderer entry',
               old_hex=old.hex(),new_hex=new.hex())
    return install(raw,[row]),row


def sample(owner,engine,phase,death):
    return dict(SelectedCharacter=owner,OperMode=1 if engine else 0,OperMode_Task=3,
                GameEngineSubroutine=engine,FrameCounter=phase,PlayerStatus=phase,
                InjuryTimer=phase,GuestHurtKind=phase,GuestHurtVisible=phase,MmDeathFlag=death,
                Player_Y_HighPos=1,Player_Y_Position=176,Player_X_Position=82,NumberofLives=2)


def local(seed,fields,a,x,y,p,pc=ENTRY):
    m = slim_fork(seed)
    m.raw_page(1,129)
    N.put(m,CurrentBank=129,**fields)
    c = N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp = a,x,y,p,224
    c.stPushWord(STOP-1)
    return c


def execute(c,visits=None):
    def see(z):
        if visits is not None and z.pc in (0x912b,COMMON,0xb55e):
            visits[z.pc] += 1
    run(c,lambda z:(z.pc,z.sp)==(STOP,224),see)


def state(c):
    return registers(c,0xef),live_stack(c),memory(c.memory)


def foreground(before,after):
    images = [M.bundle(raw) for raw in (before,after)]
    seeds = [N.fresh(b) for b in images]
    mini = [P.fixture(b,0,False,False) for b in images]
    stats = Counter()

    def compare(owner,engine,phase,death,variant,p,pc=ENTRY):
        kw = sample(owner,engine,phase,death)
        if owner==0:
            kw['MarioVariant'] = variant
        if owner==2:
            kw['RdVariant'] = variant&1
        if owner in (3,4,5,9,10,12,22,25,29,33,39):
            kw.update(Cv3Variant=variant&3,Z2Variant=variant&1,RlVariant=variant&1,
                      FmGroups=variant*17&255,FmAlts=variant*17&255)
        visits = [Counter(),Counter()]
        cpus = [local(m,kw,0x80+phase,3+phase,19+phase,p,pc) for m in (mini if owner==41 else seeds)]
        for c,seen in zip(cpus,visits,strict=True):
            execute(c,seen)
        old,new = cpus
        warm = owner==41 and death==0 and pc==ENTRY
        a,b = state(old),state(new)
        assert a==b,((owner,engine,phase,death,variant,p,pc),a[:2],b[:2],
                     old.memory[0x15a:0x17b],new.memory[0x15a:0x17b])
        assert visits[0][0x912b]-visits[1][0x912b]==int(warm)
        stats['mini' if warm else 'foreign_or_original',old.processorCycles-new.processorCycles] += 1

    for owner,phase,death,p in product(range(42),(0,1),(0,1),(0x20,0x21,0x64,0xe5)):
        compare(owner,8,phase,death,phase,p)
    for owner,engine,phase,death,p in product((0,1,2,7,9,39,41),(0,5,7,9,10,11),(0,1),(0,1),(0x20,0x61)):
        compare(owner,engine,phase,death,0,p)
    for variant,phase,pc in product(range(9),(0,1),(ENTRY,COMMON)):
        compare(0,8,phase,0,variant,0x61,pc)
    whole = Body.D.check_full_cpu(before,after,{})
    return dict(direct_cases=sum(stats.values()),cycles_saved=[[k,n,c] for (k,n),c in sorted(stats.items())],
                whole_GameCore=whole)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'proof.json').exists()
    before = ROM.read_bytes()
    assert M.sha(before)==PIN and json.loads(PROFILE.with_name('binding.json').read_text())['ROM_sha256']==PIN
    refs = ingress(before)
    after,row = compose(before,out)
    print('same extent linked',M.sha(after),flush=True)
    full = foreground(before,after)
    paths = (Path(__file__),SOURCE,R/'src/player.s',R/'src/guest_injury.s',R/'src/hot_render_gate.s',
             R/'src/game.s',R/'src/kamikaze_mario_render_v2.inc',PROFILE,PROFILE.with_name('binding.json'))
    receipt = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                   patches=[row],linked_ingresses=refs,entry_pcs=[ENTRY,COMMON,END],**full,
                   bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes()) for p in paths})
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(full),flush=True)


if __name__=='__main__':
    main()
