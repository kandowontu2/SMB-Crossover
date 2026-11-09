"""Qualify the original Tank contact precheck at its exact native ingress."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_native_contact_1110 as Contact
import check_mini_native_contact_irq_1110 as Scenes
import check_native_enemy_ordinary_dispatch_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_lift_admission_async_1108_v1 import final, tags
from check_mini_shared_offscreen_irq_1110_v1 import lag_pcs


M,N,R = Contact.M,Contact.N,Contact.R
BASE = R/'build/mini-parser-audio-native-1110/candidate.nes'
PIN = '3a3832825bc6a2628fef7b3ccc3e760262510b86a80d78bc74ec3005af3119df'
TANK = R/'build/mario-tank-visible-host-1101-v5'
SOURCE = R/'tools/reference/native_contact_tank_precheck_1110.s'
FUNDING = TANK/'candidate-patches.json'
PROFILE = R/'build/mini-seven-contact-profile-1110/capture/instruction-sample.json'
PROFILE_BIND = PROFILE.with_name('binding.json')
PREVIOUS = R/'build/mini-helper-powered-injury-native-1110/candidate.nes'
ENTRY,END = 0xaf96,0xafd6
CHECK,NATIVE,WORKER = (156,0xbfb0),(191,0xad52),(2,0xb60b)
GATE_TAG = 206
STOP = 0x5b00
SMC = (0x0162,0x016a,0x016c,0x016d,0x0179)
point = lambda c:(tags(c),c.pc)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def at(bank,pc):
    return 16+8192*bank+(pc&8191)


def link(raw,out):
    source = read(FUNDING)
    assert source['passed']
    spans = {row['owner']:row for row in source['patches']}
    owner = spans['MT_CONTACT']
    old = bytes.fromhex(owner['new_hex'])
    assert owner['file_offset']==at(78,ENTRY) and len(old)==101
    assert raw[at(78,ENTRY):at(78,ENTRY)+len(old)]==old
    ingress = bytes.fromhex(spans['MtRomContactV3']['new_hex'])
    assert spans['MtRomContactV3']['file_offset']==at(126,0x9699)
    prg = raw[16:1048592]
    assert prg.count(ingress)==1 and raw[at(126,0x9699):at(126,0x96ab)]==ingress
    assert raw[at(126,0x96ab):at(126,0x96bf)]==bytes.fromhex('900160ad9c07f0064cf59a0a060420b1ed900160')
    bank = raw[at(78,0xa000):at(78,0xa000)+8192]
    assert all(bytes((op,pc&255,pc>>8)) not in bank for pc in range(ENTRY,END) for op in (0x20,0x4c,0x6c))
    assert raw[at(28,0xbfb0):at(28,0xbfb5)]==bytes.fromhex('ad0260d030')
    assert raw[at(28,0xbfe5):at(28,0xbfe7)]==b'\x18\x60'
    assert raw[at(28,0xbfe7):at(28,0xbff7)]==(TANK/'cookie.bin').read_bytes()
    assert raw[1048592+501*1024:1048592+503*1024]==(TANK/'code501.bin').read_bytes()+(TANK/'art-code502.bin').read_bytes()
    profile = read(PROFILE)
    earlier = PREVIOUS.read_bytes()
    assert read(PROFILE_BIND)['ROM_sha256']==M.sha(earlier)
    assert all(edge in profile['farcall_edges'] for edge in ('126:96ab -> ce:af96','78:afaa -> 9c:bfb0','78:afd5 -> bf:ad52'))
    for bank,lo,hi in ((78,ENTRY,END),(28,0xbfb0,0xbff7),(63,0xad52,0xad83),(59,0xbcba,0xbcd9)):
        assert earlier[at(bank,lo):at(bank,hi)]==raw[at(bank,lo):at(bank,hi)]

    with tempfile.TemporaryDirectory(prefix='contact-',dir=out) as name:
        tmp = Path(name)
        cfg,obj,binary = (tmp/f'contact.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { C:start=$AF96,size=64,file=%O; } SEGMENTS { CONTACT:load=C,type=ro; }\n')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        new = binary.read_bytes()
    assert len(new)==END-ENTRY
    patch = dict(physical_PRG=78,CPU_half_open=[ENTRY,END],file_offset=at(78,ENTRY),
                 old_hex=old[:len(new)].hex(),new_hex=new.hex(),role='Tank-only contact precheck')
    return install(raw,[patch]),[patch]


def cold(image,owner=None):
    previous = N.Bus
    N.Bus = IRQ.Q.DispatchBus
    try:
        if owner==41:
            return Contact.L.fixture(image,0,False,False)
        if owner in (25,39):
            return Scenes.scene(image,owner,0)
        m = N.fresh(image)
        if owner==0:
            N.put(m,SelectedCharacter=0,MarioVariant=7,OperMode=1,FamilyMainCommit=1,
                  DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,NumberofLives=2,
                  AreaPointer=0x25,Mirror_PPUCTRL=160)
            N.invoke(m,'InitScreen')
            assert bytes(m.ram[2][0x1fe0:0x1ff0])==(TANK/'cookie.bin').read_bytes()
            assert bytes(m.ram[2][0x1600:0x1a00])==(TANK/'code501.bin').read_bytes()
        return m
    finally:
        N.Bus = previous


def setup(seed,owner,mode,p,*,variant=0,enemy=6,slot=0,star=0,injury=0,power=0,upward=False,
          overlap=True,bad_cookie=None,whole=False):
    c = Contact.setup(seed,owner,enemy,8,mode,p,pc=Contact.ENEMY if whole else 0x15a,
                      slot=slot,star=star,injury=injury,vertical=0xfc if upward else 4,overlap=overlap)
    m = c.memory
    N.put(m,MarioVariant=variant,PlayerStatus=power,NmiDisable=255,OperMode=1,OperMode_Task=3,
          Mirror_PPUMASK=30,DisableScreenFlag=0,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
    if bad_cookie is not None:
        m.ram[2][0x1fe0+bad_cookie] ^= 1
    if not whole:
        m[0x016a],m[0x016c],m[0x016d] = c.a,ENTRY&255,ENTRY>>8
        c.a = GATE_TAG
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    return c


def done(c):
    return (c.pc,c.sp)==(STOP,236)


def execution(c,observe=None):
    hits,snapshots = Counter(),[]

    def watch(z):
        p = point(z)
        if p in (CHECK,NATIVE,WORKER,(GATE_TAG,ENTRY),(254,0x976c),(254,0x9806),(254,0x98b5),(254,0x9af5)):
            hits[p] += 1
        if p in (CHECK,NATIVE,WORKER):
            m = z.memory
            snapshots.append((p,registers(z,0xef),tuple(m[at] for at in SMC[:-1]),tuple(m.rawtags)))
        if observe:
            observe(z)

    run(c,done,watch)
    return hits,snapshots


def same(a,b,traces,raw):
    old,new = traces[0][0],traces[1][0]
    called = bool(old[GATE_TAG,ENTRY])
    expected_skip = int(called and raw!=0)
    assert old[CHECK]-new[CHECK]==expected_skip and old[NATIVE]==new[NATIVE] and old[WORKER]==new[WORKER]
    assert all(old[k]==new[k] for k in set(old)|set(new) if k!=CHECK)
    prior,live = traces[0][1],traces[1][1]
    assert len(prior)==len(live)+expected_skip
    if expected_skip:
        assert prior[0][0]==CHECK
        prior = prior[1:]
    for (pa,ra,sa,ma),(pb,rb,sb,mb) in zip(prior,live,strict=True):
        assert pa==pb and ra[:-1]==rb[:-1] and sa==sb and ma==mb,(pa,ra,rb,sa,sb,ma,mb)
        assert rb[-1]-ra[-1]==(0 if pa==CHECK else 2)
    assert registers(a,0xef)==registers(b,0xef) and live_stack(a)==live_stack(b)
    m,n = a.memory,b.memory
    Contact.A.P.compare_memory(m,n)
    assert Contact.Link.Q.memory(m)==Contact.Link.Q.memory(n) and m.ram_writes==n.ram_writes
    old_maps,new_maps = [[v for k,v in q.writes if k==0x5115] for q in (m,n)]
    if expected_skip:
        indexes = [i for i in range(len(old_maps)-1) if old_maps[i:i+2]==[156,GATE_TAG]]
        at_index, = indexes
        del old_maps[at_index:at_index+2]
    assert old_maps==new_maps
    assert [(k,v) for k,v in m.writes if k not in (*SMC,0x145,0x5115) and not 0x17b<=k<0x200]==[
            (k,v) for k,v in n.writes if k not in (*SMC,0x145,0x5115) and not 0x17b<=k<0x200]
    return called,a.processorCycles-b.processorCycles


def foreground(before,after):
    images = Contact.L.bundles(before,after)
    groups = {raw:[cold(b,raw) for b in images] for raw in (None,0,25,39,41)}
    counts,outcomes = Counter(),Counter()

    def check(label,raw,mode,p,**kwargs):
        seeds = groups[raw] if raw in groups and (raw!=0 or kwargs.get('variant')==7) else groups[None]
        pair = [setup(seed,raw,mode,p,**kwargs) for seed in seeds]
        traces = [execution(c) for c in pair]
        used,save = same(*pair,traces,raw)
        hits = traces[1][0]
        counts[label,used,save] += 1
        for k in ((254,0x976c),(254,0x9806),(254,0x98b5),(254,0x9af5)):
            outcomes[label,k[1]] += hits[k]
        return hits

    for raw,mode,p in product(range(1,256),(0,1),(0x21,0x65)):
        hits = check('nonzero',raw,mode,p,variant=7 if raw in (8,41) else raw&7,slot=raw%6)
        assert not hits[CHECK] and hits[NATIVE] and not hits[WORKER]
    for variant,mode,p,enemy in product(range(9),(0,1),(0x21,0x60,0x65),(6,7,13)):
        hits = check('raw0 variants',0,mode,p,variant=variant,enemy=enemy,power=(p>>4)%3)
        assert hits[CHECK]==1 and bool(hits[WORKER])==(variant==7)
    for bad,mode,p in product(range(16),(0,1),(0x21,0x65)):
        hits = check('Tank header faults',0,mode,p,variant=7,power=2,bad_cookie=bad)
        assert hits[CHECK]==hits[NATIVE]==1 and hits[WORKER]==0
    for raw,mode,enemy,star,injury,upward,overlap in product((0,8,25,39,41),(0,1),(6,7,13,46),
            (0,2),(0,16),(False,True),(False,True)):
        check(f'native body {raw}',raw,mode,0x21,variant=7 if raw==0 else 1 if raw==8 else 0,
              enemy=enemy,star=star,injury=injury,upward=upward,overlap=overlap,whole=True)
    assert all(outcomes['native body 41',pc] for pc in (0x976c,0x9806,0x98b5,0x9af5))
    return dict(cycles=[[name,used,save,n] for (name,used,save),n in sorted(counts.items())],
                outcomes=[[name,pc,n] for (name,pc),n in sorted(outcomes.items()) if n])


def vectors(before,after):
    images = Contact.L.bundles(before,after)
    old,new = images
    lag,normal = lag_pcs(cold(new,41))
    counts,minima,deepest = Counter(),[255,255],{}

    def paired(z,kind,base,other,record=True):
        a,b = fork(z),fork(z,other)
        for c in (a,b):
            if kind=='normal':
                N.put(c.memory,NmiDisable=0)
            c.memory.writes.clear()
            c.memory.ram_writes.clear()
            c.memory.ppu_log.clear()

        def visit(c):
            minima[1] = min(minima[1],c.sp)
            key = base is new,N.get(c.memory,'SelectedCharacter'),kind,tuple(c.memory.rawtags)
            if record and kind!='IRQ' and not c.p&4 and (key not in deepest or c.sp<deepest[key][0].sp):
                deepest[key] = fork(c),base,other
                deepest[key][0].memory.vector_floor = None

        assert IRQ.interrupt(a,kind,lag,normal,visit)==IRQ.interrupt(b,kind,lag,normal)
        assert IRQ.hardware(a)==IRQ.hardware(b) and Contact.Link.Q.memory(a.memory)==Contact.Link.Q.memory(b.memory)
        counts[kind if record else 'nested_IRQ'] += 1
        return a

    cases = []
    profiles = (
        (41,0,0,None,True),(41,1,0,None,True),(25,0,0,None,True),(39,1,0,None,True),
        (0,0,0,None,False),(0,1,7,None,True),(0,0,7,15,False),(8,1,1,None,False),
    )
    for side,(raw,mode,variant,bad,whole) in product((0,1),profiles):
        base,other = images[side],images[1-side]
        seed = cold(base,raw if raw in (25,39,41) or raw==0 and variant==7 else None)
        cpu = setup(seed,raw,mode,0x21,variant=variant,bad_cookie=bad,whole=whole,power=2 if raw==0 else 0)
        seen,continuations = set(),[]
        active = False

        def watch(c):
            nonlocal active
            tag,pc = point(c)
            if (tag,pc)==(GATE_TAG,ENTRY):
                active = True
            if (tag,pc)==(254,0x96ab):
                active = False
            relevant = tag==GATE_TAG and ENTRY<=pc<END or tag==156 and 0xbfb0<=pc<0xbfe7
            transport = active and 0x15a<=pc<0x17b
            k = tag,pc,c.sp,c.p&4
            if k in seen or not (relevant or transport):
                return
            seen.add(k)
            minima[0] = min(minima[0],c.sp)
            continuations.append(paired(c,'FF',base,other))
            if not c.p&4:
                continuations.append(paired(c,'IRQ',base,other))
            if relevant and pc in (ENTRY,0xbfb0):
                resumed = paired(c,'normal',base,other)
                run(resumed,done)

        execution(cpu,watch)
        assert seen,(side,raw,mode,variant,bad)
        for c in continuations:
            run(c,done)
            assert final(c)==final(cpu) and bytes(c.memory[:11])==bytes(cpu.memory[:11]),(side,raw,mode,variant,bad)
        cases.append(dict(parent=side==0,raw=raw,mode=mode,variant=variant,bad_cookie=bad,cuts=len(seen)))
    for c,base,other in deepest.values():
        paired(c,'IRQ',base,other,False)
    assert all(counts[k] for k in ('FF','IRQ','normal','nested_IRQ')) and min(minima)>0x7a
    return dict(cuts=dict(counts),minimum_SP=minima,cases=cases)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    dest = out/'proof.json'
    assert not dest.exists()
    before = BASE.read_bytes()
    assert M.sha(before)==PIN
    after,patches = link(before,out)
    front = foreground(before,after)
    print('Exact full contact, owner aliases and all Tank header faults passed.',flush=True)
    irqs = vectors(before,after)
    refs = (Path(__file__),SOURCE,BASE,FUNDING,PROFILE,PROFILE_BIND,PREVIOUS,TANK/'graft.s',TANK/'visible.s',
            TANK/'cookie.bin',TANK/'code501.bin',TANK/'art-code502.bin',R/'src/mmc5.s',R/'src/reset.s')
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                 patches=patches,foreground=front,vectors=irqs,
                 bindings={str(path.resolve()):M.sha(path.read_bytes()) for path in refs})
    dest.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(dest,proof['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
