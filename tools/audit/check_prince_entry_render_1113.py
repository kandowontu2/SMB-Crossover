"""Read-only actual-cold phase0 renderer diagnosis; no candidate code edits.

Native engine/Y/OAM inputs are explicitly directed. Source pose0, epoch0,
health and actor state are supplied by the real cold constructor, not seeded.
"""
from hashlib import sha256
import json

import prince_entrance_handoff_1113 as E
import check_prince_brick_support_1111 as B


def check(raw):
    image,_=E.proposal(raw)
    seed,cold=B.cold(image)
    assert seed.ram[2][0x617]==0 and seed.ram[2][0xaa]==0
    rows=[]
    for y in (96,160):
        m=B.Q.Sonic.slim_fork(seed)
        B.N.put(m,SelectedCharacter=38,OperMode=1,GameEngineSubroutine=7,
            Player_X_Position=40,Player_PageLoc=0,Player_Y_Position=y,Player_Y_HighPos=1,
            CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=0,
            NmiDisable=255,ObjectMetasprite=0x91)
        initial=bytes(m[0x200:0x300])
        outer_graphics=B.N.invoke(m,'PlayerGfxHandler',a=83,x=71,y=109,p=0x61)
        outer=dict(descriptor=B.N.get(m,'ObjectMetasprite'),
            pointer=B.N.get(m,'SmPosePtr')+256*B.N.get(m,'SmPosePtr',1),result=outer_graphics)
        # Supply the authenticated private caller's actual C2 map. Record
        # the outer handler separately: common cold is not a parsed scene.
        m.raw_page(2,2)
        B.N.put(m,CurrentBankC=2)
        graphics=B.I.invoke(m,3,0xbdcb,(3,71,109,0x61))
        descriptor=B.N.get(m,'ObjectMetasprite')
        pointer=B.N.get(m,'SmPosePtr')+256*B.N.get(m,'SmPosePtr',1)
        assert descriptor==0 and pointer==B.N.address(m.bundle,'SmPose') and m[pointer]==0,(descriptor,pointer,outer)
        source_draw=B.I.invoke(m,3,0xbbc1,(83,71,109,0x61))
        assert source_draw['regs'][3]&1==0
        assert bytes(m[0x200:0x300])==initial and B.N.get(m,'CurrentOAMOffset')==0
        # The exact stable zero header consumed by the generic fallback is
        # unbanked native RAM. Execute that native emitter directly too.
        m[3]=pointer&255;m[4]=pointer>>8
        fallback=B.N.invoke(m,'MetaspriteRenderLoop',a=0,x=0,y=0,p=0x61)
        assert bytes(m[0x200:0x300])==initial and B.N.get(m,'CurrentOAMOffset')==0
        compact=lambda result:{key:result[key] for key in ('regs','CPU','minSP') if key in result}
        rows.append(dict(native_y=y,source_pose=m.ram[2][0x617],epoch=m.ram[2][0xaa],
            source_HP=m.ram[2][0x6cf],descriptor=descriptor,fallback_pointer=pointer,
            source_draw_C=source_draw['regs'][3]&1,native_fallback_header=m[pointer],
            emitted_player_OAM_bytes=0,outer_graphics=outer,private_graphics=compact(graphics),source_draw=compact(source_draw),fallback=fallback))
    return dict(passed=True,ROM_SHA256=sha256(image).hexdigest(),actual_cold=cold,rows=rows,
        conclusion='Phase0 Prince has no body emission: actual graphics publishes its zero native descriptor, original pose0 rejects privateDraw withC0, and native fallback emits zero sprites. This is an invisible entrance interval, not Mario fallback.',
        scope='Directed native engine/Y/OAM fixtures from actual common cold, not physical pixels or naturally reached Main state. Source phase/pose/health/actor fields are never seeded.',
        outputs=0,Mesen=False)


if __name__=='__main__':
    result=check(E.frozen_parent())
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(result,sort_keys=True),flush=True)
