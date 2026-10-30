"""Real native BG driver with explicitly staged, uninstalled FF call routes.

Only declared selector entries redirect through the real FarCallCommon to
actual RAM3 instructions. All BG decisions and native block/item writers run.
This is a CPU integration fixture, not a source-linked cart or native run.
"""
from pathlib import Path
import argparse,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v1 as C
from ff_host_terrain_controls_v1 import empty,cell
from check_tmnt_render_oa import address
ROUTES={'MegaManCollisionAdder':'FfHostAdder','HuBillBGHeadFast':'FfHostHead',
        'GmFootResident':'FfHostFeet','CrossoverSourceSideProbe':'FfHostSide',
        'CrossoverHeadWithinTerrain':'FfHostHeadWithin','SamusStopAtWall':'FfHostWall'}


def drive(b,wx=120,duck=0):
    m=empty(b);top=17 if duck else 6
    old=160-top;current=old-3
    at,base,row=cell(b,(wx+8)&65535,current+top);m[at]=0xc1
    C.put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8,Player_Y_Position=current,
          Player_Y_HighPos=1,Player_Y_Speed=253,Player_State=1,PlayerStatus=0,
          PlayerSize=0,CrouchingFlag=duck,RgCrouch=duck,FfTerrainPreviousY=old,
          FfTerrainFlags=0,Local_eb=0,DisableCollisionDet=0,SwimmingFlag=0,
          JumpspringAnimCtrl=0,BlockBounceTimer=0,GuestHurtTicks=0,SprDataOffset_Ctrl=0,
          Player_MovingDir=1,GameEngineSubroutine=8)
    targets={address(b,n):(n,v)for n,v in ROUTES.items()};called=[]
    def hook(m,c,step):
        if c.pc not in targets:return
        source,target=targets[c.pc];called.append([source,target,c.a,c.x,c.y])
        C.setv(m,'SafecallA_SMC',c.a,1)
        pc=address(b,target)
        C.setv(m,'FarcallJmpTarget_SMC',pc&255,1)
        C.setv(m,'FarcallJmpTarget_SMC',pc>>8,2)
        c.a=3;c.pc=address(b,'FarCallCommon')
    c,tr,low=C.run(m,'PlayerBGCollision',hook=hook)
    C.run(m,'FfHostAfterTerrain')
    x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')
    actual=[C.get(m,n)for n in ['Block_X_Position','Block_PageLoc','Block_Y_Position']]
    assert x==wx,('native BG ceiling displaced X',wx,duck,x,called,actual)
    assert C.get(m,'Player_Y_Position')==old,('exact ceiling response',old,C.get(m,'Player_Y_Position'))
    assert actual==[((wx+8)&65535)&240,((wx+8)&65535)>>8,144]
    return dict(worldX=wx,duck=duck,resultX=x,block=actual,routes=called,minSP=low)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--packet',type=Path,default=R/'build/final-fantasy-host-terrain-v2');ap.add_argument('--out',type=Path,default=R/'build/final-fantasy-host-terrain-nativebg-v1');args=ap.parse_args()
    assert not args.out.exists();args.out.mkdir()
    h=json.loads((args.packet/'build-proof.json').read_text())
    for p,d in h['bindings'].items():assert C.sha(p)==d,p
    b=C.bundle(args.packet);rows=[];failure=None
    try:
        for wx in [112,113,119,120,121,127,128,247,250,255,256,511]:
            for duck in [0,1]:rows.append(drive(b,wx,duck))
    except Exception as e:failure=dict(error=repr(e),traceback=traceback.format_exc())
    report=dict(passed=failure is None,status='CPU_NATIVE_BG_WITH_EXPLICIT_UNINSTALLED_TYPED_ROUTES',native=False,actual_cart_hooks=False,artificial_contact_or_result_writes=False,source_image_sha256=C.sha(args.packet/'ram3.bin'),routes=ROUTES,cases=rows,failure=failure,bindings={**h['bindings'],str((args.packet/'build-proof.json').resolve()):C.sha(args.packet/'build-proof.json'),str(Path(__file__).resolve()):C.sha(__file__)})
    (args.out/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],cases=len(rows),failure=failure)))
    if failure:raise SystemExit(1)
