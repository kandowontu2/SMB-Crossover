"""Qualify exact native Goomba edge clipping within the incumbent typed span."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_native_brick_coin_draw_1110_v1 as V
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at
from check_mini_visibility_dispatch_1110_v1 import memory


R,P,N=V.R,V.P,V.N
ROM=R/'build/mini-platform-firebar-native-1110/candidate.nes'
PIN='6bd5e4b1976e26ecccd9b7c0512944020d6eb7a6e2c8c35ab50c53d0441e7491'
SOURCE=R/'tools/reference/native_goomba_edge_1110_v1.s'
PROFILE=R/'build/mini-platform-actor-profile-1110/capture/instruction-sample.json'
START,END,ACTOR=0xbead,0xbf33,0xa094
DESCRIPTORS={
    0xaf2f:bytes([8,164,67,8,0,162,67,8,8]),
    0xaf38:bytes([8,162,3,8,0,164,3,8,8]),
    0xaf41:bytes([8,162,3,8,0,164,3,8,8]),
    0xaf4a:bytes([8,164,67,8,0,162,67,8,8]),
}


def compose(raw,out):
    for pc,data in DESCRIPTORS.items():
        V.preimage(raw,pc,data)
    V.preimage(raw,0xa09e,bytes.fromhex('e067f004e068d048c007b044b98705290819c17319fa06d037850c'))
    V.preimage(raw,0xa0d9,bytes.fromhex('b93e05c902bdd6b59002e9098503a9af85044cadbe'))
    V.preimage(raw,0xb63d,bytes.fromhex('384a'))
    V.preimage(raw,0xbe92,bytes.fromhex('a504c9b3f00929fdc9add0304ce0ba4cc3b9'))
    V.preimage(raw,0xbae0,bytes.fromhex('a504c9afd005a5034cadb9'))
    V.preimage(raw,0xb9ad,bytes.fromhex('c92ff00cc938f008c941f004c94ad0034cadbe4ccebe'))
    bank=raw[V.offset(0xa000):V.offset(0xa000)+8192]
    ingress=[]
    for i in range(len(bank)-2):
        op,lo,hi=bank[i:i+3]
        pc=0xa000+i
        target=lo+(hi<<8)
        if op in (0x20,0x4c) and START<=target<END and not START<=pc<END:
            ingress.append((pc,target))
    assert ingress==[(0xa0eb,START),(0xb9bd,START),(0xb9c0,0xbece)]
    at=V.offset(START)
    old=raw[at:at+END-START]
    assert P.sha(old)=='28bd1812115ace918b747653e5a9bff88d3afabccb70a2dd15aa4f5a24e4e23f'
    with tempfile.TemporaryDirectory(prefix='goomba-edge-',dir=out) as folder:
        tmp=Path(folder)
        cfg,obj,binary,labels=(tmp/f'edge.{s}' for s in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { W:start=$bead,size=$86,file=%O; } SEGMENTS { TYPED:load=W,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',labels],check=True)
        new=binary.read_bytes()
        syms={parts[2][1:]:int(parts[1],16) for line in labels.read_text().splitlines()
              if len(parts:=line.split())==3}
    assert len(new)==len(old)
    assert syms==dict(GoombaGeneric=0xbece,GoombaReject=0xbf2d,TypedGoomba=START,TypedGoombaEnd=END)
    patch=dict(physical_PRG=4,start=START,end_exclusive=END,file_offset=at,old_hex=old.hex(),new_hex=new.hex())
    return install(raw,[patch]),[patch],syms


def seed(bundle):
    m=N.fresh(bundle)
    m.raw_page(1,132)
    N.put(m,CurrentBank=132,NmiDisable=255,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
          DisableScreenFlag=0,Mirror_PPUMASK=30)
    return m


def actor(seed,row,camera,pose,facing,cursor=12,rotation=204,visit=None):
    m=slim_fork(seed)
    slot=row['slot']
    for name,value in (('Enemy_ID',row['id']),('Enemy_Flag',row['flag']),('Enemy_State',row['state']),
                       ('Enemy_X_Position',row['x']&255),('Enemy_PageLoc',row['x']>>8),
                       ('Enemy_Y_Position',row['y_low']),('Enemy_Y_HighPos',row['y_high']),
                       ('Enemy_MovingDir',facing),('Enemy_SprAttrib',0),('EnemyVerticalFlip',0)):
        m[P.address(m.bundle,name)+slot]=value
    N.put(m,SelectedCharacter=41,ScreenLeft_PageLoc=camera>>8,ScreenLeft_X_Pos=camera&255,
          GuestOamRotationActive=1,RgOamRotation=rotation,CurrentOAMOffset=cursor,NmiDisable=255)
    c=cpu_at(m,ACTOR,229,0x21,x=pose,y=slot+1)
    c.a=slot+1
    run(c,lambda q:(q.pc,q.sp)==(V.STOP,229),visit)
    ordered=[(a,v) for a,v in m.writes if 0x200<=a<0x300]
    return (registers(c,0xef),live_stack(c),memory(m),ordered),c.processorCycles


def qualifier(seeds):
    peak=json.loads(PROFILE.read_text())
    scene=peak['scene']
    rows=[row for row in scene['actors'] if row['id']==6 and row['flag']==1]
    camera=scene['camera_left']
    assert [row['x']-camera for row in rows]==[123,226,249] and all(r['y_low']==184 for r in rows)
    assert peak['foreground_opcodes']['4:bebb']==7
    witness=[]
    for row in rows:
        timings=[]
        for pose,facing in product((0x67,0x68),(1,2)):
            a,b=[actor(m,row,camera,pose,facing) for m in seeds]
            assert a[0]==b[0],(row,pose,facing,a[0][3],b[0][3])
            timings.append((a[1],b[1],a[1]-b[1]))
        witness.append(dict(relative_x=row['x']-camera,pose_facing_cycles=sorted(set(timings)),
                            min_saved=min(r[2] for r in timings),max_saved=max(r[2] for r in timings)))

    counts=Counter()
    positions=((0,0,0,1),(123,0,184,1),(226,0,184,1),(247,0,247,1),(248,0,184,1),
               (249,0,184,1),(255,0,247,1),(255,0,248,1),(0,0,255,1),(255,255,184,1),
               (249,1,184,1),(249,0,184,0),(249,0,184,2),(0,127,255,255))
    for entry,ptr,pos,cursor,(rot,active),attr,p in product(
        (START,0xbe92),DESCRIPTORS,positions,(0,12,247,248,251,252,255),
        ((0,0),(0,1),(204,1),(251,0x81)),(0,3,0x8b,255),(0x21,0xe5),
    ):
        a,b=[V.draw(m,entry,ptr,pos,cursor,rot,active,attr,p) for m in seeds]
        assert a[0]==b[0],(hex(entry),hex(ptr),pos,cursor,rot,active,attr,p,a[0][:2],b[0][:2],a[0][3],b[0][3])
        counts[a[1]-b[1]]+=1
    return dict(cases=sum(counts.values()),cycles=sorted(counts.items()),witness=witness,
                witness_saved_min=sum(q['min_saved'] for q in witness),
                witness_saved_max=sum(q['max_saved'] for q in witness))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN
    image,patches,syms=compose(raw,args.output)
    result=qualifier([seed(P.bundle(data)) for data in (raw,image)])
    q=dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),
           patches=patches,symbols=syms,**result,
           bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),SOURCE,ROM,PROFILE)},
           scope='Authentic typed Goomba templates, actual 6bd5 actor geometry, matched ordered writes including clipped OAM X/Y.')
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ('patches','bindings')}),flush=True)


if __name__=='__main__':
    main()
