"""Reduce redundant Mini source-step instructions while preserving the native ABI."""

import argparse
from collections import Counter
from itertools import groupby, product
import json
from pathlib import Path

import check_mini_projection_reuse_1110 as P
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork


L, M, N, R, S = P.L, P.M, P.N, P.R, P.S
BASE = R/'build/mini-box-transport-native-1110/candidate.nes'
PIN = '03c0cfe6d4562f6b7970199ce2d6ffa6f2f0f905a8cb8425945add6fcb71585d'
KERNEL = R/'build/mini-projection-reuse-1110/kernel.s'
SOURCE = R/'tools/reference/mini_step_alu_1110.inc'


def transform(original):
    units = dict(chunk.split('\n',1) for chunk in SOURCE.read_text().split('\n; === ')[1:])
    text = original

    def replace_between(start,end,new):
        nonlocal text
        assert text.count(start)==text.count(end)==1
        lo,hi=text.index(start),text.index(end)
        assert lo<hi
        text=text[:lo]+new.rstrip()+'\n'+text[hi:]

    replace_between('    lda #0\n    sta buttons\n    sta ybuttons\n',
                    '    lda #7\n    sta anim\n',units['pad'])
    replace_between('@unattached:\n','    ; Reuse the existing 0..14 state gate above.',units['states'])
    text=P.replace_one(text,'@air:\n    jsr MiniCrouchInput\n    lda MiniFamily\n    sta ymode',
                       '@air:\n    sta ymode\n    jsr MiniCrouchInput')
    lo,hi=text.index('MiniAddSigned:\n'),text.index('MiniSnap:\n')
    signed=text[lo:hi]
    replace_between('MiniAddAligned:\n','MiniSnap:\n',units['aligned'])
    text=P.replace_one(text,'MiniCrouchInput:\n',signed+units['step_pad']+'\nMiniCrouchInput:\n')

    text=P.replace_one(text,'MiniToPixel:\n    lda MiniCoord+1\n','MiniToPixel:\n')
    text=P.replace_one(text,'MiniHeadEvent:\n','    .res 3,$ea\nMiniHeadEvent:\n')
    for entry,variable,indent in (('MiniTempPixel','MiniTemp','    '),('MiniHostPixelX','MiniX',' '),
                                   ('MiniHostPixelY','MiniY',' ')):
        old=(f'{entry}:\n{indent}lda {variable}\n{indent}sta MiniCoord\n{indent}lda {variable}+1\n'
             f'{indent}sta MiniCoord+1\n{indent}jmp MiniToPixel\n')
        text=P.replace_one(text,old,old.replace(f'{indent}sta MiniCoord+1\n','')+f'{indent}.res 3,$ea\n')

    replace_between('MiniNativeTile:\n','MiniNativeTileEnd:\n',units['tile'])
    return text


def build(output):
    raw=BASE.read_bytes()
    assert M.sha(raw)==PIN
    old=KERNEL.with_suffix('.bin').read_bytes()
    source=KERNEL.read_text()
    projection=json.loads(KERNEL.with_name('proof.json').read_text())
    assert projection['passed'] and projection['bindings'][KERNEL.relative_to(R).as_posix()]==M.sha(KERNEL.read_bytes())
    assert len(old)==5120 and raw[L.CODE:L.CODE+5120]==old
    assert raw[L.COOKIE:L.COOKIE+16]==bytes((167,41,1))+digest(raw[L.CODE:L.CODE+7168])
    rebuilt,labels=P.compile_source(output,source,L.CONFIG)
    assert rebuilt==old and labels==projection['labels']
    new,updated=P.compile_source(output,transform(source),L.CONFIG)
    assert len(new)==len(old) and updated==labels,(len(new),updated)
    changed=[]
    for different,run_offsets in groupby(range(5120),key=lambda i:old[i]!=new[i]):
        if different:
            indices=list(run_offsets)
            changed.append((indices[0],indices[-1]+1))
    allowed=((0xa3e5,0xa56d),(0xaac7,0xaae0),(0xab70,0xabc2),
             (0xacbf,0xad3a),(0xb194,0xb1b2))
    assert all(any(a-0xa000<=lo<hi<=b-0xa000 for a,b in allowed) for lo,hi in changed),changed
    patches=[L.patch(raw,L.CODE+lo-0xa000,new[lo-0xa000:hi-0xa000],
                     'Mini source arithmetic or tile query') for lo,hi in allowed]
    cookie=digest(new+raw[L.CODE+5120:L.CODE+7168])
    patches.append(L.patch(raw,L.COOKIE+3,cookie,'authenticated Mini payload digest'))
    successor=install(raw,patches)
    assert successor[L.CODE:L.CODE+5120]==new
    return raw,successor,labels,patches,allowed,changed


def digest(payload):
    return bytes.fromhex(M.sha(payload))[:13]


def invoke(m,pc,stop=0x5b00,p=0x61):
    cpu=N.NesMPU(memory=m,pc=pc)
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=53,11,29,p,224
    cpu.stPushWord(0x5aff)
    run(cpu,lambda c:c.pc==stop)
    return registers(cpu),cpu.processorCycles


def exact_cold(raw,candidate,changed):
    machines=[]
    attributes=P.J.source_contract(raw,KERNEL.read_text())
    for image in (raw,candidate):
        m=N.fresh(M.bundle(image))
        N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,
              DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
        result=N.invoke(m,'MiniScene')
        cookie=image[L.COOKIE:L.COOKIE+16]
        assert bytes(m.ram[3][:5120])==image[L.CODE:L.CODE+5120]
        assert bytes(m.ram[2][0x1000:0x1300])==image[L.CODE+5120:L.CODE+5120+0x300]
        assert bytes(m.ram[2][0x1300:0x1400])==attributes
        assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in (2,3))
        assert m.ram[2][0x300]==1 and result['P']&1
        machines.append((m,result))
    assert machines[0][1]==machines[1][1]
    masks={2:[(0x1fe3,0x1ff0)],3:[*changed,(0x1fe3,0x1ff0)]}
    P.compare_memory(*(m for m,_ in machines),ram_exclusions=masks)
    return dict(MiniScene=machines[1][1],cookie=cookie.hex(),
                runtime_attribute_SHA256=M.sha(attributes)),masks


def inputs(seeds,raw,candidate,labels,masks):
    stops=[]
    for image in (raw,candidate):
        code=image[L.CODE:L.CODE+5120]
        sig=bytes.fromhex('a9078d06c2ad28c28d40c2c90f')
        assert code.count(sig)==1
        # The original next instruction overwrites A/NZ before any reader.
        stops.append(0xa000+code.index(sig)+2)
    stats=Counter()
    for held,previous,p in product(range(256),(0,0x55,0xaa,0xff),(0x20,0x61,0x35,0xf0)):
        pair=[slim_fork(seed) for seed in seeds]
        outcomes=[]
        for m,stop in zip(pair,stops,strict=True):
            ram=m.ram[2]
            ram[0x248:0x24a]=bytes((held,previous))
            outcomes.append(invoke(m,labels['MiniStep'],stop,p))
            assert ram[0x204]==((held>>1)&1)|((held&1)<<1)|((held&0x40)>>4)
            assert ram[0x225]==(held>>7)|((held&8)>>2)
            assert ram[0x24a]==(held&~previous)
        assert outcomes[0][0]==outcomes[1][0],(held,previous,p,outcomes)
        P.compare_memory(*pair,ram_exclusions=masks)
        stats[outcomes[0][1]-outcomes[1][1]]+=1
    return sorted(stats.items())


def tiles(seeds,labels,masks):
    stats=Counter()
    for raw_tile,page,(x,y),p in product(range(256),(0,1,255),
                ((0,31),(15,32),(16,47),(31,239),(255,240),(255,256)),(0x61,0x20)):
        pair=[slim_fork(seed) for seed in seeds]
        outcomes=[]
        for m in pair:
            ram=m.ram[2]
            S.u16(ram,0x2e0,page*256+x)
            S.u16(ram,0x2e2,y)
            ram[0x2e4:0x2ea]=b'\xa5'*6
            m[0x300:0x4a0]=bytes([raw_tile])*416
            outcomes.append(invoke(m,labels['MiniNativeTile'],p=p))
        assert outcomes[0][0]==outcomes[1][0],(raw_tile,page,x,y,p,outcomes)
        P.compare_memory(*pair,ram_exclusions=masks)
        stats[outcomes[0][1]-outcomes[1][1]]+=1
    return sorted(stats.items())


def steps(seeds,labels,masks):
    boundaries=[(state,x*16+fraction,y*16+fraction,vx,vy,pad,tier,tile,0)
                for state,(x,y),fraction,(vx,vy,pad),(tier,tile) in product(
                    (1,4,7,10,13),((0,0),(15,15),(255,31),(256,32),(511,159),
                    (694,164),(767,239),(768,240),(1551,255),(1536,256),(4095,4095)),(0,15),
                    ((-5602,-6144,0xc2),(5602,-6144,0xc1),(5602,8192,0x41),(0,8192,0)),
                    ((0,0),(1,0x54),(1,0x26),(1,0xc3)))]
    states=[(state,1511*16+11,159*16+7,5602,-6144,0xc1,1,0x54,attached)
            for state,attached in product(range(256),(0,1,255))]
    counts=Counter()
    for case in boundaries+states:
        state,x,y,vx,vy,pad,tier,tile,attached=case
        pair=[slim_fork(m) for m in seeds]
        for m in pair:
            S.step_input(m,state,x,y,vx,vy,pad,tier,tile)
            ram=m.ram[2]
            ram[0x229]=attached
            left=max(0,(x>>4)-120)
            S.u16(ram,0x258,left*16)
            S.u16(ram,0x25a,min(4095,left+240)*16+15)
        before,after=[S.source_step(m,labels) for m in pair]
        assert before[:2]==after[:2],(case,before[:2],after[:2])
        P.compare_memory(*pair,ram_exclusions=masks)
        assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b],case
        counts[before[2]-after[2]]+=1
    return sorted(counts.items())


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args()
    out=args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw,candidate,labels,patches,spans,changed=build(out)
    print('Exact linked source footprint',len(changed),M.sha(candidate),flush=True)
    cold,masks=exact_cold(raw,candidate,changed)
    seeds=[L.fixture(b,0,False,False) for b in L.bundles(raw,candidate)]
    for seed in seeds:
        seed.raw_page(1,3)
        seed.raw_page(2,2)
        N.put(seed,CurrentBank=3,CurrentBankC=2)
    pad=inputs(seeds,raw,candidate,labels,masks)
    print('Pad cycles',pad,flush=True)
    tile=tiles(seeds,labels,masks)
    print('Tile cycles',tile,flush=True)
    step=steps(seeds,labels,masks)
    whole=P.check_full_cpu(raw,candidate,masks)
    refs=(Path(__file__),BASE,SOURCE,KERNEL,KERNEL.with_suffix('.bin'),L.CONFIG,
          *(out/f'kernel.{ext}' for ext in ('s','bin','lbl')))
    proof=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
               expected_memory_only_SHA256=M.sha(candidate),Mini_kernel_bytes=5120,labels=labels,
               patches=patches,code_spans=spans,exact_cold=cold,exact_changed_code=changed,
               pad=pad,tile=tile,step=step,whole_GameCore=whole,
               bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(step=step,whole_GameCore=whole)),flush=True)


if __name__=='__main__':
    main()
