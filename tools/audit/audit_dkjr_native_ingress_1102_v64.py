"""Real native GameCore callback census for the private DK Jr image.

Records missing actual routes; it never patches a shared gate to manufacture
admission. Item positions/metadata are explicit isolated legal fixtures.
"""
import collections,json
from pathlib import Path
import check_dkjr_native_item_status_1102_v61 as P
A,R,O,W,N=P.A,P.R,P.O,P.W,P.N


def main():
    b,seed,L,q=P.fixture();base=N.NesMPU;counts=collections.Counter();minimum=255
    names=['LmBoundingBoxGate','BoundingBoxCore','PowerUpObjHandler','NrPickupCollision','NrPickup','MarioSourcePowerupCollision','GuestBeginPowerup']
    points={(W.address(b,n),((W.location(b,n)-16)//8192)|128):n for n in names}
    class Trace(base):
        def step(self):
            nonlocal minimum
            minimum=min(minimum,self.sp)
            if self.pc>=0x8000:
                bank=self.memory.rawtags[(self.pc-0x8000)//8192]
                if (self.pc,bank)in points:counts[points[self.pc,bank]]+=1
                if bank==3 and 0xa000<=self.pc<0xa072 and(self.pc-0xa000)%3==0:counts['private-row-'+str((self.pc-0xa000)//3)]+=1
            return super().step()
    rows=[];N.NesMPU=Trace
    try:
        for kind in [None,0,1,2,3]:
            m=N.fork(seed);counts.clear();minimum=255
            P.P.direct(m,L['DkjrNativeFruitReset'])
            for i in range(6):m[W.address(b,'Enemy_Flag')+i]=0
            N.put(m,FrameCounter=1,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
            if kind is not None:
                for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind,Enemy_X_Position=48,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9).items():m[W.address(b,field)+5]=value
                P.P.direct(m,L['DkNativePrepare'],x=5)
            source=bytes(m.ram[2][:0x800]);out=N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
            rows.append(dict(item_kind=kind,actual_calls=dict(counts),minimum_SP=minimum,
                lives=N.get(m,'NumberofLives'),engine=N.get(m,'GameEngineSubroutine'),timer=N.get(m,'TimerControl'),
                item_flag=N.get(m,'Enemy_Flag',5),native_star=N.get(m,'StarInvincibleTimer'),
                item_collected=bool(kind is not None and not N.get(m,'Enemy_Flag',5)),
                private_fullbox_actual=counts['private-row-16'],private_maturity_actual=counts['private-row-23'],private_pickup_actual=counts['private-row-24']))
            assert N.get(m,'NumberofLives')==2
    finally:N.NesMPU=base
    blockers=[]
    if not rows[0]['private_fullbox_actual']:blockers.append('Actual native LmBoundingBoxGate does not reach private16; proposed source bound FullBox is not yet actual raw40 collision authority.')
    if any(not z['private_maturity_actual']or not z['private_pickup_actual']for z in rows[1:]):blockers.append('Actual native item callbacks do not complete private23/24 for everytype; direct63 collector parity is not shared ingress qualification.')
    out=dict(passed=True,qualification_complete=False,ROM_written=False,native_owner_admitted=False,
        historical_v65_matching_header_fixture=True,isolated_legal_fixture=True,scenarios=rows,concrete_blockers=blockers,
        scope='Complete real GameCore executes unchanged shared/native code against the private compiled image. No source hit/powerup/collection outcome is seeded; explicit native item actor/metadata initial positions are legal fixtures. Observed missing routes remain failures of admission readiness, not functional CLR policies. Final latestPrince/Bub source binding and root sharedgrant required before native candidate.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-items-v60.s',O/'native-items-v60.bin',O/'native-items-v60-layout.json',O/'native-collector-v63-CPU.json',R/'src/object.s',R/'src/new_roster_dispatch.s']})
    (O/'native-ingress-v64-census.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
