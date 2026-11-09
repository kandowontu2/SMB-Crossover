"""Share the base coordinate of each Mini collision sweep without caching state."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_mini_jump_lane_reuse_1110 as J
import check_mini_sweep_center_1110 as S
from check_mini_funded_actor_1108_v3 import install, slim_fork
from compose_mini_frame_budget_1108 import check_full_cpu
from measure_mini_kernel_transport_1109 import compile_source, replace_one
from prepare_mini_audio_frame_token_native_1110 import EXPECTED as PIN
from prepare_mini_side_alias_1108 import compare_memory


L,M,N,R = J.L,J.M,J.N,J.R
BASE = R/'build/mini-audio-token-native-1110/candidate.nes'
KERNEL = R/'build/mini-jump-lane-reuse-1110/kernel.s'
BASE_PROOF = KERNEL.with_name('proof.json')


def transform(source):
    for bound,coordinate in (('MiniBottom','Y'),('MiniSaved','X')):
        original = f'''    lda {bound}
    jsr MiniAddAligned
    lda MiniCoord
    sta MiniEnd
    lda MiniCoord+1
    sta MiniEnd+1
    jsr MiniHostPixel{coordinate}
'''
        replacement = f'''    ; This far bound is unsigned. Keep the base pixel for the near bound.
    lda MiniCoord
    clc
    adc {bound}
    and #$f8
    sta MiniEnd
    lda MiniCoord+1
    adc #0
    sta MiniEnd+1
    .byte $ea                 ; Keep both original continuations fixed.
'''
        source = replace_one(source,original,replacement)
    return source


def old_image():
    before = BASE.read_bytes()
    assert M.sha(before)==PIN
    source = KERNEL.read_text()
    prev = json.loads(BASE_PROOF.read_text())
    assert prev['passed'] and prev['bindings'][KERNEL.relative_to(R).as_posix()]==M.sha(KERNEL.read_bytes())
    old = KERNEL.with_suffix('.bin').read_bytes()
    assert len(old)==5120 and old==before[L.CODE:L.CODE+5120]
    assert before[L.COOKIE:L.COOKIE+3]==bytes((167,41,1))
    assert before[L.COOKIE+3:L.COOKIE+16]==bytes.fromhex(M.sha(before[L.CODE:L.CODE+7168]))[:13]
    # MiniInit clears the owned world scratch and the authenticated Fresh leaf
    # immediately publishes bottom=7 and right=6. The right span adds 3 only
    # for the original left-running threshold. Signed top/left logic stays.
    assert source.count(' sta MiniBottom\n')==source.count(' sta MiniRight\n')==1
    assert ' lda #6\n sta MiniRight\n lda #7\n sta MiniBottom' in source
    assert 'adc #3\n    sta MiniSaved\n@rightbound:' in source
    attrs = J.source_contract(before,source)
    return before,source,old,prev,attrs


def build(output):
    raw,source,old,prev,attrs = old_image()
    reproduced,labels = compile_source(output,source,L.CONFIG)
    assert reproduced==old and labels==prev['labels']
    new,moved = compile_source(output,transform(source),L.CONFIG)
    assert moved==labels and len(new)==len(old)
    signatures = ('ad57c22082abad72c28d78c2ad73c28d79c220a3b1',
                  'ad7ec22082abad72c28d78c2ad73c28d79c22094b1')
    spans,patches = [],[]
    staged = bytearray(old)
    for sig in signatures:
        key = bytes.fromhex(sig)
        assert old.count(key)==1
        start = old.index(key)
        spans.append((0xa000+start,0xa000+start+21))
        chunk = new[start:start+21]
        assert chunk[0:4]==bytes.fromhex('ad72c218') and chunk[-1]==0xea
        staged[start:start+21] = chunk
        patches.append(L.patch(raw,L.CODE+start,chunk,'existing Mini far bound projection'))
    assert staged==new
    cookie = bytes.fromhex(M.sha(new+raw[L.CODE+5120:L.CODE+7168]))[:13]
    patches.append(L.patch(raw,L.COOKIE+3,cookie,'existing Mini payload digest'))
    return raw,install(raw,patches),labels,spans,patches,attrs


def carry_arithmetic():
    for value,bound in product(range(65536),(0,6,7,9)):
        low = (value&255)+bound
        high = ((value>>8)+(low>>8))&255
        assert (high<<8)|(low&248)==((value+bound)&65528)
    return 65536*4


def differential(raw,candidate,labels,attrs):
    seeds = [L.fixture(b,0,False,False) for b in L.bundles(raw,candidate)]
    assert all(m.ram[2][0x1300:0x1400]==attrs for m in seeds)
    geometry = [('boundary',state,x*16+fraction,y*16+fraction,vx,vy,pad,tier,tile,0)
                for state,(x,y),fraction,(vx,vy,pad),(tier,tile) in product(
                    (1,4,7,10,13),((0,0),(15,15),(255,31),(256,32),(511,159),
                    (694,164),(767,239),(768,240),(1551,255),(1536,256),(4095,4095)),(0,15),
                    ((-5602,-6144,0xc2),(5602,-6144,0xc1),(5602,8192,0x41),(0,8192,0)),
                    ((0,0),(1,0x54),(1,0x26),(1,0xc3)))]
    states = [('state',state,1511*16+11,159*16+7,5602,-6144,0xc1,1,0x54,attached)
              for state,attached in product(range(256),(0,1,255))]
    counts = Counter()
    for case in geometry+states:
        group,state,x,y,vx,vy,pad,tier,tile,attached = case
        pair = [slim_fork(m) for m in seeds]
        for m in pair:
            S.step_input(m,state,x,y,vx,vy,pad,tier,tile)
            ram = m.ram[2]
            ram[0x229] = attached
            left = max(0,(x>>4)-120)
            S.u16(ram,0x258,left*16)
            S.u16(ram,0x25a,min(4095,left+240)*16+15)
        before,after = [S.source_step(m,labels) for m in pair]
        assert before[:2]==after[:2],(case,before[:2],after[:2])
        compare_memory(*pair,ram_exclusions=S.MASKS)
        assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b],case
        saving = before[2]-after[2]
        assert saving in (0,126,252,378),(case,saving)
        counts[group,saving] += 1
    assert counts['state',0] and all(counts['boundary',saving] for saving in (126,252,378)),counts
    return [[group,saving,n] for (group,saving),n in sorted(counts.items())]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R/'build') and not (output/'proof.json').exists()
    output.mkdir(exist_ok=True)
    raw,candidate,labels,spans,patches,attrs = build(output)
    boundaries = differential(raw,candidate,labels,attrs)
    whole = check_full_cpu(raw,candidate,S.MASKS)
    q = dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
        expected_memory_only_SHA256=M.sha(candidate),source_preimage_reproduced=True,
        Mini_kernel_bytes=5120,patches=patches,labels=labels,Mini_sweep_CPU_spans=spans,
        carry_equivalence_cases=carry_arithmetic(),actual_MiniStep=boundaries,whole_GameCore=whole,
        exact_runtime_attribute_SHA256=M.sha(attrs),
        bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes()) for p in
                  (Path(__file__),KERNEL,BASE_PROOF,KERNEL.with_suffix('.bin'),L.CONFIG,
                   *(output/f'kernel.{ext}' for ext in ('s','bin','lbl')))})
    (output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('expected_memory_only_SHA256','Mini_sweep_CPU_spans',
                                      'actual_MiniStep','whole_GameCore')}),flush=True)


if __name__=='__main__':
    main()
