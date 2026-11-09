"""Reuse the missed right column in Mini's source jump sweep."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_mini_sweep_center_1110 as S
from check_mini_funded_actor_1108_v3 import install, slim_fork
from compose_mini_frame_budget_1108 import check_full_cpu
from measure_mini_kernel_transport_1109 import compile_source, replace_one
from prepare_mini_side_alias_1108 import compare_memory


L, M, N, R = S.L, S.M, S.N, S.R
HOIST = R/'build/mini-sweep-center-1110'
FAMILY = (0,0,255,2,2,255,3,3,255,2,2,255,1,1,255)


def transform(source):
    start = source.index('@notjumpinit:\n')
    air = source.index('@air:\n',start)
    source = source[:start]+'''@notjumpinit:
    ; Reuse the existing 0..14 state gate above. Save the caller's X.
    txa
    pha
    ldx MiniCurrent
    lda @families,x
    bmi @end
    sta MiniFamily
    pla
    tax
    lda MiniFamily
    cmp #2
    beq @ground
    bcs @crouch
'''+source[air:]
    for label,kind in (('ground',2),('crouch',3)):
        source = replace_one(source,f'@{label}:\n    lda #{kind}\n    sta MiniFamily\n',
                             f'@{label}:\n')
    values = ','.join(f'${x:02x}' for x in FAMILY)
    source = replace_one(source,'@end:\n    rts\n\nMiniCrouchInput:',f'''@end:
    pla
    tax
    lda MiniCurrent
    cmp MiniCurrent          ; A and flags from the original equal compare.
    rts
@families:
    .byte {values}

MiniCrouchInput:''')
    source = replace_one(source,'''    sta MiniContacts
@xfinished:
    ; Original jump_state scans right then left even with zero/left motion.
    lda MiniFamily
    cmp #1''','''    sta MiniContacts
    clc                      ; A hit must always run the actual next lane.
@xfinished:
    ; On a miss the equal end-of-row comparison leaves C=1.
    lda MiniFamily
    eor #1                   ; Preserve the hit/miss carry through admission.
'''.rstrip())
    source = replace_one(source,'''    lda #8
    sta MiniMask
    lda MiniLeft
    jmp @xbound
@xcommit:''','''    lda #8
    sta MiniMask
    bcc @leftFull
    ; Mini's live horizontal bounds are always +1 and +6. The projected
    ; subpixel low byte carries their whole-pixel column and half-column.
    lda MiniTemp
    cmp #$20
    bcc @leftReuse
    cmp #$70
    bcc @leftFlip
    cmp #$a0
    bcc @leftReuse
    cmp #$f0
    bcs @leftReuse
@leftFull:
    lda MiniLeft
    jmp @xbound
@leftFlip:
    lda MiniScanX
    eor #8
    sta MiniScanX
@leftReuse:
    ; The immutable runtime flags are 0, $0f and $10, so a same-column
    ; right miss also misses left. Its final Y and query fields are identical.
    lda MiniLeft
    sta MiniBound
@xcommit:''')
    return replace_one(source,'\nMiniToPixel:\n',
                       '\n    .res 6,$ea ; Preserve the shared pixel helper addresses.\nMiniToPixel:\n')


def base_image():
    before,_ = S.original_image()
    proof = json.loads((HOIST/'proof.json').read_text())
    assert M.sha(before)==proof['parent_SHA256']
    raw = install(before,proof['patches'])
    assert M.sha(raw)==proof['expected_memory_only_SHA256']
    for ext in ('bin','s','lbl'):
        p = HOIST/f'kernel.{ext}'
        assert M.sha(p.read_bytes())==proof['bindings'][p.relative_to(R).as_posix()]
    return raw,proof


def source_contract(raw, source):
    # The real cold worker reconstructs D300 from the resident attributes.
    # Bind all four installed resident copies and the exact reconstructed
    # table which both live owners authenticate before any source Step.
    tables = []
    for bank in (119,120,125,127):
        at = 16+8192*bank+0xf36
        data = raw[at:at+256]
        tables.append(bytes((v&3)|(0 if x in (0xc2,0xc3) else
                      60 if v&3==1 else 64 if x==0x26 else 0) for x,v in enumerate(data)))
    assert len(set(tables))==1
    assert M.sha(tables[0])=='aec04d8e6465b5ba04b09af9c49beb7b49e9471f84127e6845de15f0c331f73a'
    assert Counter(v>>2 for v in tables[0])=={0:199,15:56,16:1}
    assert source.count('    sta MiniLeft\n')==source.count('    sta MiniRight\n')==0
    assert source.count(' sta MiniLeft\n')==source.count(' sta MiniRight\n')==1
    assert ' lda #1\n sta MiniReady\n sta MiniLeft\n sta MiniTop\n lda #6\n sta MiniRight\n' in source
    return tables[0]


def images(output):
    raw,proof = base_image()
    source = (HOIST/'kernel.s').read_text()
    attrs = source_contract(raw,source)
    code,labels = compile_source(output,transform(source),L.CONFIG)
    assert len(code)==5120 and labels==proof['labels'],(len(code),labels)
    world_end = labels['MiniWorldEnd']-0xa000
    assert raw[L.CODE+world_end:L.CODE+5120]==code[world_end:]
    cookie = bytes.fromhex(M.sha(code+raw[L.CODE+5120:L.CODE+7168]))[:13]
    patches = [L.patch(raw,L.CODE,code,'existing five Mini source code pages'),
               L.patch(raw,L.COOKIE+3,cookie,'existing Mini payload digest')]
    return raw,install(raw,patches),patches,labels,attrs


def tile_observations(rows, *, removed=False):
    kept, removed_count = [], 0
    for entry, result in zip(rows[::2],rows[1::2],strict=True):
        assert entry[0]=='entry' and result[0]=='return'
        if removed and entry[2][13]==2:  # MiniAxis=2 is the second X lane.
            removed_count += 1
        else:
            kept.extend((entry,result))
    return kept,removed_count


def measure(before,after,labels,attributes):
    old,new = L.bundles(before,after)
    seeds = [L.fixture(image,0,False,False) for image in (old,new)]
    assert all(m.ram[2][0x1300:0x1400]==attributes for m in seeds)
    stats, summary = Counter(), {}
    cases = [('geometry',13,(240*16)+lo,159*16,0,-6144,0,0,0,0) for lo in range(256)]
    cases += [('tiles',13,((496+n)*16)+9,y*16,vx,-6144,keys,tier,tile,0)
              for n,y,(vx,keys),(tier,tile) in product(
                  (1,5,8,10,14,15),(15,24,31,32,159,235,248,256),
                  ((0,0),(5602,0xc1),(-5602,0xc2)),
                  ((0,0),(0,0x54),(1,0x26),(1,0xc2),(1,0xc3),(1,0x54)))]
    cases += [('state',state,1511*16+11,159*16,0,-6144,0xc1,0,0,attached)
              for state,attached in product(range(256),(0,1,255))]
    for kind,state,x,y,vx,vy,keys,tier,tile,attached in cases:
        pair = [slim_fork(m) for m in seeds]
        for m in pair:
            S.step_input(m,state,x,y,vx,vy,keys,tier,tile)
            m.ram[2][0x229] = attached
        a,b = [S.source_step(m,labels) for m in pair]
        case = (kind,state,x,y,vx,keys,tier,tile,attached)
        assert a[0]==b[0],(case,a[0],b[0])
        reused = len(a[1])>len(b[1])
        kept, removed = tile_observations(a[1],removed=reused)
        assert kept==b[1],(case,a[1],b[1])
        if kind=='geometry':
            assert reused==((x&255)<0xa0 or (x&255)>=0xf0),case
        compare_memory(*pair,ram_exclusions=S.MASKS)
        assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b],case
        stats[kind,removed] += 1
        limits = summary.setdefault((kind,removed),[a[2]-b[2],a[2]-b[2]])
        limits[0] = min(limits[0],a[2]-b[2]); limits[1] = max(limits[1],a[2]-b[2])
    return [dict(group=k[0],removed_reads=k[1],cases=stats[k],cycles_saved=v)
            for k,v in sorted(summary.items())]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    args.output.mkdir(exist_ok=True)
    old,new,patches,labels,attrs = images(args.output)
    steps = measure(old,new,labels,attrs)
    print(json.dumps(steps),flush=True)
    whole = check_full_cpu(old,new,S.MASKS)
    refs = (Path(__file__),Path(S.__file__),HOIST/'proof.json',HOIST/'kernel.s',HOIST/'kernel.bin',
            L.CONFIG,R/'tools/reference/mini_fireball_art_1108.s',
            *(args.output/f'kernel.{ext}' for ext in ('bin','lbl','s')))
    q = dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=M.sha(old),
             expected_memory_only_SHA256=M.sha(new),kernel_bytes=5120,labels=labels,
             patches=patches,steps=steps,whole_GameCore=whole,
             exact_runtime_attribute_SHA256=M.sha(attrs),
             bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ('patches','bindings','labels')}),flush=True)


if __name__=='__main__':
    main()
