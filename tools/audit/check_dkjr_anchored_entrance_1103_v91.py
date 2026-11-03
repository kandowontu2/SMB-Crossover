"""Native entrance ordering and pending-world gameplay guards on real cold90."""
import json
from pathlib import Path
import prepare_dkjr_anchored_owner_1103_v90 as P
import check_dkjr_entrance_order_1103_v88 as V88

A,R,O=P.A,P.R,P.O
C=P.P.C;N,W=C.N,A.W


def main():
    base,q=P.image();m,history,good=V88.run(base)
    assert good and m.ram[2][0x8fe]==2,history
    # A pending source actor with an invalid native entrance origin cannot
    # advance its original state, take damage, consume an item or emit its
    # constructor's stale cached body. No final native Y is seeded here.
    pending,_=C.cold(base,40)
    N.put(pending,Player_X_Position=0,Player_PageLoc=0,Player_Y_Position=0,Player_Y_HighPos=0,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,
        GameEngineSubroutine=0,VRAM_Buffer1_Offset=0)
    N.invoke(pending,'HuFresh',a=83,x=0,y=109,p=0x21)
    assert pending.ram[2][0x8fe]==1
    for name,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=3,
            Enemy_X_Position=0,Enemy_PageLoc=0,Enemy_Y_Position=0,Enemy_Y_HighPos=1).items():
        pending[W.address(base,name)+5]=value
    N.put(pending,ObjectOffset=5,GameEngineSubroutine=8,CurrentOAMOffset=24)
    initial=bytes(pending.ram[2][:0x800]);rows=[]
    names=['HuMovement','HuFullBox','HuDraw','HuInjury','HuDeathStart','HuDeath','HuBounceOnly','HuMature','HuPickup']
    for name in names:
        n=N.fork(pending)
        z=N.invoke(n,name,a=83,x=5,y=0,p=0x21)
        assert bytes(n.ram[2][:0x800])==initial,('pending original state',name)
        assert n.ram[2][0x8fe]==1 and N.get(n,'Enemy_Flag',5)==1 and N.get(n,'NumberofLives')==2,('pending item/life',name)
        assert N.get(n,'CurrentOAMOffset')==24,('pending OAM',name)
        if name=='HuDraw':
            zero=W.address(base,'ObjectMetasprite')
            assert n[zero]==0 and n[W.address(base,'SmPosePtr')]|n[W.address(base,'SmPosePtr')+1]<<8==zero
        rows.append(dict(actual_native_entry=name,carry=bool(z['P']&1),original2048_unchanged=True,item_unconsumed=True))
    # The scene/Fresh APIs are deliberately the same private Reset→Construct
    # wrapper. Once anchored, both rearm exactly one future native entrance.
    rearms=[]
    for name in ['HuFresh','HuGenericFresh']:
        n=N.fork(m)
        N.put(n,DisableScreenFlag=1,Mirror_PPUMASK=0)
        z=N.invoke(n,name,a=83,x=0,y=109,p=0x21)
        assert z['P']&1 and n.ram[2][0x8fe]==1 and n.ram[2][0x6b]==1
        rearms.append(name)
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(base['raw']),manual_final_native_Y_written=False,
        actual_entrance_history=history,pending_public_guard_cases=rows,
        rearmed_after_anchored_scene_or_Fresh=rearms,
        body_bytes=q['body_bytes'],metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],
        scope='Real native table-driven Entrance_GameTimerSetup/PlayerEntrance→firstGameCore uses the actual post-entranceX40/Y176/high1, sourceOAM32/191, Ready2. No fixedY/new state byte. All nine pending-world public policies leave original2048 bytes and HP/item/lives untouched; stable zeroheader and no stale body OAM. Fresh/scene rearm via Reset→Construct. Complete compiled writer/indirect/retirement and IRQ/palette/name/lifecycle proof remain pending; no native/menu/ROM admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(V88.__file__),
            O/'native-owner-proposal-v90.json',O/'native-entrance-v89-layout.json',O/'native-entrance-v88-negative.json']})
    (O/'native-entrance-v91-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','actual_entrance_history','pending_public_guard_cases','rearmed_after_anchored_scene_or_Fresh']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-entrance-v91-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
