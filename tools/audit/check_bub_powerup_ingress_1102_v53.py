"""Exercise the complete native powerup overlap/collection ingress privately."""
from collections import Counter
import json
from pathlib import Path
import check_bub_original_upgrades_1102_v49 as Q
import prepare_bub_original_upgrades_1102_v51 as U
from check_tmnt_render_oa import location
from prepare_selected_native_packet_v1 import sha
R=Q.R;O=R/'build/bub-upgrades-root-ingress-1102-v53';N=Q.N;address=Q.address

def main():
    O.mkdir(exist_ok=True);prior=Q.U;Q.U=U
    try:old,new,route,q=Q.bundles()
    finally:Q.U=prior
    proof=R/'build/bub-upgrades-root-qualification-1102-v52/receipt.json';qualified=json.loads(proof.read_text());assert qualified['passed']and qualified['public_pickup_row']==24
    for name,h in qualified['bindings'].items():assert sha(R/name)==h,name
    actual=N.NesMPU;calls=Counter();points={}
    for name in['PowerUpObjHandler','NrPickupCollision','JnCollisionDispatch','HuMature','HandlePowerUpCollision','NrPickup','JnPickupDispatch','HuPickup','HuFullBox','M3CollectPickup']:
        points[address(new,name),((location(new,name)-16)//8192)|128]=name
    points[q['labels']['BbNativePickup'],3]='BbNativePickup24'
    class Trace(actual):
        def step(self):
            if self.pc>=0x8000:
                name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if name:calls[name]+=1
            return super().step()
    episodes=[];N.NesMPU=Trace
    try:
        for identity in[0,1]:
            seed=Q.Q.fresh(new,route,identity);Q.L.E.main_fields(seed)
            N.put(seed,NmiDisable=255,TimerControl=1,Player_Rel_XPos=64,Player_Rel_YPos=176)
            N.invoke(seed,'HuFullBox',a=83,x=0,y=0,p=0x21)
            for kind in range(4):
                m=N.fork(seed);actor=0x42 if identity else 0x2e;slot=5;N.put(m,ObjectOffset=slot)
                for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=64,Enemy_PageLoc=0,Enemy_Y_Position=191,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=1).items():m[address(new,field)+slot]=value
                before=dict(calls);out=N.invoke(m,'PowerUpObjHandler',a=83,x=slot,y=0,p=0x21);delta={k:v-before.get(k,0)for k,v in calls.items()if v!=before.get(k,0)}
                row=dict(identity=identity,kind=kind,CPU=out['CPU'],minimum_SP=out['minimum_SP'],actual_calls=delta,source_flags=m.ram[2][actor+2],native_flag=N.get(m,'Enemy_Flag',slot),native_status=N.get(m,'PlayerStatus'),engine=N.get(m,'GameEngineSubroutine'),star=N.get(m,'StarInvincibleTimer'),floaty=N.get(m,'FloateyNum_Control',slot),lives=N.get(m,'NumberofLives'))
                episodes.append(row)
                if not all(delta.get(name,0)>0 for name in['NrPickupCollision','HuMature','HandlePowerUpCollision','NrPickup','HuPickup','BbNativePickup24']):
                    (O/'negative.json').write_text(json.dumps(dict(passed=False,episodes=episodes,scope='Explicit legal CPU item overlap fixture; no emulator/earned block claim.'),indent=2)+'\n');raise AssertionError(row)
                assert not row['native_flag']and row['lives']==2,row
                if kind<2:assert row['source_flags']==(1 if kind==0 else 6),row
                elif kind==2:assert row['star']==35,row
                else:assert row['floaty']==11,row
    finally:N.NesMPU=actual
    result=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,ROM_memory_SHA256=q['expected_memory_only_ROM_SHA256'],actual_public_pickup_row=24,native_side_row14_unchanged=True,episodes=episodes,scope='Both identities execute real complete PowerUpObjHandler→native mature/rectangle overlap→NrPickup/HuPickup→original-upgrade adapter24 and genuine native collector for all4types. Mushroom/flower original source flag changes, item erase/native status; star35/1up floaty11. Explicit legal CPU item placements, not earned block/controller/maturity-emergence or audio fidelity. Prior v52 imported case key actual_resident_row14 was a stale observation label; its actual target expression and authoritative public_pickup_row field are24. This successor records the correct row explicitly.',bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),proof,U.O/'proposal.json',U.O/'private-image.bin']})
    (O/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
