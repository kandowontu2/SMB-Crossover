"""Qualify Mini's duplicate-clamp and stationary-axis removal on exact 991b."""

import argparse
from collections import Counter
from itertools import groupby, product
import json
from pathlib import Path

import check_mini_step_alu_1110 as Alu
import prepare_mini_step_scroll_weapon_native_1110 as Composed
from check_mini_funded_actor_1108_v3 import install, slim_fork
from measure_mini_kernel_transport_1109 import compile_source, replace_one


L, M, N, R, S = Alu.L, Alu.M, Alu.N, Alu.R, Alu.S
BASE = R/'build/mini-step-scroll-weapon-native-1110/candidate.nes'
PIN = '991b4cd1033890aaa7dc0fa773dc167496fd0937bc449c8a3a209709f2a6c318'
KERNEL = R/'build/mini-step-alu-1110/kernel.s'
FRAGMENTS = R/'tools/reference/mini_step_edges_1110.inc'
CALLS = {0xb0cb:('2094b1','2099b1'),0xb123:('2070ab','207aab'),
         0xb1fd:('2094b1','2099b1'),0xb213:('20a3b1','20a5b1')}
SPANS = ((0xa3e5,0xacaa),(0xaf4d,0xb0b7),(0xb180,0xb1b2),
         *((pc,pc+1) for pc in CALLS))


def transform(source):
    fragments = dict(x.split('\n',1) for x in FRAGMENTS.read_text().split('\n; === ')[1:])
    rewrite = lambda old,new: replace_one(source,old,new)

    # The ported air/ground integrate tails already saturate their respective
    # signed deltas. Only the two small manual integrations need a clamp.
    assert source.count('jsr MiniClampDeltaX') == source.count('jsr MiniClampDeltaY') == 1
    assert source.count('jsr MiniGroundGravity') == 2 and source.count('jsr MiniAddDeltaX') == 1
    source = rewrite('    sta ydelta+1\n    rts\n\nMiniAddDeltaX:',
                     '    sta ydelta+1\n    jmp MiniClampDeltaY\n\nMiniAddDeltaX:')
    source = rewrite('    sta delta+1\n    rts\n\nMiniCollisions:',
                     '    sta delta+1\n    jmp MiniClampDeltaX\n\n'+fragments['stationary'].strip()+'\n\nMiniCollisions:')
    source = rewrite('    jsr ground_x\n    jmp MiniCollisions','    jsr ground_x\n    jmp MiniGroundCollisions')
    source = rewrite('    jsr MiniClampDeltaX\n','')
    source = rewrite('    ; Source actor-collision stage clears both accumulated deltas after Y.',
                     'MiniYAxis:\n    ; Source actor-collision stage clears both accumulated deltas after Y.')
    source = rewrite('    jsr MiniClampDeltaY\n','    ldx #$20                ; Preserve the zero-Y-delta return register.\n')

    signed = 'MiniClampDeltaX:\n    ldx #0\n    jmp MiniClamp\n'
    source = rewrite(signed,'')
    source = rewrite(' jsr MiniHostToSubpixel\n lda MiniCoord\n sta MiniEdgeLeft\n'
                     ' lda MiniCoord+1\n sta MiniEdgeLeft+1\n clc\n adc #15'
                     '                  ; +240 pixels = +3840 subpixels.\n'
                     ' sta MiniEdgeRight+1\n lda MiniCoord\n sta MiniEdgeRight',
                     ' jsr MiniHostToSubpixel\n sta MiniEdgeLeft\n sta MiniEdgeRight\n'
                     ' lda MiniCoord+1\n sta MiniEdgeLeft+1\n clc\n adc #15'
                     '                  ; +240 pixels = +3840 subpixels.\n sta MiniEdgeRight+1')
    source = rewrite('; Mini\'s downward source sweep contacts',signed+'    .res 1,$ea\n\n; Mini\'s downward source sweep contacts')

    # Pool the existing private alignment NOPs without changing public entries.
    source = rewrite('    .res $188-(*-MiniStep),$ea ; Preserve MiniCrouchInput and all later entries.\n','')
    source = rewrite('    .res 6,$ea ; Preserve the shared pixel helper addresses.\n','')
    source = rewrite('    .res $22-(*-MiniAddAligned),$ea\n','')
    assert source.count('    .res 3,$ea\n') == source.count('    .byte $ea                 ; Keep both original continuations fixed.\n') == 2
    source = source.replace('    .res 3,$ea\n','').replace('    .byte $ea                 ; Keep both original continuations fixed.\n','')
    source = rewrite('MiniWorldEnd:\n','    .res $8c5-(*-MiniStep),$ea\nMiniWorldEnd:\n')

    start,end = source.index('MiniHostToSubpixel:\n'),source.index('MiniHostGraphics:\n')
    wrappers = source[source.index('MiniHostPixelX:\n',start):end]
    assert wrappers.count(' .res 3,$ea\n') == 2
    return source[:start]+fragments['to_subpixel'].strip()+'\n'+wrappers.replace(' .res 3,$ea\n','')+' .res 1,$ea\n'+source[end:]


def build(output):
    raw = BASE.read_bytes()
    old = KERNEL.with_suffix('.bin').read_bytes()
    source = KERNEL.read_text()
    assert M.sha(raw)==PIN and len(old)==5120 and raw[L.CODE:L.CODE+5120]==old
    assert raw[L.COOKIE:L.COOKIE+16]==bytes((167,41,1))+Alu.digest(raw[L.CODE:L.CODE+7168])
    old_receipt = json.loads(KERNEL.with_name('proof.json').read_text())
    assert old_receipt['passed'] and old_receipt['bindings'][str(KERNEL.resolve())]==M.sha(KERNEL.read_bytes())
    rebuilt,labels = compile_source(output,source,L.CONFIG)
    assert rebuilt==old and labels==old_receipt['labels']
    new,new_labels = compile_source(output,transform(source),L.CONFIG)
    assert len(new)==len(old) and labels==new_labels,(len(new),new_labels)
    for pc,(preimage,replacement) in CALLS.items():
        i=pc-0xa000
        assert old[i-1:i+2].hex()==preimage and new[i-1:i+2].hex()==replacement,hex(pc)
    changed = []
    for different,offsets in groupby(range(5120),key=lambda i:old[i]!=new[i]):
        if different:
            offsets=list(offsets)
            changed.append((offsets[0],offsets[-1]+1))
    assert all(any(a-0xa000<=lo<hi<=b-0xa000 for a,b in SPANS) for lo,hi in changed),changed
    patches = [L.patch(raw,L.CODE+lo-0xa000,new[lo-0xa000:hi-0xa000],'Mini source step or coordinate projection')
               for lo,hi in SPANS]
    cookie = Alu.digest(new+raw[L.CODE+5120:L.CODE+7168])
    patches.append(L.patch(raw,L.COOKIE+3,cookie,'authenticated Mini payload digest'))
    after = install(raw,patches)
    return raw,after,labels,patches,changed


def check_steps(seeds,labels,masks):
    # X711 is the observed grounded lag cluster. Test it alongside exact
    # high-byte edge equality, forced viewport pushes and signed clamp seeds.
    world = ((711,599,839),(694,582,822),(0,0,240),(255,16,256),
             (256,256,496),(496,256,496),(497,256,496),(128,136,376),
             (4095,3840,4095),(16,0,240))
    samples = ((0,0),(1,0),(127,-127),(128,-128),(-128,128),(255,-255),
               (-255,255),(32767,-32768),(-32768,32767),(0x1234,-0x1234))
    hist = Counter()
    for state,(x,left,right),(dx,dy),nocollide in product(range(15),world,samples,(0,1)):
        pair = [slim_fork(seed) for seed in seeds]
        for m in pair:
            S.step_input(m,state,x*16+15,200*16+15,0,256,0,0,0x54)
            ram = m.ram[2]
            S.u16(ram,0x202,dx)
            S.u16(ram,0x222,dy)
            S.u16(ram,0x258,left*16)
            S.u16(ram,0x25a,right*16+15)
            ram[0x227] = nocollide
        before,after = [S.source_step(m,labels) for m in pair]
        case = state,x,left,right,dx,dy,nocollide
        assert before[:2]==after[:2],(case,before[:2],after[:2])
        Alu.P.compare_memory(*pair,ram_exclusions=masks)
        assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b],case
        hist[state,before[2]-after[2]] += 1
    return [[state,save,n] for (state,save),n in sorted(hist.items())]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw,after,labels,patches,changed = build(out)
    print('Exact linked kernel',M.sha(after),flush=True)
    cold,masks = Alu.exact_cold(raw,after,changed)
    seeds = [L.fixture(b,0,False,False) for b in L.bundles(raw,after)]
    # Retain the existing movement/tile packet checks plus both signed clamp
    # directions and the source-only stationary interior admission.
    steps = Alu.steps(seeds,labels,masks)
    edges = check_steps(seeds,labels,masks)
    core = Alu.P.check_full_cpu(raw,after,masks)
    loop = Composed.whole_loop(raw,after,masks)
    refs = (Path(__file__),FRAGMENTS,BASE,KERNEL,KERNEL.with_suffix('.bin'),KERNEL.with_name('proof.json'),L.CONFIG,
            *(out/f'kernel.{ext}' for ext in ('s','bin','lbl')))
    receipt = dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
                   expected_memory_only_SHA256=M.sha(after),Mini_kernel_bytes=5120,labels=labels,
                   patches=patches,code_spans=SPANS,exact_changed_code=changed,exact_cold=cold,
                   step=steps,forced_edges_and_deltas=edges,whole_GameCore=core,whole_GameLoop=loop,
                   bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(whole_GameCore=core,whole_GameLoop=loop)),flush=True)


if __name__=='__main__':
    main()
