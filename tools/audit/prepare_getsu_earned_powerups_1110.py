"""Bind a natural native Getsu power-up replay to the tested current ROM."""

import argparse
from collections import Counter
import json
from pathlib import Path

import deliver_getsu_current_1110 as D
from check_tmnt_render_oa import address, location
from prepare_selected_native_packet_v1 import prepare, sha


R, N = D.R,D.Current.Getsu.N
ROM = D.NATIVE/'candidate.nes'
NATIVE = D.NATIVE/'route'
SOURCE = R/'tools/playthroughs/getsu_fuma_powerups_1110.lua'
H = D.Current.Getsu.H


def symbol(b,name):
    return ((location(b,name)-16)//8192,address(b,name))


def ingress(b):
    """Exercise actual native item admission and collection through the full handler."""
    seed = H.prepare(b)
    points = {((bank|128),pc):name for name in ('PowerUpObjHandler','NrPickupCollision',
              'JnCollisionDispatch','M3PickupCollision','HuMature','HandlePowerUpCollision',
              'NrPickup','HuPickup','MarioSourcePowerupCollision','RlCollectDispatch',
              'GuestBeginPowerup','GuestPowerupUpdate') for bank,pc in [symbol(b,name)]}
    original = N.NesMPU
    hits = Counter()
    order = []

    class Trace(original):
        def step(self):
            name=points.get(H.point(self))
            if name:
                hits[name]+=1
                order.append(name)
            return super().step()

    episodes=[]
    N.NesMPU=Trace
    try:
        for kind,stage in ((0,0),(1,1),(2,0),(3,0)):
            for maturity in (6,128):
                m=N.fork(seed)
                N.put(m,ObjectOffset=5,FrameCounter=0,PlayerStatus=stage,
                      TimerControl=1,NmiDisable=255,Player_X_Position=64,
                      Player_Rel_XPos=64,Player_Rel_YPos=176,Player_Y_Position=176,
                      Player_Y_HighPos=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
                      ScreenRight_X_Pos=255,ScreenRight_PageLoc=0)
                m[address(b,'BoundingBox_UL_Corner'):address(b,'BoundingBox_UL_Corner')+4] = bytes((64,176,80,207))
                for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=maturity,PowerUpType=kind,
                    Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,
                    Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():
                    m[address(b,field)+5]=value
                hits.clear()
                order.clear()
                N.invoke(m,'PowerUpObjHandler',a=83,x=5,y=0,p=0x21)
                row=dict(kind=kind,initial_status=stage,maturity=maturity,calls=dict(hits),order=list(order),
                         enemy_box=list(m[address(b,'EnemyBoundingBoxCoord')+20:address(b,'EnemyBoundingBoxCoord')+24]),
                         flag=N.get(m,'Enemy_Flag',5),status=N.get(m,'PlayerStatus'),engine=N.get(m,'GameEngineSubroutine'),
                         active=N.get(m,'GuestPowerupActive'),target=N.get(m,'GuestPowerupTarget'),
                         star=N.get(m,'StarInvincibleTimer'),floaty=N.get(m,'FloateyNum_Control',5))
                if row['active']:
                    def watch(cpu):
                        if H.point(cpu)==((10|128),address(b,'GuestPowerupUpdate')):
                            hits['GuestPowerupUpdate']+=1
                    for age in range(90):
                        H.S.frame(m,0,watch)
                        if not N.get(m,'GuestPowerupActive'):
                            break
                    row.update(transform_updates=hits['GuestPowerupUpdate'],final_status=N.get(m,'PlayerStatus'),
                               final_engine=N.get(m,'GameEngineSubroutine'),final_active=N.get(m,'GuestPowerupActive'),
                               sampled_game_loops=age+1)
                episodes.append(row)
    finally:
        N.NesMPU=original
    return episodes


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('audit',))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    out=a.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    raw=D.qualified(ROM,D.PROOF)
    b=D.Current.Getsu.W.bundle(raw)
    if a.action=='audit':
        out.mkdir(exist_ok=True)
        rows=ingress(b)
        q=dict(passed=True,ROM_sha256=D.PIN,episodes=rows,
               scope='Legal CPU item placements through actual native PowerUpObjHandler. Controller replay is separate.',
               bindings={str(x.relative_to(R)):sha(x) for x in (ROM,D.PROOF,Path(__file__).resolve())})
        with (out/'ingress-v2.json').open('x',encoding='utf-8') as f:
            json.dump(q,f,indent=2)
            f.write('\n')
        print(json.dumps(rows),flush=True)


if __name__=='__main__':
    main()
