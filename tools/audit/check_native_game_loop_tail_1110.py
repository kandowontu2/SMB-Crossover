"""Compare the fixed native GameLoop return tails and their real interrupt cuts."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_movement_prefix_1110 as M
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


R, P, N, D, Q, IRQ = M.R,M.P,M.N,M.D,M.Q,M.IRQ
BASE = R/'build/mini-parser-audio-native-1110/candidate.nes'
PIN = '3a3832825bc6a2628fef7b3ccc3e760262510b86a80d78bc74ec3005af3119df'
PROFILE = R/'build/mini-3a-lift-threshold-profile-1110/capture/instruction-sample.json'
SOURCE = R/'tools/reference/native_game_loop_tail_1110.s'
START, BEGIN_JOIN, END = 0x82d9,0x82e1,0x8350
MODES = ((1,3,0,0,0),(1,3,0,0,16),(1,3,0,0x80,16),(1,3,4,0x81,16),
         (2,0,0,1,0),(1,2,0,0x80,0),(0,3,0,0x81,0))


def patch(raw,out):
    for bank,pc,expected in (
        (126,0x82b2,'ad3901f0fbad3a014820d982'),
        (126,START,'a9ff8d3901205683'),
        (126,END,'a900205683608d6a01a9008d6c01a9b48d6d01a9bf205a0160'),
        (63,0xb400,'0848f017eeff5f68288d6a01a9f08d6c01a9b08d6d01a99a4cf3b5'),
        (63,0xb41b,'2031b49006eeff5f4c2bb4a9008dff5f68288d390160'),
        (63,0xb5f3,'8d620168684c6101'),
    ):
        D.check_span(raw,bank,pc,bytes.fromhex(expected))
    fixed = raw[D.offset(126,0x8000):D.offset(126,0x8000)+8192]
    callers = [(0x8000+i,op) for i,op in enumerate(fixed[:-2]) if op in (0x20,0x4c,0x6c)
               and fixed[i+1:i+3]==bytes.fromhex('5683')]
    assert callers==[(0x82de,0x20),(0x8352,0x20)],callers
    with tempfile.TemporaryDirectory(dir=out,prefix='main-tail-') as folder:
        cfg,obj,binary = (Path(folder)/f'tail.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { E:start=$8352,size=3,file=%O; M:start=$8365,size=4,file=%O; } '
                       'SEGMENTS { END_MAIN:load=E,type=ro; MAIN_GATE:load=M,type=ro; }\n')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        code = binary.read_bytes()
    assert code==bytes.fromhex('4c56834c5a01ea')
    rows = [M.patch(126,0x8352,bytes.fromhex('205683'),code[:3]),
            M.patch(126,0x8365,bytes.fromhex('205a0160'),code[3:])]
    return install(raw,rows),rows


def scene():
    return Q.read_scene(PROFILE)


def prepare(seed, role='normal', mode=None):
    c = Q.Edge.prepare(seed,scene(),False)
    m = c.memory
    N.put(m,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,
          DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=255)
    if N.get(m,'SelectedCharacter')==2:
        m[0x5fee] = 1              # Rogue alternate is the completed-Main owner.
        m[0x72da] = 0x82           # Exercise the active scheduler save/restore.
    if mode is not None:
        op,task,timer,status,buttons = mode
        N.put(m,OperMode=op,OperMode_Task=task,GamePauseTimer=timer,
              GamePauseStatus=status,SavedJoypad1Bits=buttons)
    if role=='end':
        c.pc = END
        m[0x5fff] = 3
    return c


def state(c):
    return registers(c,0xef),live_stack(c),Q.state(c),IRQ.hardware(c)


def stop(role):
    return (lambda q:D.bank_pc(q)==(254,BEGIN_JOIN)) if role=='begin' else Q.at_end


def whole(before,after):
    seeds = M.cold_seeds(before,after)
    checks = Counter()
    for owner,rows in seeds.items():
        cases = [('normal',None),*((role,mode) for role,mode in product(('begin','end'),MODES))]
        for role,mode in cases:
            pair = [prepare(seed,role,mode) for seed in rows]
            for c in pair:
                run(c,stop(role))
            a,b = pair
            assert state(a)==state(b),(owner,role,mode,registers(a),registers(b))
            saved = a.processorCycles-b.processorCycles
            assert saved=={'normal':27,'begin':9,'end':18}[role],(owner,role,mode,saved)
            if role=='end':
                wanted = 4 if owner==2 and mode[0] else 0
                assert a.memory[0x5fff]==b.memory[0x5fff]==wanted
                assert a.memory[0x139]==b.memory[0x139]==0
            checks[owner,role,saved] += 1
    return [[*key,count] for key,count in sorted(checks.items())]


def vectors(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    seeds = M.cold_seeds(before,after)
    lag,regular = M.lag_pcs(seeds[41][1])
    counts,deepest,sites = Counter(),{},set()
    minimum = [255,255]

    def paired(c,kind,side,owner,role,nested=False):
        pair = [fork(c,images[i]) for i in (side,1-side)]

        def observe(z):
            minimum[1] = min(minimum[1],z.sp)
            key = side,owner,role,kind,tuple(z.memory.rawtags)
            if kind!='IRQ' and not z.p&4 and (key not in deepest or z.sp<deepest[key].sp):
                deepest[key] = fork(z)
                deepest[key].memory.vector_floor = None

        costs = [IRQ.interrupt(z,kind,lag,regular,observe if i==0 and not nested else None)
                 for i,z in enumerate(pair)]
        assert costs[0]==costs[1] and state(pair[0])==state(pair[1]),(kind,side,owner,role,c.pc)
        counts[role,'nested_IRQ' if nested else kind] += 1
        return pair[0]

    def interesting(c):
        tag,pc = D.bank_pc(c)
        return (tag==254 and (0x82db<=pc<=BEGIN_JOIN or END<=pc<=0x8368)
                or tag==191 and (0xb400<=pc<=0xb447 or 0xb5f3<=pc<=0xb5f8)
                or tag==154 and 0xb0f0<=pc<=0xb133
                or 0x15a<=pc<0x17b)

    for owner,role,side in product(seeds,('begin','end'),(0,1)):
        mode = (1,3,0,0,0 if owner==41 else 16)
        cpu = prepare(seeds[owner][side],role,mode)
        seen = set()

        def visit(c):
            if not interesting(c):
                return
            site = (*D.bank_pc(c),c.sp)
            if site in seen:
                return
            seen.add(site)
            sites.add((side,*site[:2]))
            minimum[0] = min(minimum[0],c.sp)
            kind = 'FF' if c.memory[0x139] else 'normal'
            paired(c,kind,side,owner,role)
            if not c.p&4:
                paired(c,'IRQ',side,owner,role)

        run(cpu,stop(role),visit)
        assert seen

    for (side,owner,role,_,_),c in deepest.items():
        paired(c,'IRQ',side,owner,role,True)

    # Match actual old/new callers before a removed return frame exists and
    # after the previous bank has been restored. These pairs then resume.
    resumes = Counter()
    for owner,role,kind in product(seeds,('begin','end'),('FF','IRQ','normal')):
        if kind=='normal' and role=='begin':
            continue
        pair = [prepare(seed,role,MODES[0]) for seed in seeds[owner]]
        if kind=='normal':
            for c in pair:
                run(c,lambda z:z.memory[0x139]==0)
        for c in pair:
            IRQ.interrupt(c,kind,lag,regular)
            run(c,stop(role))
        assert state(pair[0])==state(pair[1]),(owner,role,kind)
        resumes[role,kind] += 1
    assert counts['end','normal'] and all(counts[role,'nested_IRQ'] for role in ('begin','end'))
    assert min(minimum)>0x7a
    return dict(cuts=[[ *key,count] for key,count in sorted(counts.items())],sites=sorted(sites),
                resumed=[[ *key,count] for key,count in sorted(resumes.items())],minimum_SP=minimum,
                lag_PC=lag,normal_PC=regular)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    raw = BASE.read_bytes()
    assert P.sha(raw)==PIN
    assert json.loads(PROFILE.with_name('binding.json').read_text())['ROM_sha256']==PIN
    out.mkdir()
    after,rows = patch(raw,out)
    foreground = whole(raw,after)
    print('Native GameLoop, pause branches and completed-Main ownership passed.',flush=True)
    interrupted = vectors(raw,after)
    refs = (Path(__file__),SOURCE,BASE,PROFILE,PROFILE.with_name('binding.json'),M.KERNEL,
            Path(M.__file__),Path(IRQ.__file__),R/'src/game.s',R/'src/mmc5.s',R/'src/native_helper_pause.s',
            R/'src/rogue_dawn_audio_scheduler_hooks_v5.s')
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),
                 patches=rows,whole_GameLoop=foreground,vectors=interrupted,
                 bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(proof['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
