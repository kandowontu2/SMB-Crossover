"""Qualify the shared default draw packet directly on the 991b cartridge."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from check_mini_funded_actor_1108_v3 import registers, run, slim_fork
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at
import profile_mini_mario_matched_1110 as Match
from prepare_mini_lane_audio_native_1110 import CODE, COOKIE, verify_payload


R, P, N = Match.R, Match.P, Match.N
ROM = R/'build/mini-step-scroll-weapon-native-1110/candidate.nes'
PIN = '991b4cd1033890aaa7dc0fa773dc167496fd0937bc449c8a3a209709f2a6c318'
KERNEL = R/'build/mini-step-alu-1110/kernel.bin'
PROFILE = R/'build/mini-world-draw-1110/aggregate.json'
PATCH_PC, WRAPPER, CALLER = 0xbe5b, 0xbe45, 0xa7b4
PREIMAGE = bytes.fromhex('a9b18d6c01a9a28d6d01a984')
REPLACEMENT = bytes.fromhex('a9288d6c01a9bd8d6d01a994')
ENDPOINTS = {'default':(148,0xbd28),'arthur':(191,0xb784),'rogue':(132,0xa000)}
SMC = slice(0x15a,0x17b)


def offset(bank, pc):
    return 16+8192*bank+(pc&8191)


def check_span(raw, bank, pc, data):
    at = offset(bank,pc)
    assert raw[at:at+len(data)]==data,(bank,hex(pc))


def link(raw):
    assert P.sha(raw)==PIN
    old = bytes.fromhex('8d6a0108ad0260c920f02fc902d007adee5fc901f015')
    check_span(raw,79,WRAPPER,old)
    check_span(raw,79,PATCH_PC,PREIMAGE+bytes.fromhex('4cbfbe'))
    check_span(raw,79,0xbe70,bytes.fromhex('a9008d6c01a9a08d6d01a9844cbfbe'))
    check_span(raw,79,0xbe7f,bytes.fromhex('a9848d6c01a9b78d6d01a9bf4cbfbe'))
    check_span(raw,79,0xbebf,bytes.fromhex('8d62012868684c6101'))
    check_span(raw,4,0xa2b1,bytes.fromhex('8d6a01')+REPLACEMENT+bytes.fromhex('4c5a01'))
    check_span(raw,86,CALLER,bytes.fromhex('8d6a01a9458d6c01a9be8d6d01a9cf205a01'))
    check_span(raw,20,0xbd28,bytes.fromhex('0848ad0260c929'))
    assert P.address(P.bundle(raw),'HuDrawAll')==WRAPPER
    row = json.loads(PROFILE.read_text())['default_draw_packet_retarget']
    at = offset(79,PATCH_PC)
    assert row['file_offset']==at and row['old_hex']==PREIMAGE.hex() and row['new_hex']==REPLACEMENT.hex()
    image = raw[:at]+REPLACEMENT+raw[at+len(REPLACEMENT):]
    verify_payload(raw,KERNEL)
    verify_payload(image,KERNEL)
    return image,dict(physical_PRG=79,CPU_half_open=[PATCH_PC,PATCH_PC+len(PREIMAGE)],
                      file_offset=at,old_hex=PREIMAGE.hex(),new_hex=REPLACEMENT.hex())


def bank_pc(c):
    tag = c.memory.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
    return tag,c.pc


def warm_draw(m, flags, *, a=85, x=3, y=91):
    m[0x5115] = 214
    N.put(m,CurrentBank=214,NmiDisable=255)
    c = cpu_at(m,CALLER,252,flags,x=x,y=y)
    c.a = a
    return c


def foreign_routes(images):
    seed = [N.fresh(b) for b in images]
    counts, delta = Counter(),Counter()
    for owner,alt,p in product(range(42),(0,1,255),(0x21,0x25,0x65,0xe0)):
        role = 'arthur' if owner==32 else 'rogue' if (owner,alt)==(2,1) else 'default'
        endpoint = ENDPOINTS[role]
        cpus = []
        for m in seed:
            q = slim_fork(m)
            N.put(q,SelectedCharacter=owner)
            q[0x5fee] = alt
            c = warm_draw(q,p)
            run(c,lambda z:bank_pc(z) in ENDPOINTS.values())
            assert bank_pc(c)==endpoint,(owner,alt,bank_pc(c))
            cpus.append(c)
        a,b = cpus
        assert registers(a,0xef)[:4]==registers(b,0xef)[:4],(owner,alt,p)
        assert b.sp-a.sp == (3 if role=='default' else 0),(owner,alt,p,a.sp,b.sp)
        left,right = semantic(a),semantic(b)
        assert left[:4]==right[:4] and left[5:]==right[5:],(owner,alt,p)
        assert bytes(a.memory[SMC])==bytes(b.memory[SMC]),(owner,alt,p)
        saving = a.processorCycles-b.processorCycles
        assert (0<saving<74 if role=='default' else saving==0),(role,saving)
        counts[role] += 1
        delta[role,saving] += 1
    return dict(cases=dict(counts),cycles_to_entry=[[role,cycles,n] for (role,cycles),n in sorted(delta.items())])


def cold(bundle,owner):
    if owner in (0,41):
        old = Match.KERNEL
        try:
            Match.KERNEL = KERNEL
            m,boot = Match.cold(bundle,owner)
        finally:
            Match.KERNEL = old
        if owner==41:
            raw = bundle['raw']
            assert bytes(m.ram[3][:5120])==raw[CODE:CODE+5120]==KERNEL.read_bytes()
            assert bytes(m.ram[2][0x1000:0x1300])==raw[CODE+5120:CODE+5120+0x300]
            attr = R/'build/mini-projection-reuse-1110/proof.json'
            assert P.sha(m.ram[2][0x1300:0x1400])==json.loads(attr.read_text())['exact_runtime_attribute_SHA256']
            assert all(bytes(m.ram[i][0x1fe0:0x1ff0])==raw[COOKIE:COOKIE+16] for i in (2,3))
        return m,boot
    slot = {2:2,25:24,32:31}[owner]
    m = N.fresh(bundle)
    N.put(m,CrossoverMenuIndex=slot)
    for name in ('MenuResolveCharacter','QueueSelection','DrawSelectionPreview'):
        N.invoke(m,name)
    if owner==2:
        Match.menu_key(m,32)
        assert m[0x5fee]==1
    assert N.get(m,'SelectedCharacter')==owner
    start = Match.menu_key(m,16)
    assert N.get(m,'CrossoverMenuState')==0
    N.invoke(m,'ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for updates in range(600):
        if (N.get(m,'OperMode_Task'),N.get(m,'GameEngineSubroutine'))==(3,8):
            break
        Match.controls(m,0)
        N.invoke(m,'GameLoop',x=0,y=0)
        N.consume(m)
    else:
        raise AssertionError(('Actual owner entrance',owner))
    assert N.get(m,'SelectedCharacter')==owner and N.get(m,'AreaAddrsLOffset')==5
    return m,dict(menu_slot=slot,entrance_updates=updates,initial_CHR=list(m.chr_latches))


def whole(before,after):
    images = [P.bundle(q) for q in (before,after)]
    scene = json.loads(Match.WITNESS.read_text())['scene']
    rows = []
    for owner,crowd in product((0,2,32,41),(False,True)):
        boot = [cold(b,owner) for b in images]
        assert boot[0][1]==boot[1][1]
        pair = [Match.arena(slim_fork(m),scene,crowd) for m,_ in boot]
        savings = []
        for key in (0,0,193,193,1,1):
            cpus = []
            for m in pair:
                m.writes.clear()
                m.ram_writes.clear()
                m.ppu_log.clear()
                Match.controls(m,key)
                c = cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
                run(c,lambda z:(z.pc,z.sp)==(STOP,252))
                cpus.append(c)
            a,b = cpus
            assert semantic(a)==semantic(b) and bytes(a.memory[SMC])==bytes(b.memory[SMC]),(owner,crowd,key)
            savings.append(a.processorCycles-b.processorCycles)
            for m in pair:
                N.consume(m)
        assert savings==[0 if owner in (2,32) else 74]*6,(owner,crowd,savings)
        rows.append(dict(owner=owner,crowd=crowd,boot=boot[0][1],savings=savings))
    return rows


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    raw = ROM.read_bytes()
    final,patch = link(raw)
    routes = foreign_routes([P.bundle(im) for im in (raw,final)])
    print('Draw endpoints',routes,flush=True)
    loops = whole(raw,final)
    print('Whole GameLoop',[(r['owner'],r['crowd'],r['savings']) for r in loops],flush=True)
    paths = (Path(__file__),ROM,PROFILE,KERNEL,Path(Match.__file__),R/'src/mmc5.s',
             R/'src/game.s',R/'src/metasprite_engine.s')
    out = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(final),
               patches=[patch],endpoints=routes,whole_GameLoop=loops,
               bindings={str(p):P.sha(p.read_bytes()) for p in paths})
    args.output.mkdir(exist_ok=True)
    (args.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
    main()
