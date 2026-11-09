"""Reuse the exact native Goomba packet already selected in Mini's draw lane."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import re
import subprocess

import measure_mini_render_bookkeeping_1109_v1 as V
import measure_mini_only_goomba_1108_v4 as D
from check_mini_funded_actor_1108_v3 import install, slim_fork, registers, live_stack, run

A,N,R,OUT=V.A,V.N,V.R,V.OUT
ENTRY,END=0xa038,0xa0f2
TYPED=0xbead
AFTER_STORE=0xa1c9


def edit(src,a,b):
    assert src.count(a)==1,a
    return src.replace(a,b)


def assemble(b):
    defs=''.join(f'{name}=${A.address(b,name):04x}\n' for name in
                 [*D.P.NAMES,'M0','FrameCounter','SpriteShuffleOffset','ObjectMetasprite','WorldFirebarDrawAdmission'])
    defs+=f'DrawMetasprite=${D.P.ORIGINAL:04x}\nNativeDrawTail=${D.AFTER_LOOP:04x}\nNativeRenderCall=${D.NATIVE_RENDER:04x}\nTypedGoomba=${TYPED:04x}\n'
    new=edit(D.SOURCE,''' sta SpriteShuffleOffset
 jsr MiniGoomba
 lda SpriteShuffleOffset''',''' pha
 jsr MiniGoomba
 pla''')
    new=edit(new,''' lda HpNativeDrawHi,y
 ora ObjectVerticalFlip,y''',''' lda SprObject_SprAttrib,y
 and #8                      ; FLASH retains the actual generic post-render.
 ora HpNativeDrawHi,y
 ora ObjectVerticalFlip,y''')
    new=edit(new,''' lda PlayerFacingDir,y
 lsr
 bne Left
 lda MetaspriteTableRightLo,x
 bne Pointer
Left:
 lda MetaspriteTableLeftLo,x''',''' lda PlayerFacingDir,y
 cmp #2                       ; native LSR/BNE treats 2..255 as left
 lda MetaspriteTableRightLo,x
 bcc Pointer
 sbc #9                       ; proven immutable left/right pair spacing''')
    new=edit(new,''' jmp NativeRenderCall''',''' jmp TypedGoomba              ; still runs full native clips and capacity''')
    result=[]
    for name,source in [('typed-goomba-original',D.SOURCE),('typed-goomba-fast',new)]:
        p=OUT/name
        src,cfg,obj,data,lbl=(p.with_suffix(ext) for ext in ['.s','.cfg','.o','.bin','.lbl'])
        src.write_text(defs+source)
        cfg.write_text(f'MEMORY{{C:start=${ENTRY:04x},size=$100,file=%O;}}SEGMENTS{{CODE:load=C,type=ro;}}\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',data,'-Ln',lbl],check=True)
        obj.unlink()
        labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-F]+) \.(\w+)$',lbl.read_text(),re.M)}
        result.append((data.read_bytes(),labels))
    return result


def test_order(images,labels):
    counts=Counter()
    seeds=[A.fixture(b,0,False,False)for b in images]
    for m in seeds:
        m.raw_page(1,132)
        N.put(m,CurrentBank=132)

    def setup(m,phase,parity,scene,rotation,cursor):
        N.put(m,SelectedCharacter=41,GameEngineSubroutine=8,SpriteShuffleOffset=phase,
              FrameCounter=parity,GuestOamRotationActive=1,RgOamRotation=rotation,
              CurrentOAMOffset=cursor,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
              ScreenRight_X_Pos=255,ScreenRight_PageLoc=0, RlOutlineBypass=0)
        for n in ('Enemy_Flag','Enemy_ID'):
            at=A.address(m.bundle,n)
            m[at:at+6]=bytes(6)
        at=A.address(m.bundle,'ObjectMetasprite')
        m[at:at+24]=bytes(24)
        rows={
            'empty':[],
            'ordinary':[(1,0x67,1,32,1,160,0,0x21),(4,0x68,2,84,1,180,0,0x43)],
            'crowd':[(i,0x67+i%2,1+i%2,32+i*24,1,140+i*3,0,i%4) for i in range(1,7)],
            'left_clip':[(1,0x67,1,252,1,176,0,0x20),(4,0x68,2,0,1,150,0,0x40)],
            'vertical_clip':[(1,0x67,1,128,0,251,0,0),(4,0x68,2,64,1,251,0,0)],
            'flash_flip':[(1,0x67,1,32,1,160,0,0x29),(4,0x68,2,64,1,180,0x80,0x42)],
            'mixed':[(1,0x67,1,32,1,160,0,0x21),(4,0x68,2,84,1,180,0,0x43),(18,0x37,1,160,1,120,0,0)],
            'lift':[(1,0x67,1,32,1,160,0,0x21),(4,0x68,2,84,1,180,0,0x43)],
            'firebar':[(1,0x67,1,32,1,160,0,0x21),(4,0x68,2,84,1,180,0,0x43)],
        }[scene]
        for slot,pose,face,x,high,y,flip,attr in rows:
            for n,v in [('ObjectMetasprite',pose),('PlayerFacingDir',face),('SprObject_X_Position',x),
                        ('SprObject_PageLoc',255 if scene=='left_clip' and slot==1 else 0),('SprObject_Y_HighPos',high),
                        ('SprObject_Y_Position',y),('ObjectVerticalFlip',flip),('SprObject_SprAttrib',attr)]:
                D.P.write(m,n,v,slot)
        if scene=='lift':
            for n,v in [('Enemy_Flag',1),('Enemy_ID',0x25),('Enemy_State',0x60),('Enemy_BoundBoxCtrl',5)]:
                D.P.write(m,n,v,3)
            N.invoke(m,'HpPrepareNativePointers',x=0,y=0)
        if scene=='firebar':
            V.init(m,3,0x1b,1,41,1)
            N.put(m,SpriteShuffleOffset=phase,FrameCounter=parity,RgOamRotation=rotation,CurrentOAMOffset=cursor)
        m[0x200:0x304]=bytes((17*i+31)&255 for i in range(260))
        m.writes.clear()

    for phase,parity,scene in product(range(24),[0,1],['empty','ordinary','crowd','left_clip','vertical_clip','flash_flip','mixed','lift','firebar']):
        results=[]
        for i,seed in enumerate(seeds):
            m=slim_fork(seed)
            setup(m,phase,parity,scene,[0,4,124,248,252][phase%5],[4,236,244,248,252][phase%5])
            c=N.NesMPU(memory=m,pc=ENTRY)
            c.a,c.x,c.y,c.p,c.sp=83,7,23,0x71,224
            order=[]

            def visit(z):
                if m.rawtags[1]==132:
                    if z.pc==labels[i]['MiniDrawActor']:
                        order.append((z.y,z.x))
                    if z.pc==A.address(m.bundle,'WorldFirebarDrawAdmission'):
                        order.append((0,-1))

            run(c,lambda z:z.pc==AFTER_STORE,visit)
            results.append((registers(c),live_stack(c),A.state(m),
                           [(a,v) for a,v in m.writes if 0x200<=a<0x304 or a in (0x5115,0x5116)],order,c.processorCycles))
        a,b=results
        assert a[:-1]==b[:-1],(phase,parity,scene,a[0],b[0],a[3:5],b[3:5])
        counts[scene,a[-1]-b[-1]]+=1
    return [[scene,delta,count] for (scene,delta),count in sorted(counts.items())]


def measure_main(images):
    groups=[]
    for enemies,parser in product([0,2,5],[False,True]):
        pair=[A.fixture(b,enemies,False,parser) for b in images]
        rows=[]
        for epoch in range(2,22):
            outcomes=[]
            for m in pair:
                buttons=129 if 6<=epoch<18 else 0
                N.put(m,FrameCounter=epoch,SavedJoypadBits=buttons,SavedJoypad1Bits=buttons,
                      VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                m.writes.clear()
                z=N.invoke(m,'GameCoreRoutine',x=0,y=0)
                outcomes.append((V.state(m,z),z['CPU']))
            a,b=outcomes
            assert a[0]==b[0],(enemies,parser,epoch,a[0][0],b[0][0])
            rows.append([a[1],b[1],a[1]-b[1]])
        groups.append(dict(enemies=enemies,parser=parser,cycles=rows))
    return groups


def main():
    raw=V.ROM.read_bytes()
    assert A.sha(raw)==V.PIN
    b=A.bundle(raw)
    desc=D.P.prove_art(b)
    rows=[int(desc[f'MetaspriteData_GOOMBA_WALKING_{i}_{face}']['cpu'],16) for i in [1,2]for face in ['LEFT','RIGHT']]
    assert rows==[0xaf2f,0xaf38,0xaf41,0xaf4a]
    (old,ol),(new,nl)=assemble(b)
    assert len(old)==END-ENTRY and len(new)<=len(old)
    at=16+4*8192+ENTRY-0xa000
    assert raw[at:at+len(old)]==old
    # The typed join starts at the original interior X/Y guards. Its bad
    # bounds and malformed header continue through existing native exits.
    join=16+4*8192+TYPED-0xa000
    assert raw[join:join+18].hex()=='a508d0e7a50ac901d0e1a507c9f8b0dba509'
    patch=dict(physical_PRG=4,CPU_half_open=[ENTRY,END],file_offset=at,old_hex=old.hex(),new_hex=new.ljust(len(old),b'\xea').hex())
    render=json.loads((OUT/'measurement.json').read_text())
    successor=install(raw,[patch])
    pair=[b,A.bundle(successor)]
    direct=test_order(pair,[ol,nl])
    whole=measure_main([b,A.bundle(install(raw,[patch,render['patch']]))])
    q=dict(passed=True,CPU_only=True,ROM_written=False,base_SHA256=V.PIN,patch=patch,
           memory_only_SHA256=A.sha(successor),combined_world_render_SHA256=A.sha(install(raw,[patch,render['patch']])),
           typed_descriptors=desc,ordered_OAM_cases=direct,combined_GameCore=whole,
           scope='Exact Mini-only cloned actor render sequence. Stacks own temporary actor index; only native final SpriteShuffleOffset write is observable by subsequent engine code. Constant nine-byte descriptor spacing proven. Existing native clip, capacity, rotation and generic flash/flip paths remain; foreign shared renderer unchanged. IRQ/vector proof pending.',
           bindings={str(p):A.sha(p.read_bytes())for p in [Path(__file__),Path(D.__file__),V.ROM,R/'src/metasprite_engine.s',R/'src/native_goomba_draw.s',OUT/'measurement.json']})
    (OUT/'typed-goomba.json').write_text(json.dumps(q,indent=2)+'\n')
    print('Typed order',direct,'whole combined',[(x['enemies'],sorted(set(y[2] for y in x['cycles'])))for x in whole],flush=True)


if __name__=='__main__':main()
