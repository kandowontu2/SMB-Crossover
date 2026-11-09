"""Compare the Mega Giant host geometry with actual pinned donor instructions."""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

from inventory_roster_exact_1110_v1 import M, R, ROM, PIN as HOST_PIN, bundle, sha
from prepare_mini_mario_native_power_1103_v56 import address
from trace_mega_giant_donor_1110_v1 import DONOR, PIN as DONOR_PIN


SOURCE=R/'tools/reference/mega_giant_mario_geometry_1110_v1.s'
STOP=0x5b00
BASE=0xa000


def invoke(mem,pc,*,a=0,x=0,y=0,p=0x21):
    cpu=M.NesMPU(memory=mem,pc=pc)
    cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=a,x,y,p,230
    cpu.stPushWord(STOP-1)
    for _ in range(500):
        if cpu.pc==STOP:
            assert cpu.sp==230
            return cpu
        assert mem[cpu.pc],hex(cpu.pc)
        cpu.step()
    raise AssertionError(('Unreturned CPU leaf',hex(pc),hex(cpu.pc)))


def assemble(out):
    with tempfile.TemporaryDirectory(prefix='asm-',dir=out) as temporary:
        tmp=Path(temporary)
        obj,cfg,binary,labels=(tmp/f'geometry.{ext}' for ext in ('o','cfg','bin','lbl'))
        cfg.write_text('MEMORY { CODE:start=$a000,size=$2000,file=%O; } SEGMENTS { GIANT:load=CODE,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',labels],check=True)
        return binary.read_bytes(),{line.split()[2][1:]:int(line.split()[1],16) for line in labels.read_text().splitlines()}


def parse_native_area(raw):
    b=bundle(raw)
    m=M.fresh(b)
    M.put(m,CrossoverMenuIndex=0)
    for name in ('MenuResolveCharacter','QueueSelection'):
        M.invoke(m,name)
    assert M.get(m,'SelectedCharacter')==0
    M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
    start=M.invoke(m,'CrossoverMenuInput')
    M.invoke(m,'ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    M.invoke(m,'PauseRoutine',a=0)
    for setup in range(600):
        if M.get(m,'OperMode_Task')==3 and M.get(m,'GameEngineSubroutine')==8:
            break
        M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,
              Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        M.invoke(m,'GameLoop')
        M.consume(m)
    else:
        raise AssertionError('Native initial parser did not reach gameplay')
    assert (address(b,'Block_Buffer_1'),address(b,'Block_Buffer_2'))==(0x300,0x3d0)
    assert (address(b,'Player_Rel_XPos'),address(b,'Player_Rel_YPos'))==(0x571,0x57c)
    assert (address(b,'Player_X_Position'),address(b,'Player_PageLoc'),address(b,'Player_Y_Position'))==(0x75,0x5c,0xbd)
    assert (address(b,'Player_OffscreenBits'),address(b,'CrouchingFlag'))==(0x5a0,0x717)
    assert (address(b,'GetBlockBufferAddr'),address(b,'BoundingBox_UL_Corner'))==(0x95dc,0x658)
    assert M.get(m,'WorldNumber')==M.get(m,'LevelNumber')==0
    tiles=bytes(m[0x300:0x4a0])
    assert 0 in tiles and any(tiles)
    return tiles,setup


def check_geometry(raw,donor,code,labels,tiles):
    source=bytearray(65536)
    source[0x8000:]=donor[16:32784]
    native=bytearray(65536)
    native[0x8000:0xa000]=raw[16+126*8192:16+127*8192]
    native[BASE:BASE+len(code)]=code
    original_x=source[0xe3b1:0xe3ec]
    original_y=source[0xe3ec:0xe427]
    assert native[labels['GiantProbeX']:labels['GiantProbeY']]==original_x
    assert native[labels['GiantProbeY']:labels['GiantProbeY']+59]==original_y
    assert source[0xe201:0xe209]==bytes.fromhex('f0a82020f0e82020')
    source[0x500:0x6a0]=native[0x300:0x4a0]=tiles
    counts={'GiantBodyBox':0,'GiantHead':0,'GiantFeet':0,'GiantSide':0}
    for x,y,duck,off in product((0,7,16,40,224,247,255),range(256),(0,1),(0,0x10)):
        source[0x3ad]=native[0x571]=x
        source[0x3b8]=native[0x57c]=y
        source[0x499]=duck+1
        native[0x717]=duck
        source[0x3d0]=native[0x5a0]=off
        invoke(source,0xe29c)
        invoke(source,0xeb5f)
        invoke(native,labels['GiantBodyBox'])
        assert source[0x4ac:0x4b0]==native[0x658:0x65c],(x,y,duck,off)
        counts['GiantBodyBox']+=1

    for x,page,y,index,(name,entry,dy) in product((0,7,16,40,239,247,255),(0,1,2,255),
            (32,47,88,107,135,176,191,239),range(59),
            (('GiantHead',0xe428,0),('GiantFeet',0xe427,1),('GiantSide',0xe42b,0))):
        actual=index+dy
        if actual>=59 or original_y[actual]==255:
            continue
        displacement=original_y[actual]-256 if original_y[actual]&128 else original_y[actual]
        if not 32<=y+displacement<=239:
            continue
        source[0x86]=native[0x75]=x
        source[0x6d]=native[0x5c]=page
        source[0xce]=native[0xbd]=y
        old=invoke(source,entry,y=index)
        new=invoke(native,labels[name],y=index)
        assert (old.a,old.x,old.y)==(new.a,new.x,new.y),(x,page,y,index,name)
        assert source[2:7]==native[5:10] and source[7]-2==native[10],(x,page,y,index,name)
        counts[name]+=1
    return counts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    raw,donor=ROM.read_bytes(),DONOR.read_bytes()
    assert sha(ROM)==HOST_PIN and sha(DONOR)==DONOR_PIN
    code,labels=assemble(out)
    cells,setup=parse_native_area(raw)
    counts=check_geometry(raw,donor,code,labels,cells)
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,host_SHA256=HOST_PIN,donor_SHA256=DONOR_PIN,
           code_bytes=len(code),code_SHA256=hashlib.sha256(code).hexdigest(),symbols=labels,cases=counts,
           actual_native_parser_setup_updates=setup,bindings={str(path):sha(path) for path in (Path(__file__),SOURCE,ROM,DONOR)},
           scope='Real current 1-1 parser fills native buffers. Exact original giant geometry and signed head/side/feet probe packets then match source instructions on those cells. Conditional component, no menu or owning hook yet.')
    (out/'geometry-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))


if __name__=='__main__':
    main()
