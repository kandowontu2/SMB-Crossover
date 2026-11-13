"""Current Prince Star/1UP native pickup fixtures, stdout only.

Actors are explicitly placed mature; this is not a natural level route.
Source health, weapon and player position are never seeded.
"""
from hashlib import sha256
import json

import check_prince_natural_sword_1113 as P


def state(model):
    N=P.N
    return dict(x=N.get(model,'Player_X_Position')+256*N.get(model,'Player_PageLoc'),
        y=N.get(model,'Player_Y_Position'),health=model.ram[2][0x6cf],
        sword=model.ram[2][0x6ee],lives=N.get(model,'NumberofLives'),
        star=N.get(model,'StarInvincibleTimer'),status=N.get(model,'PlayerStatus'))


def main():
    raw=P.Base.C.ROM.read_bytes()
    seed,opening=P.cold(raw)
    rows=[]
    for kind in (2,3):
        model=P.Base.C.L.clone(seed)
        initial=state(model)
        N,W=P.N,P.W
        camera=N.get(model,'ScreenLeft_X_Pos')+256*N.get(model,'ScreenLeft_PageLoc')
        N.put(model,ObjectOffset=5,TimerControl=1,
              Player_Rel_XPos=(initial['x']-camera)&255,Player_Rel_YPos=initial['y'])
        for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,
            PowerUpType=kind,Enemy_X_Position=initial['x']&255,
            Enemy_PageLoc=initial['x']>>8,Enemy_Y_Position=initial['y']+7,
            Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():
            model[W.address(model.bundle,field)+5]=value
        N.invoke(model,'NrPrepare',a=kind,x=5,y=0)
        assert N.get(model,'PowerUpType',5)==kind
        N.invoke(model,'HuFullBox',x=0)
        N.invoke(model,'PowerUpObjHandler',x=5)
        collected=state(model)
        erased=N.get(model,'Enemy_Flag',5)==0
        assert erased and collected['health']==initial['health']==5
        assert collected['sword']==initial['sword']==0
        assert (collected['x'],collected['y'])==(initial['x'],initial['y'])
        if kind==2:
            assert collected['star']==35 and N.get(model,'AreaMusicQueue')==64
        else:
            assert N.get(model,'FloateyNum_Control',5)==11
        N.put(model,TimerControl=0)
        model.controller_pad=0
        for _ in range(24):P.Frames.frame(model)
        final=state(model)
        assert final['health']==5 and final['sword']==0
        assert final['lives']==initial['lives']+int(kind==3)
        assert final['y']==176 and final['x']==initial['x']
        if kind==2:assert final['star']>0
        rows.append(dict(kind=kind,before=initial,collected=collected,final=final,
                         actor_erased=erased,actual_Main_NMI_updates=24))
    result=dict(passed=True,ROM_SHA256=sha256(raw).hexdigest(),opening=opening,
        rows=rows,source_health_weapon_position_seeds=0,output_files=0,
        scope='Explicit mature native actor fixtures; real preparation, boxes, collision, collection and Main/NMI continuation. No natural Star/1UP or physical-Mesen claim.')
    print(json.dumps(result,sort_keys=True),flush=True)


if __name__=='__main__':main()
