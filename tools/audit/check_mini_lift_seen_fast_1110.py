"""Qualify the authenticated Mini no-op lift scan on exact 90a8."""

import argparse
from collections import Counter
from itertools import groupby, product
import json
from pathlib import Path

import check_mini_step_edges_1110 as Edges
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from measure_mini_kernel_transport_1109 import compile_source, replace_one


A, L, M, N, R = Edges.Alu, Edges.L, Edges.M, Edges.N, Edges.R
BASE = R/'build/mini-edges-draw-offscreen-native-1110/candidate.nes'
PIN = '90a8ac32d51acd29965a45aa5fd512b0b2d77d1c01b03982b62e6d9bed1d1d82'
KERNEL = R/'build/mini-step-edges-1110/kernel.s'
SOURCE = R/'tools/reference/mini_lift_seen_fast_1110.inc'
ORIGINAL = bytes.fromhex('a002ad1e07d9fabbd00aad2007f9fdbbc95090048810eb60ad0cc3397daed0f7'
                         'b9fdbb09208d6a014c6eae020203109040')
THUNK = bytes.fromhex('a99c8d6c01a9b38d6d01a9bd4c5a01010204')
CALL, RETURN = 0xafc9,0xafcc


def transform(text):
    text = replace_one(text,'    lda vel+1\n    jsr MiniAddDeltaX\n','    jsr integrate\n')
    lo = text.index('@integrate:\n',text.index('MiniGroundGravity:\n'))
    hi = text.index('MiniGroundCollisions:\n',lo)
    section = text[lo:hi]
    assert 'jmp MiniClampDeltaY' in section and 'jmp MiniClampDeltaX' in section
    text = text[:lo]+'@integrate:\n    jmp y_integrate\n\n'+text[hi:]
    lo = text.index('MiniClampDeltaY:\n')
    hi = text.index('MiniTempPixel:\n',lo)
    assert 'MiniClamp:' in text[lo:hi] and 'sta delta+1,x' in text[lo:hi]
    text = text[:lo]+text[hi:]
    text = replace_one(text,'MiniClampDeltaX:\n    ldx #0\n    jmp MiniClamp\n    .res 1,$ea\n',
                       '    .res 6,$ea\n')
    text = replace_one(text,' lda #$98\n jsr MiniFarCall\n@epoch:',
                       ' lda #$98\n jsr MiniLiftSeenFast\n@epoch:')
    return replace_one(text,'    .res $8c5-(*-MiniStep),$ea\n',
                       SOURCE.read_text()+'\n    .res $8c5-(*-MiniStep),$ea\n')


def build(out):
    raw = BASE.read_bytes()
    assert M.sha(raw)==PIN
    for pc,expected in ((0xbbcf,ORIGINAL),(0xae6e,THUNK)):
        at = 16+8192*24+(pc&8191)
        assert raw[at:at+len(expected)]==expected
    source,old = KERNEL.read_text(),KERNEL.with_suffix('.bin').read_bytes()
    old_proof = json.loads(KERNEL.with_name('proof.json').read_text())
    assert old_proof['passed'] and old_proof['bindings'][str(KERNEL.resolve())]==M.sha(KERNEL.read_bytes())
    assert raw[L.CODE:L.CODE+5120]==old and raw[L.COOKIE:L.COOKIE+16]==bytes((167,41,1))+A.digest(raw[L.CODE:L.CODE+7168])
    rebuilt,labels = compile_source(out,source,L.CONFIG)
    assert rebuilt==old and labels==old_proof['labels']
    new,new_labels = compile_source(out,transform(source),L.CONFIG)
    assert len(new)==len(old)==5120 and new_labels==labels
    assert old[CALL-0xa000:RETURN-0xa000]==bytes.fromhex('205a01')
    assert new[CALL-0xa000]==0x20
    worker = int.from_bytes(new[CALL-0xa000+1:RETURN-0xa000],'little')
    assert new[worker-0xa000:worker-0xa000+5]==bytes.fromhex('ad0cc3c907')
    changed = []
    for different,group in groupby(range(5120),key=lambda i:old[i]!=new[i]):
        if different:
            group = list(group)
            changed.append((group[0],group[-1]+1))
    patches = [L.patch(raw,L.CODE+lo,new[lo:hi],'existing Mini source executable') for lo,hi in changed]
    cookie = A.digest(new+raw[L.CODE+5120:L.CODE+7168])
    patches.append(L.patch(raw,L.COOKIE+3,cookie,'authenticated Mini payload digest'))
    return raw,install(raw,patches),labels,patches,changed,worker


def helper_call(m,flags,x,y):
    m[0x5115] = 3
    m[0x5116] = 2
    N.put(m,CurrentBank=3,CurrentBankC=2)
    # Establish the exact HostMain packet immediately before the real JSR.
    m[0x16a] = 0x75
    m[0x16c] = 0xcf
    m[0x16d] = 0xbb
    m.writes.clear()
    m.ram_writes.clear()
    c = N.NesMPU(memory=m,pc=CALL)
    c.a,c.x,c.y,c.p,c.sp = 0x98,x,y,flags,224
    run(c,lambda z:(z.pc,z.sp)==(RETURN,224))
    return c


def dispatch(seeds,masks):
    counts = Counter()

    def check(right,seen,valid_scene,full,flags):
        pair = [slim_fork(m) for m in seeds]
        cpus = []
        for m in pair:
            L.camera(m,right)
            N.put(m,AreaAddrsLOffset=5 if valid_scene else 0,WorldNumber=0,LevelNumber=0)
            m.ram[2][0x30c] = seen
            for slot in range(6):
                m[M.address(m.bundle,'Enemy_Flag')+slot] = int(full)
                m[M.address(m.bundle,'Enemy_ID')+slot] = 6
            cpus.append(helper_call(m,flags,17,99))
        old,new = cpus
        assert registers(old)==registers(new) and live_stack(old)==live_stack(new),(right,seen,valid_scene,full,flags)
        A.P.compare_memory(*pair,ram_exclusions=masks)
        assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b]
        old_maps,new_maps = [[v for address,v in m.writes if address==0x5115] for m in pair]
        hardware = lambda m:[(at,v) for at,v in m.writes if 0x2000<=at<0x4020 or 0x5100<=at<=0x5206]
        if seen==7:
            assert old_maps==[0x98,3] and not new_maps
            assert [(at,v) for at,v in hardware(pair[0]) if at!=0x5115]==hardware(pair[1])
        else:
            assert old_maps==new_maps and hardware(pair[0])==hardware(pair[1])
        assert pair[0].ram_writes==pair[1].ram_writes
        counts['fast' if seen==7 else 'legacy',old.processorCycles-new.processorCycles] += 1

    for page,low,seen in product((2,3),range(256),range(8)):
        check(page*256+low,seen,False,False,(0x21,0x65,0xa0,0xe4)[low&3])
    for right,seen,full,flags in product((527,528,607,608,655,656,735,736,831,832,911,912),
                                        (0,1,2,4,7),(False,True),(0x21,0x65)):
        check(right,seen,True,full,flags)
    return [[mode,cycles,n] for (mode,cycles),n in sorted(counts.items())]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw,after,labels,patches,changed,worker = build(out)
    print('Exact linked Mini helper source',hex(worker),M.sha(after),flush=True)
    cold,masks = A.exact_cold(raw,after,changed)
    seeds = [L.fixture(b,0,False,False) for b in L.bundles(raw,after)]
    calls = dispatch(seeds,masks)
    print('Exact manager call comparison',calls,flush=True)
    step = A.steps(seeds,labels,masks)
    edges = Edges.check_steps(seeds,labels,masks)
    core = A.P.check_full_cpu(raw,after,masks)
    loop = Edges.Composed.whole_loop(raw,after,masks)
    refs = (Path(__file__),SOURCE,BASE,KERNEL,KERNEL.with_suffix('.bin'),KERNEL.with_name('proof.json'),L.CONFIG,
            *(out/f'kernel.{ext}' for ext in ('s','bin','lbl')))
    proof = dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
                 expected_memory_only_SHA256=M.sha(after),Mini_kernel_bytes=5120,labels=labels,
                 patches=patches,exact_changed_code=changed,exact_cold=cold,call=[CALL,RETURN],worker=worker,
                 helper_call= calls,step=step,forced_edges_and_deltas=edges,whole_GameCore=core,whole_GameLoop=loop,
                 bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(whole_GameCore=core,whole_GameLoop=loop)),flush=True)


if __name__=='__main__':
    main()
