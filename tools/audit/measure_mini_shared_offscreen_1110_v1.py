"""Compare the current shared offscreen arithmetic without emitting a ROM."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import profile_mini_busy_1108_v1 as P
from check_mini_visibility_dispatch_1110_v1 import memory
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork, live_stack


R,N=P.R,P.N
ROM=R/'build/mini-box-terrain-visible-1110/candidate.nes'
PIN='6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
PROFILE=R/'build/mini-final-peak-1110/capture/instruction-sample.json'
SOURCE=R/'tools/reference/mini_shared_offscreen_1110_v1.s'
EXTENTS=((0x8b1a,0x8b60),(0x8b73,0x8bb8),(0x8bc6,0x8bdb))
OLD=(bytes.fromhex('8607a001b91f0738f575850ab91d07f55cbe708bc9003021be718bc901101aa9388509a9088508a50ac509b00c4a4a4a2907c001b0026508aabd608ba607c900d0038810bf60'),
     bytes.fromhex('4cc68beab9c48b38f5bd850aa901f5a4bec18bc9003021bec28bc901101aa9208509a9048508a50ac509b00c4a4a4a2907c001b0026508aabdb88ba607c900d0038810c060'),
     bytes.fromhex('8607a001b5a4c901d001884c778beaeaeaeaeaeaea'))
TABLES={0x8b60:'7f3f1f0f0703010080c0e0f0f8fcfeff070f07',
        0x8bb8:'00080c0e0f07030100040004ff00'}


def offset(pc):
    return 16+126*8192+(pc&8191)


def compose(out,raw):
    assert all(raw[offset(pc):offset(pc)+len(bytes.fromhex(data))]==bytes.fromhex(data)
               for pc,data in TABLES.items())
    assert len(OLD)==len(EXTENTS)
    # The installed outline replaced the unused native DividePDiff body.
    # Only the old entry/stub reach the two private continuation addresses.
    actual={'8bc6':[],'8b77':[]}
    prg=raw[16:16+128*8192]
    for pc,matches in actual.items():
        imm=int(pc,16).to_bytes(2,'little')
        matches.extend(i for i in range(len(prg)-2) if prg[i] in (0x20,0x4c) and prg[i+1:i+3]==imm)
    assert actual=={'8bc6':[offset(0x8b73)-16],'8b77':[offset(0x8bd1)-16]},actual
    with tempfile.TemporaryDirectory(prefix='offscreen-',dir=out) as folder:
        work=Path(folder)
        cfg,obj,binary=(work/f'offscreen.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { X:start=$8b1a,size=$46,file=%O; Y:start=$8b73,size=$68,file=%O; } '
                       'SEGMENTS { OFFSCREEN_X:load=X,type=ro; OFFSCREEN_Y:load=Y,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        data=binary.read_bytes()
    assert len(data)==0x46+0x68
    assert data[0x46+0x45:0x46+0x53]==bytes.fromhex(TABLES[0x8bb8])
    data=data[:0x46+0x45]+data[0x46+0x53:]
    patches=[]
    for (start,end),old in zip(EXTENTS,OLD,strict=True):
        size=end-start
        assert size==len(old)
        patch,data=data[:size],data[size:]
        patches.append(dict(physical_PRG=126,start=start,end_exclusive=end,file_offset=offset(start),
                            old_hex=old.hex(),new_hex=patch.hex()))
    assert not data
    return install(raw,patches),patches


def leaves(images):
    cpus=[]
    for raw in images:
        ram=bytearray(65536)
        ram[0x8000:0xa000]=raw[offset(0x8000):offset(0x8000)+8192]
        cpus.append(N.NesMPU(memory=ram))

    def call(c,pc,x,p):
        c.pc,c.a,c.x,c.y,c.p,c.sp=pc,0x81,x,0x5c,p,252
        c.processorCycles=0
        c.stPushWord(0x5aff)
        run(c,lambda z:(z.pc,z.sp)==(0x5b00,252))
        return registers(c),bytes(c.memory[7:11]),c.processorCycles

    def test(kind,fields,index,p):
        outcomes=[]
        for cpu in cpus:
            mem=cpu.memory
            mem[7:11]=bytes.fromhex('3c7fa584')
            if kind=='Y':
                page,low=fields
                mem[(0xa4+index)&255],mem[(0xbd+index)&255]=page,low
                pc=0x8b73
            else:
                left,lpage,right,rpage,x,page=fields
                mem[0x71d:0x721]=bytes((lpage,rpage,left,right))
                mem[(0x75+index)&255],mem[(0x5c+index)&255]=x,page
                pc=0x8b1a
            outcomes.append(call(cpu,pc,index,p))
        a,b=outcomes
        assert a[:2]==b[:2],(kind,fields,index,p,a,b)
        savings[kind,a[-1]-b[-1]]+=1

    savings=Counter()
    for page,y in product(range(256),range(256)):
        test('Y',(page,y),(page+y)%29,(0x20,0x25,0x63,0xe9)[y&3])
    for left,lpage,x,delta in product((0,1,7,8,16,63,128,192,248,255),
                                      (0,2,127,255),range(256),(-2,-1,0,1,2,127,128)):
        right=(left-1)&255
        rpage=(lpage+int(left!=0))&255
        test('X',(left,lpage,right,rpage,x,(lpage+delta)&255),(x+delta)%29,(0x21,0x64,0xad)[x%3])
    # Independent edges cover one-way parser/camera transients as well as a
    # conventional 256-pixel viewport, including signed-page wrap.
    for left,lpage,right,rpage,x in product((0,64,255),(0,1,128,255),(0,23,200,255),
                                           (0,1,127,255),(0,23,55,56,127,128,255)):
        test('X',(left,lpage,right,rpage,x,((lpage+rpage)//2)&255),x%29,0xe5)
    assert not any(delta<0 for _,delta in savings)
    return dict(savings_histogram=[[*k,v] for k,v in sorted(savings.items())],cases=sum(savings.values()))


def full(images):
    rows=[]
    for actors,parser in ((0,False),(2,False),(4,False),(4,True),(6,True)):
        pair=[P.fixture(b,actors,False,parser) for b in images]
        deltas=[]
        for age in range(24):
            keys=0 if age<8 else 1 if age<16 else 129
            regs=[]
            for m in pair:
                N.put(m,FrameCounter=(N.get(m,'FrameCounter')+1)&255,SavedJoypadBits=keys,
                      SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                regs.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
            assert memory(pair[0])==memory(pair[1]),(actors,parser,age)
            assert all(regs[0][n]==regs[1][n] for n in 'AXYP'),(actors,parser,age)
            deltas.append(regs[0]['CPU']-regs[1]['CPU'])
        rows.append(dict(actors=actors,parser=parser,updates=len(deltas),minimum_saved=min(deltas),maximum_saved=max(deltas)))
    assert all(row['minimum_saved']>0 for row in rows)
    return rows


def actual_peak():
    profile=json.loads(PROFILE.read_text())
    scene=profile['scene']
    assert (scene['frame'],scene['x'],scene['cycles'])==(1971,1511,30801)
    fg=profile['foreground_opcodes']
    def old(pc):
        return fg.get(f'126:{pc:04x}',0)
    x_edges=old(0x8b1e)//4
    x_neg=old(0x8b30)-2*x_edges
    x_pos=old(0x8b37)-2*(x_edges-x_neg)
    x_zero=x_edges-x_neg-x_pos
    x_far=old(0x8b45)-2*x_zero
    assert (x_edges,x_neg,x_pos,x_far)==(10,5,0,5) and old(0x8b47)==0
    # Negative high uses BMI/LDX (2 cycles saved). Zero high with a distant
    # low difference uses the cheaper sign/zero test and direct comparison
    # before restoring its table index (6 cycles saved).
    x_saved=2*x_neg+6*x_far
    # Every reached Y call uses the existing unit-1 bypass. All four low
    # differences are distant and use the bottom-edge table default.
    y_calls=old(0x8b73)//3
    assert y_calls==4 and old(0x8bd0)==2*y_calls and old(0x8b9f)==0
    y_saved=25*y_calls
    return dict(frame=scene['frame'],world_x=scene['x'],baseline_foreground=scene['cycles'],
                X_edges=x_edges,X_negative_high=x_neg,X_zero_high_far_low=x_far,Y_unit1_far=y_calls,
                X_derived_savings=x_saved,Y_derived_savings=y_saved,combined_derived_savings=x_saved+y_saved,
                projected_foreground=scene['cycles']-x_saved-y_saved,
                scope='Derived from exact incumbent Mesen foreground opcode/branch costs and qualified instruction substitutions. Candidate physical timing is separate.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN
    image,patches=compose(args.output,raw)
    leaves_result=leaves((raw,image))
    print('Exact shared leaf cases:',leaves_result,flush=True)
    whole=full([P.bundle(data) for data in (raw,image)])
    peak=actual_peak()
    q=dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),
           patches=patches,leaves=leaves_result,whole_GameCore=whole,actual_peak=peak,
           bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),SOURCE,ROM,PROFILE,R/'src/common.s')},
           scope='Shared native X/Y arithmetic and unchanged table bytes. Exact AXYP/SP and R4–R7 leaf checks, '
                 'then full representative GameCore memory/OAM/maps. Actual vectors have a separate qualification.')
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,candidate_SHA256=q['expected_memory_only_SHA256'],whole=whole,peak=peak)),flush=True)


if __name__=='__main__':
    main()
