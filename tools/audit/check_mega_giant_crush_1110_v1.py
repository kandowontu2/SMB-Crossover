"""Execute Mega Giant's proposed cell adapter through the exact native effect owner."""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import subprocess
import tempfile

from check_mega_giant_geometry_1110_v1 import M, R, ROM, HOST_PIN, address, bundle, sha
from check_mega_giant_ppu_mapping_1110_v1 import start_stage
from check_tmnt_render_oa import location


SOURCE=R/'tools/reference/mega_giant_mario_crush_1110_v1.s'
FIXTURE=0x5b80
RETURN=0x5b00
PHYSICS=dict(Player_X_Position=0xa7,Player_PageLoc=2,Player_Y_Position=0x8b,
             Player_Y_HighPos=1,PlayerSize=1,CrouchingFlag=4,Player_Y_Speed=0xf7,MmBlockAttack=0)
OWNED=dict(SelectedCharacter=0,MarioVariant=9,OperMode=1,GameEngineSubroutine=8)


def assemble(out,b):
    source=SOURCE.read_text()
    addresses={}
    for line in source.splitlines():
        if not line.startswith('.import'):
            continue
        for name in line.split(' ',1)[1].split(', '):
            addresses[name]=address(b,name)
    definitions=''.join(f'{name}=${value:04x}\n' for name,value in addresses.items())
    source=definitions+re.sub(r'^\.import(?:zp)? .*\n','',source,flags=re.M)
    claim=location(b,'GuestClaimBlockSlot')
    assert (claim-16)//8192==8 and address(b,'GuestClaimBlockSlot')==0xbdc4
    assert b['raw'][claim:claim+6]==bytes.fromhex('aebe0520f1bd')
    assert addresses['FarCallCommon']==0x15a and addresses['PlayerHeadCollision']==0x9ef5
    with tempfile.TemporaryDirectory(prefix='crush-',dir=out) as folder:
        work=Path(folder)
        cfg,asm,obj,raw=(work/('crush.'+ext) for ext in ('cfg','s','o','bin'))
        cfg.write_text('MEMORY { CODE:start=$5b80,size=$200,file=%O; } '
                       'SEGMENTS { GIANT_CRUSH:load=CODE,type=ro; }\n')
        asm.write_text(source)
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',asm,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',raw],check=True)
        return raw.read_bytes(),addresses


def invoke(m,metatile,page,x):
    cpu=M.NesMPU(memory=m,pc=FIXTURE)
    cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p=metatile,page,x,236,0x21
    cpu.stPushWord(RETURN-1)
    path=set()
    min_sp=cpu.sp
    for _ in range(30000):
        if cpu.pc==RETURN:
            break
        if cpu.pc>=0x8000:
            path.add((m.rawtags[(cpu.pc-0x8000)//8192]&127,cpu.pc))
        assert m[cpu.pc],('Crush reached BRK',hex(cpu.pc))
        cpu.step()
        min_sp=min(min_sp,cpu.sp)
    else:
        raise AssertionError('Crush effect did not return')
    assert cpu.sp==236
    return bool(cpu.p&1),path,cpu.processorCycles,min_sp


def setup(seed,ptr,row,tile,**override):
    m=M.fork(seed)
    M.put(m,**(PHYSICS|OWNED|dict(R2=row,R6=ptr&255,R7=ptr>>8,VRAM_Buffer1_Offset=0)|override))
    m[ptr+row]=tile
    m.writes.clear()
    m.ram_writes.clear()
    return m


def check(seed):
    sample=[]
    for tile,page,row in product((0x10,0x11,0x12,0x13,0x14,0x15,0x51,0xc0,0xc1),(0,1,2,3),(0x30,0x70,0x90,0xa0)):
        x=0x7f
        ptr=0x300+(0xd0 if page&1 else 0)+(x>>4)
        m=setup(seed,ptr,row,tile)
        old_maps=m.rawtags[:]
        accepted,path,cycles,sp=invoke(m,tile,page,x)
        assert accepted and (8,0xbdc4) in path and (9,0xbe8b) in path
        assert m[ptr+row]==0x23 and m.rawtags==old_maps
        assert {n:M.get(m,n) for n in PHYSICS}==PHYSICS
        slot=M.get(m,'SprDataOffset_Ctrl')^1
        assert (M.get(m,'Block_X_Position',slot),M.get(m,'Block_PageLoc',slot),
                M.get(m,'Block_Y_Position',slot),M.get(m,'Block_BBuf_Low',slot),
                M.get(m,'Block_Orig_YPos',slot))==(x&0xf0,page,row+32,ptr&255,row)
        is_reward=tile in (0xc0,0xc1)
        assert M.get(m,'Block_State',slot)==(0x11 if is_reward else 0x12)
        assert M.get(m,'Block_Metatile',slot)==(0xc4 if is_reward else 0)
        assert M.get(m,'VRAM_Buffer1_Offset')==(10 if tile==0xc1 else 24)
        sample.append((cycles,sp))

    controls=dict(foreign=dict(SelectedCharacter=41),variant=dict(MarioVariant=0),title=dict(OperMode=0),
                  castle=dict(GameEngineSubroutine=5),budget=dict(VRAM_Buffer1_Offset=40),
                  pointer_hi=dict(R7=4),pointer_column=dict(R6=0xb0),row_alignment=dict(R2=0x73),
                  row_limit=dict(R2=0xd0),busy=dict())
    rejected=[]
    for name,fields in controls.items():
        m=setup(seed,0x307,0x70,0x12,**fields)
        if name=='busy':
            state=address(m.bundle,'Block_State')
            m[state:state+2]=[0x11,0x11]
        accepted,path,_,_=invoke(m,0x12,0,0x7f)
        assert not accepted and (9,0xbe8b) not in path and m[0x377]==0x12
        assert {n:M.get(m,n) for n in PHYSICS}==PHYSICS
        rejected.append(name)
    for actual,wanted in ((0,0),(0x23,0x23),(0x13,0x12)):
        m=setup(seed,0x307,0x70,actual)
        accepted,path,_,_=invoke(m,wanted,0,0x7f)
        assert not accepted and (8,0xbdc4) not in path and m[0x377]==actual
        rejected.append(f'cell_{actual:02x}_expected_{wanted:02x}')
    return dict(effect_cases=len(sample),negative_cases=rejected,
                complete_leaf_cycles=[min(v[0] for v in sample),max(v[0] for v in sample)],
                minimum_SP=min(v[1] for v in sample))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(ROM)==HOST_PIN
    b=bundle(ROM.read_bytes())
    code,addresses=assemble(args.output,b)
    seed,_=start_stage(b)
    seed[FIXTURE:FIXTURE+len(code)]=code
    seed.writes.clear()
    seed.ram_writes.clear()
    metrics=check(seed)
    q=dict(passed=True,ROM_written=False,source_CPU_only=True,host_SHA256=HOST_PIN,fixture_address=FIXTURE,
           assembled_bytes=len(code),assembled_SHA256=hashlib.sha256(code).hexdigest(),addresses=addresses,**metrics,
           scope='Exact compiled native block effect owners, temporary cell anchors, reward classification and guards. '
                 'The cell and variant are fixture inputs. Caller must classify original crushable contact and provide '
                 'its real world column. Runtime placement, sweep/deferral, native IRQ, and admission remain open.',
           bindings={str(p):sha(p) for p in (Path(__file__),SOURCE,ROM)})
    (args.output/'crush-effect-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assembled_bytes=len(code),**metrics)))


if __name__=='__main__':
    main()
