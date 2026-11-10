"""Changed aligned Sonic metadata/glue IRQ/real lag-NMI cuts, stdout only."""
import argparse
import copy
from hashlib import sha256
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_native_effects_aligned_1110 as A
import check_sonic_native_host_services_1110 as S
import check_sonic_shared_audio_1110 as Audio
import check_ff_head_lifetime_irq_1110 as ISR

R,T,E,C=A.R,A.T,A.E,A.C


def clone(m,c=None):
    q=list.__new__(type(m));list.extend(q,list.__iter__(m))
    for k,v in vars(m).items():
        setattr(q,k,v if k in('bundle','program','effect')else []if k in('writes','ram_writes','ppu_log','blocked')else copy.deepcopy(v))
    q.active=False
    if c is None:return q
    d=copy.copy(c);d.memory=q;return q,d


def qualify(seed,p):
    source=inspect.getsource(S.vector_matrix)
    needle='used=tag==3 and 0xa000<=c.pc<private_end or 0x15a<=c.pc<0x17b'
    assert source.count(needle)==1
    source=source.replace(needle,'used=(tag==3 and 0xbd69<=c.pc<private_end)or(tag==2 and 0xd040<=c.pc<0xd25e)or c.pc in FRAME_CALLS or 0x15a<=c.pc<0x17b')
    source=source.replace('def trace(m,name,pc):','def trace(m,name,pc,y=109):')
    source=source.replace('c.a,c.x,c.y,c.p,c.sp=85,73,109,0x21,224','c.a,c.x,c.y,c.p,c.sp=85,73,y,0x21,224')
    needle='    assert ISR.DEEPEST is not None'
    assert source.count(needle)==1
    extra='''
    for name,leaf,y in(('bounds','MetaBounds',0),('head','MetaHead',0),('side','MetaSide',3),('feet','MetaFeet',0),('graphics','MetaGraphics',0),('draw','MetaDraw',0),('death','MetaDeath',0)):
        m=clone(first)
        set_native(m,Player_Rel_XPos=80,Player_Rel_YPos=176,Player_Y_HighPos=1,CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=224)
        if name=='head':
            for key,value in dict(HeadPending=1,HeadTile=0x61,HeadRow=128,HeadPhase=15,HeadColumn=2,HeadPage=1).items():m[EFFECT['context'][key]]=value
        if name=='death':set_native(m,MmDeathPit=1,MmDeathAge=0)
        trace(m,name,p['symbols'][leaf],y)
    below=clone(first)
    for at in range(0x300,0x4a0):below[at]=0
    for tick in range(1,60):
        set_native(below,FrameCounter=tick,SavedJoypadBits=0)
        invoke(below,p['symbols']['SonicServices'])
    set_native(below,FrameCounter=60)
    trace(below,'below-viewport',p['symbols']['SonicServices'])
    sky=clone(seed);scene(sky,64,64);invoke(sky,p['symbols']['SonicHostFresh'])
    for at in range(0x300,0x4a0):sky[at]=0
    for col in range(24):sky[0x300+(col//16&1)*208+4*16+(col&15)]=0x54
    for tick in range(20):
        set_native(sky,FrameCounter=tick,SavedJoypadBits=0 if tick<2 else 129)
        invoke(sky,p['symbols']['SonicServices'])
        if tick>2 and word(sky,0xc074)<32:break
    assert word(sky,0xc074)<32
    set_native(sky,FrameCounter=tick+1)
    trace(sky,'above-viewport',p['symbols']['SonicServices'])
'''
    source=source.replace(needle,extra+'\n'+needle)
    scope=dict(S.__dict__);scope.update(clone=clone,invoke=T.invoke,EFFECT=p,
        FRAME_CALLS={row[0]for row in p['frame_terrain_calls']})
    exec(compile(source,'<aligned changed-code native IRQ matrix>','exec'),scope)
    with patch.object(ISR,'regs',side_effect=lambda c:(c.pc,c.a,c.x,c.y,c.p&0xef,c.sp)):
        return scope['vector_matrix'](seed,p['service'],ISR)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    image,program,p=A.proposal();image,audio=Audio.proposal(image)
    seed=T.install(C.Current.W.bundle(image),p,program)
    result=qualify(seed,p)
    print(json.dumps(dict(passed=True,source_only=True,outputs_written=0,ROM_written=False,
        in_memory_SHA256=E.digest(image),source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        vectors=result,audio_source_SHA256=audio['source_SHA256'],
        scope='Reached changed private glue/aligned metadata andtwoframe-call/actualSMC cuts only. Unchanged motor/ordinaryprefix retains frozen551 vectors; native stage/sharedfoot/frontend integration still pending.'),sort_keys=True),flush=True)
    assert not args.output.exists()


if __name__=='__main__':main()
