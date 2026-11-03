"""Complete real native mushroom/flower transformations for both source actors."""
from collections import Counter
import json
from pathlib import Path
import check_bub_collecting_interrupts_1102_v59 as I
from prepare_selected_native_packet_v1 import R,sha
G,Q,N,address=I.G,I.Q,I.N,I.address
O=R/'build/bub-upgrades-root-lifecycle-1102-v60'

def main():
    O.mkdir(exist_ok=True);_,b,route,q=G.bundles();rows=[]
    for identity in [0,1]:
        m=Q.Q.fresh(b,route,identity);Q.L.E.main_fields(m)
        actor=0x42 if identity else 0x2e
        N.put(m,NmiDisable=255,TimerControl=0,Player_Rel_XPos=64,Player_Rel_YPos=176)
        N.invoke(m,'HuFullBox',a=83,x=0,y=0,p=0x21)
        for kind in [0,1]:
            N.put(m,ObjectOffset=5)
            for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=191,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():m[address(b,field)+5]=value
            N.invoke(m,'PowerUpObjHandler',a=83,x=5,y=0,p=0x21)
            flags=1 if kind==0 else 7
            assert m.ram[2][actor+2]==flags
            assert N.get(m,'GameEngineSubroutine')==9 and N.get(m,'GuestPowerupActive')==1
            assert N.get(m,'Square2SoundQueue')!=0
            frozen=bytes(m.ram[2][:1024]);coords=[N.get(m,n) for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]
            minimum=224
            for epoch in range(1,61):
                N.put(m,VRAM_Buffer1_Offset=0)
                out=N.invoke(m,'PlayerChangeSize',a=83,x=0,y=0,p=0x21);minimum=min(minimum,out['minimum_SP'])
                assert bytes(m.ram[2][:1024])==frozen,(identity,kind,epoch,'source animation must freeze')
                assert coords==[N.get(m,n) for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]
                if epoch<60:assert N.get(m,'GameEngineSubroutine')==9 and N.get(m,'GuestPowerupActive')==1
            assert N.get(m,'GuestPowerupActive')==0 and N.get(m,'GameEngineSubroutine')==8
            assert N.get(m,'PlayerStatus')==kind+1 and N.get(m,'TimerControl')==0
            assert N.get(m,'NumberofLives')==2 and m.ram[2][actor+2]==flags
            rows.append(dict(identity=identity,item=kind,original_source_flags=flags,native_transformation_updates=60,native_status=kind+1,source_and_coordinates_frozen=True,actual_pickup_SFX_queued=True,minimum_SP=minimum))
        # Following ordinary native Main must resume this same powered actor.
        for epoch in range(24):
            N.put(m,FrameCounter=epoch,SavedJoypadBits=1,SavedJoypad1Bits=1,VRAM_Buffer1_Offset=0)
            N.invoke(m,'GameCoreRoutine',x=0,y=0)
            assert m.ram[2][actor+2]==7 and N.get(m,'NumberofLives')==2
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,ROM_memory_SHA256=q['expected_memory_only_ROM_SHA256'],scenarios=rows,scope='Both actors collect legal explicitly placed native mushroom then flower via complete PowerUpObjHandler, retaining original01 then07 flags. Real PlayerChangeSize/native dispatch completes each60update freeze and returns engine8 with power1/2, unchanged full1KB source/coordinates during freeze, then24 real GameCore calls retain upgrades. Genuine native powerup sound queue is nonzero; no acoustic fidelity, earned block/emulator/fullstage/life-reset claim.',bindings={str(f.relative_to(R)):sha(f) for f in [Path(__file__),G.O/'proposal.json',I.U.O/'proposal.json',I.U.O/'private-image.bin']})
    (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':
    try:main()
    except Exception as e:
        O.mkdir(exist_ok=True);(O/'negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
