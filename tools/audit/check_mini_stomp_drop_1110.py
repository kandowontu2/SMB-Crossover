"""Qualify Mini's no-drop Goomba stomp at the original MaaStomp caller."""

import argparse
import ast
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_actor_bounds_irq_1110 as I
import check_native_enemy_offscreen_edge_irq_1110 as Q
import check_shared_palette_reset_irq_1110 as Audio
from check_mini_funded_actor_1108_v3 import install, run
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP


B,D,P,N,M,R=Q.B,Q.D,Q.P,Q.N,Q.M,Q.R
ROM=R/'build/mini-graphics-edge-movement-native-1110/candidate.nes'
PIN='a1c28fdf0b03bbc652e989083a74fc8365b7a875b821bcb92d63f7cd7144180d'
PROFILE=R/'build/mini-76bd-falling-profile-1110/capture/instruction-sample.json'
SOURCE=R/'tools/reference/mini_stomp_drop_1110.s'
DK=R/'tools/audit/prepare_dkjr_current_frontend_1108_v2.py'
CALLER,JOIN,WORKER,END=0xb907,0xb90a,0xb592,0xb5a7
PACKET=(0x162,0x16a,0x16c,0x16d,0x179)
DROP=0x6f12
CORE=bytes.fromhex('084820e4e0d0034e7f5c68282006eea904951fee3b06ad3b06186d8e0720b598ee8e07'
                   'ac6f07b97b989d93074c9d98')


def historical_preimage(before,after):
    tree=ast.parse(DK.read_text())
    compose=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='compose')
    apply=next(n for n in compose.body if isinstance(n,ast.FunctionDef) and n.name=='apply')
    call=next(n for n in compose.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
              and isinstance(n.value.func,ast.Name) and n.value.func.id=='apply'
              and len(n.value.args)>=2 and isinstance(n.value.args[1],ast.Constant) and n.value.args[1].value==WORKER)
    program=compile(ast.Module(body=[apply,call],type_ignores=[]),str(DK),'exec')
    for side,raw in enumerate((before,after)):
        scope=dict(raw=raw,off=D.offset,image=bytearray(raw),owned=set(),patches=[])
        try:
            exec(program,scope)
        except AssertionError as error:
            assert side==1 and error.args[0][0:2]==(66,hex(WORKER)),error
        else:
            assert side==0 and len(scope['patches'])==1
    return dict(old_EA_preimage_accepted=True,new_guard_preimage_rejected=True,source=str(DK))


def link(raw,out):
    D.check_span(raw,66,0xb8fb,CORE)
    D.check_span(raw,66,0xb58c,bytes.fromhex('4cadb54cfabd')+b'\xea'*(END-WORKER))
    D.check_span(raw,66,0xb5a7,bytes.fromhex('aeae044cc2ab'))
    for bank in (119,120,125,127):
        D.check_span(raw,bank,0xee06,bytes.fromhex('b517c906d0034c10ee60'))
    D.check_span(raw,59,0xb3b6,bytes.fromhex('08488a4898488e126f'))
    D.check_span(raw,126,0x98b5,bytes.fromhex('8d6a01a9c08d6c01a9bf8d6d01a9a44caa94'))
    bank=raw[16+66*8192:16+67*8192]
    assert not [(i,to) for i,op in enumerate(bank[:-2]) if op in (0x20,0x4c,0x6c)
                and WORKER<=(to:=bank[i+1]+256*bank[i+2])<END]
    with tempfile.TemporaryDirectory(prefix='stomp-link-',dir=out) as td:
        tmp=Path(td)
        cfg,obj,blob=(tmp/f'drop.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY { W:start=$b592,size=$15,file=%O,fill=yes,fillval=$ea; } '
                       'SEGMENTS { WORKER:load=W,type=ro; }\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',blob],check=True)
        data=blob.read_bytes()
    rows=[]
    for pc,old,new in ((WORKER,b'\xea'*(END-WORKER),data),(CALLER,bytes.fromhex('2006ee'),bytes.fromhex('2092b5'))):
        assert len(old)==len(new)
        rows.append(dict(physical_PRG=66,CPU_half_open=[pc,pc+len(old)],file_offset=D.offset(66,pc),
                         old_hex=old.hex(),new_hex=new.hex()))
    image=install(raw,rows)
    return image,rows,historical_preimage(raw,image)


def with_seeds(before,after,kernel=Q.KERNEL,kernel_sha=Q.KERNEL_PIN,owners=Q.OWNERS):
    images=[P.bundle(q) for q in (before,after)]
    old=B.BoundsBus
    B.BoundsBus=Audio.PaletteBus
    try:
        with Q.cold_kernel(kernel,kernel_sha):
            seeds=B.cold_pair(images,owners)
    finally:
        B.BoundsBus=old
    scene=json.loads(PROFILE.read_text())['scene']
    assert scene['frame']==1490 and scene['actors'][0]['id']==6 and scene['actors'][0]['x']==714
    return images,seeds,scene


def contact(c,slot=0):
    m=c.memory
    if D.bank_pc(c)==(254,0x9659) and c.x==slot and not getattr(m,'stomp_contact',False):
        at=0x65c+4*slot
        box=bytes(m[at:at+4])
        assert box[0]<=box[2] and box[1]<=box[3]
        m[0x658:0x65c]=box
        N.put(m,Player_Y_Speed=2,Player_Y_Position=169,Player_Y_HighPos=1,StarInvincibleTimer=0,Player_State=2)
        m[0x63d+slot]&=0xfe
        m[DROP]=0xff
        m.stomp_contact=True


def begin(seed,scene,slot=0):
    c=I.prepare(seed,scene)
    run(c,lambda z:D.bank_pc(z)==(194,CALLER),lambda z:contact(z,slot))
    assert c.x==slot and c.memory.stomp_contact and c.memory[0x17+slot]==6
    return c


def raw_packet(m):
    return tuple(list.__getitem__(m,at) for at in PACKET)


def watch_publication(c):
    m=c.memory
    m.point=D.bank_pc(c)
    if m.point==(194,JOIN):
        m.taint={at:at for at in PACKET}
        m.transfer=None
        m.copy_sites={}
        m.transports=[]
        m.stack_copies=[]
        m.shadow_watch=True


def game_end(c):
    m=c.memory
    assert not getattr(m,'taint',{}),getattr(m,'taint',{})
    assert m[DROP]==0 and m[0x1f]==4 and m[0x8e]==0xfc
    return semantic(c),bytes(m[D.SMC]),tuple((a,v) for a,v in m.writes if 0x200<=a<0x300)


def routes(images,seeds,scene):
    context=begin(seeds[41][0],scene)
    counts=Counter()
    for owner,alt,eid,flags in product(range(42),(0,1),(0,6,7,0x2d),(0x21,0xe5)):
        result=[]
        for im in images:
            c=fork(context,im)
            N.put(c.memory,SelectedCharacter=owner)
            c.memory[0x5fee],c.memory[0x17],c.p=alt,eid,flags
            run(c,lambda z:D.bank_pc(z)==(194,JOIN))
            result.append((semantic(c),raw_packet(c.memory),c.processorCycles,c.memory[DROP]))
        a,b=result
        if owner==41 and eid==6:
            assert a[0][:3]==b[0][:3] and a[0][3]&0xfd==b[0][3]&0xfd and a[0][4:]==b[0][4:],(a[0][:5],b[0][:5])
            assert a[3]==b[3]==0 and a[1]!=b[1]
        else:
            assert a[:2]==b[:2] and a[3]==b[3],(owner,alt,eid,flags,a[0][:5],b[0][:5],a[1],b[1])
        counts['mini_Goomba' if owner==41 and eid==6 else 'other',a[2]-b[2]]+=1
    return [[role,delta,n] for (role,delta),n in sorted(counts.items())]


def whole(before,after,kernel=Q.KERNEL,kernel_sha=Q.KERNEL_PIN):
    _,seeds,scene=with_seeds(before,after,kernel,kernel_sha,owners=(41,))
    rows=[]
    for phase,key in product((0,1,7,13),(0,192)):
        pair=[]
        for side,seed in enumerate(seeds[41]):
            c=begin(seed,dict(scene,frame=scene['frame']+phase,keys=key))
            at=c.processorCycles
            run(c,lambda z:D.bank_pc(z)==(194,JOIN))
            hook=c.processorCycles-at
            packet=raw_packet(c.memory)
            if side:
                watch_publication(c)
            run(c,lambda z:(z.pc,z.sp)==(STOP,252),watch_publication if side else None)
            pair.append((game_end(c),hook,packet,c.processorCycles))
        a,b=pair
        assert a[0]==b[0] and a[2]!=b[2],(phase,key,a[2],b[2])
        assert a[3]-b[3]==a[1]-b[1]>1300
        rows.append(dict(phase=phase,input=key,savings=a[3]-b[3],hook=[a[1],b[1]],
                         join_packets=[a[2],b[2]],final_packet_exact=True))
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN
    image,patches,allocation=link(raw,args.output)
    checks=routes(*with_seeds(raw,image,owners=(41,)))
    print('Routes',checks,flush=True)
    loops=whole(raw,image)
    refs=(Path(__file__),SOURCE,PROFILE,ROM,Q.KERNEL,DK,R/'src/inventory_drops.s',R/'src/remaining_weapons.s',
          R/'src/rogue_dawn_host_weapons.s',R/'src/collision.s',R/'tools/prepare_supermaaa_host_v1.py')
    out=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
             patches=patches,allocation=allocation,route_cycles=checks,whole_GameLoop=loops,
             bindings={str(p):P.sha(p.read_bytes()) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['expected_memory_only_SHA256'],loops,flush=True)


if __name__=='__main__':
    main()
