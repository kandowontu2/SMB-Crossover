"""Qualify full-index native contact offsets and actual rejected callers."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_movement_prefix_1110 as M
import check_mini_native_contact_1110 as Contact
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_native_enemy_ordinary_dispatch_irq_1110 import hardware, interrupt


R, N, D, P, Q = M.R,M.N,M.D,M.P,M.Q
BASE = R/'build/mini-shared-game-loop-tail-native-1110/candidate.nes'
PIN = '29aa4f8df07425dfe6dcdaaa431421c78347adbca5979c332edce69c79367cf5'
SOURCE = R/'tools/reference/native_player_contact_offset_1110.s'
PROFILE = R/'build/mini-dd-clear-and-nmi-profile-1110/capture/instruction-sample.json'
ENTRY, END, OLD_OFFSET, CORE = 0x9659,0x9690,0x967d,0x9512
OLD = bytes.fromhex('ad0260f009c908d005a50e4ab028203a9bb023bda805d01ea50fc908d018b51f2920d012'
                    '204b9b201295a60db009bd3d0629fe9d3d0660')
CALLERS = (('normal',0xa488,0xa4b7,6),('flame',0xa6cc,0xa4b7,0x33),
           ('bullet',0xac55,0xa4b7,0x33),('pickup',0xb806,0xa4b7,0x2e),
           ('bowser_front',0xa8a9,0xa908,0x2d),('bowser_rear',0xa8df,0xa908,0x2d))
ENGINE_CASES = (0,4,7,8,9,10,11,0x7f,0x80,0xff)


def code(raw,bank,pc,n):
    at = D.offset(bank,pc)
    return raw[at:at+n]


def references(raw, bank, target, ops):
    if bank is None:
        prg,base = raw[16:1048592],0
    else:
        prg,base = code(raw,bank,0xa000,8192),8192*bank
    arg = target.to_bytes(2,'little')
    return [divmod(base+i,8192) for i,op in enumerate(prg[:-2]) if op in ops and prg[i+1:i+3]==arg]


def link(raw,out):
    assert P.sha(raw)==PIN and len(OLD)==END-ENTRY
    D.check_span(raw,126,ENTRY,OLD)
    D.check_span(raw,126,END,bytes.fromhex('b417c02ed0034c289b'))
    D.check_span(raw,126,0x9b4b,bytes.fromhex('a50d0a0a186904a8ada105290fc90f60'))
    assert references(raw,None,ENTRY,(0x20,0x4c,0x6c))==[(0,0x04b7),(0,0x0908)]
    assert not references(raw,None,END,(0x20,0x4c,0x6c))
    assert not references(raw,126,OLD_OFFSET,(0x20,0x4c))
    packet = bytes.fromhex('a9598d6c01a9968d6d01')
    assert packet not in raw[16:1048592]
    assert references(raw,0,0xa496,(0x20,0x4c))==[(0,a&8191) for _,a,_,_ in CALLERS[:4]]
    assert references(raw,0,0xa8ed,(0x20,0x4c))==[(0,a&8191) for _,a,_,_ in CALLERS[4:]]
    for bank,pc,pattern in ((0,0xa485,'20d7982096a4'),(0,0xa6c6,'20a08a20c2a12096a4'),
                            (0,0xac4f,'20a08a20c2a12096a4'),(0,0xb7e6,'20a08a20e98a20c2a1207cba'),
                            (0,0xa8d3,'a50d48aecd06860da92d951720eda8'),
                            (0,0xa8f9,'20a08ab51fd0eca90a9d460620c2a14c5996'),
                            (126,0x8ac7,'a60d60'),(126,0x9fbb,'a60d60'),(126,0x83c9,'860d2060a2')):
        D.check_span(raw,bank,pc,bytes.fromhex(pattern))
    src = (R/'src/object.s').read_text()
    assert src.count('jmp PlayerEnemyCollision')==2 and 'stx ObjectOffset\n  lda #Bowser' in src
    sample = json.loads(PROFILE.read_text())
    assert sample['scene']['frame']==1460
    assert sample['foreground_opcodes']['126:967d']==18

    with tempfile.TemporaryDirectory(dir=out,prefix='player-contact-') as tmp:
        cfg,obj,binary,lbl = (Path(tmp)/f'contact.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { C:start=$9659,size=$37,file=%O; } SEGMENTS { CONTACT:load=C,type=ro; }')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        labels = {fields[2][1:]:int(fields[1],16) for line in lbl.read_text().splitlines()
                  if (fields:=line.split())}
        data = binary.read_bytes()
    row = M.patch(126,ENTRY,OLD,data)
    return install(raw,[row]),row,labels


def stable(c):
    return Q.state(c),hardware(c),live_stack(c)


def clear_trace(m):
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()


def arithmetic(before,after,labels):
    buses = [N.Bus(P.bundle(raw)) for raw in (before,after)]
    checks = 0
    for slot,p in product(range(256),(0x21,0x24,0x29,0x65,0xe1,0xe9)):
        pair = []
        for m,pc in zip(buses,(OLD_OFFSET,labels['InlineOffset']),strict=True):
            m[0x0d] = slot
            cpu = M.cpu_at(m,pc,244,p,x=slot,y=9)
            run(cpu,lambda z:z.pc==CORE)
            pair.append(cpu)
        a,b = pair
        assert a.x==b.x==slot and a.y==b.y==((slot+1)*4)&255
        assert a.p&0x4c==b.p&0x4c and live_stack(a)==live_stack(b)
        checks += 1
    return checks


def context(seed,owner,slot,enemy,engine,flags,state=0,timer=0,overlap=False,version=0):
    c = Contact.setup(seed,owner,enemy,engine,version,flags,pc=ENTRY,slot=slot,overlap=overlap)
    m = c.memory
    m.raw_page(1,128)
    N.put(m,CurrentBank=128,NmiDisable=255,TimerControl=timer,Player_OffscreenBits=0,
          OperMode=1,OperMode_Task=3,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
    m[(0x1f+slot)&255] = state
    clear_trace(m)
    return c


def done(c):
    return (c.pc,c.sp)==(0x5b00,236)


def cold(before,after):
    return M.cold_seeds(before,after)


def foreground(before,after,labels):
    seeds = cold(before,after)
    counts = Counter()
    joins = Counter()
    for owner,slot,flags,overlap,version in product(range(42),range(6),(0x21,0x65),(False,True),(0,1)):
        pair = [context(seed,owner,slot,6,8,flags,overlap=overlap,version=version)
                for seed in seeds.get(owner,seeds[0])]
        for c in pair:
            N.put(c.memory,FrameCounter=slot&1)
            def inspect(z):
                if z.pc==CORE:
                    joins[owner,slot&1] += 1
                    assert z.y==((slot+1)*4)&255 and z.p&0x40==0
            run(c,done,inspect)
        a,b = pair
        assert stable(a)==stable(b),(owner,slot,flags,overlap,version)
        counts['foreign' if owner!=41 else 'Mini',a.processorCycles-b.processorCycles] += 1
    assert all(joins[owner,parity] for owner in range(42) for parity in (0,1) if owner!=8 or not parity)
    assert joins[8,1]==0
    return dict(all_byte_slots=arithmetic(before,after,labels),cycles=[[ *key,n] for key,n in sorted(counts.items())])


def caller(seed,owner,role,call,ingress,enemy,engine,state,timer,flags):
    slot = 1 if role!='bowser_rear' else 5
    c = context(seed,owner,slot,enemy,engine,flags,state,timer)
    m = c.memory
    N.put(m,FrameCounter=2)
    m[0x06cd] = 5
    c.pc,c.sp = ingress,250
    c.stPushWord(0x83cd)         # Real enclosing GameCore JSR, ending at $83CE.
    if role=='bowser_rear':
        c.stPush(1)             # RunBowser's saved front ObjectOffset.
    c.stPushWord(call+2)
    clear_trace(m)
    return c


def join_rejected(a,b,role,return_pc):
    for c in (a,b):
        run(c,lambda z:z.pc==return_pc)
    volatile = (a.a!=b.a or (a.p^b.p)&0x83!=0)
    assert stable_without_volatile(a)==stable_without_volatile(b),(role,return_pc)
    for _ in range(250):
        assert D.bank_pc(a)==D.bank_pc(b),(role,hex(a.pc),hex(b.pc))
        assert stable_without_volatile(a)==stable_without_volatile(b),(role,hex(a.pc))
        if registers(a,0xef)==registers(b,0xef):
            return volatile,D.bank_pc(a)
        a.step()
        b.step()
    raise AssertionError(('Actual caller never overwrote rejected flags',role,hex(a.pc)))


def stable_without_volatile(c):
    m = c.memory
    return registers(c,0x6c)[1:],Contact.Link.Q.memory(m),hardware(c),live_stack(c)


def rejected(before,after):
    counts,sites = Counter(),set()
    seeds = cold(before,after)
    for owner,(role,call,ingress,enemy),engine,state,timer in product(
            seeds,CALLERS,ENGINE_CASES,(0x20,0xa0),(0,1)):
        pair = [caller(seed,owner,role,call,ingress,enemy,engine,state,timer,0x21) for seed in seeds[owner]]
        changed,site = join_rejected(*pair,role,call+3)
        sites.add((role,*site))
        counts[role,changed] += 1
    assert all(counts[role,True] for role,_,_,_ in CALLERS)
    return dict(cases=[[ *key,n] for key,n in sorted(counts.items())],actual_convergence_sites=sorted(sites))


def vectors(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    seeds = cold(before,after)
    lag,normal = M.lag_pcs(seeds[41][1])
    counts,sites,nested = Counter(),set(),{}
    sp = [255,255]

    def paired(z,kind,side,role,record=True):
        a,b = fork(z),fork(z,images[1-side])
        for c in (a,b):
            clear_trace(c.memory)

        def inspect(c):
            sp[1] = min(sp[1],c.sp)
            key = side,role,N.get(c.memory,'SelectedCharacter'),tuple(c.memory.rawtags)
            if kind=='FF' and not c.p&4 and (key not in nested or c.sp<nested[key].sp):
                nested[key] = fork(c)
                nested[key].memory.vector_floor = None

        x = interrupt(a,kind,lag,normal,inspect if record else None)
        y = interrupt(b,kind,lag,normal)
        assert x==y and stable(a)==stable(b),(role,side,kind,z.pc)
        counts[kind if record else 'nested_IRQ'] += 1

    for side,owner,(engine,state) in product((0,1),seeds,((8,0),(4,0x20))):
        c = context(seeds[owner][side],owner,3,6,engine,0x21,state)
        seen = set()

        def watch(z):
            tag,pc = D.bank_pc(z)
            key = tag,pc,z.sp
            if key in seen or tag!=254 or not (ENTRY<=pc<END or CORE<=pc<=0x9574 or 0x9b3a<=pc<=0x9b5a):
                return
            seen.add(key)
            sites.add((side,tag,pc))
            sp[0] = min(sp[0],z.sp)
            paired(z,'FF',side,engine)
            if not z.p&4:
                paired(z,'IRQ',side,engine)

        run(c,done,watch)
        assert seen
    for (side,role,_,_),c in nested.items():
        paired(c,'IRQ',side,role,False)

    for owner,(role,call,ingress,enemy),kind in product(seeds,CALLERS,('FF','IRQ','normal')):
        pair = [caller(seed,owner,role,call,ingress,enemy,4,0x20,0,0x21) for seed in seeds[owner]]
        for c in pair:
            run(c,lambda z:z.pc==ENTRY)
            if kind=='normal':
                N.put(c.memory,NmiDisable=0)
            clear_trace(c.memory)
        a,b = pair
        assert interrupt(a,kind,lag,normal)==interrupt(b,kind,lag,normal)
        assert stable(a)==stable(b)
        join_rejected(a,b,role,call+3)
        counts[f'caller_{kind}'] += 1
    assert min(sp)>0x7a and all(counts[key] for key in ('FF','IRQ','nested_IRQ','caller_normal'))
    return dict(cuts=dict(counts),sites=sorted(sites),minimum_SP=sp)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not (out/'proof.json').exists()
    before = BASE.read_bytes()
    out.mkdir(exist_ok=True)
    after,row,labels = link(before,out)
    front = foreground(before,after,labels)
    print('Native contact and full slot arithmetic passed.',flush=True)
    reject = rejected(before,after)
    print('Actual native caller volatility converged.',flush=True)
    irqs = vectors(before,after)
    refs = (Path(__file__),SOURCE,BASE,PROFILE,PROFILE.with_name('binding.json'),M.KERNEL,
            R/'src/object.s',R/'src/collision.s',R/'src/game.s',R/'src/new_roster_dispatch.s',R/'src/reset.s')
    result = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                  patches=[row],labels=labels,foreground=front,rejected_callers=reject,vectors=irqs,
                  bindings={str(path.resolve()):P.sha(path.read_bytes()) for path in refs})
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
