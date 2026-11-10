"""Small changed-policy ABI/lifecycle/vector qualification; stdout only."""
from collections import Counter
from hashlib import sha256
import json

import check_thomas_powerup_progression_1110 as P

C,W,N,L=P.C,P.W,P.N,P.L


def prepared(seed,age=0,tier=0):
    m=L.clone(seed);m.raw_page(2,2)
    N.put(m,CurrentBankC=2,NmiDisable=255,GuestPowerupActive=1,GuestPowerupAge=age,
        GuestPowerupOld=tier,GuestPowerupDisplay=tier,GuestPowerupTarget=tier+1,
        GameEngineSubroutine=9,TimerControl=255)
    return m


def main():
    parent=P.Ex.proposal(P.Route.A5.proposal(W.ROM.read_bytes())[0])[0]
    image,kernel,cookie,record=P.proposal(parent)
    b=W.Symbols.bundle();b['raw']=image
    row=next(r for r in C.Starts.C.inventory(image)['rows'] if r['name']=='THOMAS')
    _,seed=C.cold(b,row);cases=Counter()
    for slot in (4,5):
      for kind in range(4):
       for state in (0,6,128,192):
        m=L.clone(seed);m[W.address(b,'PowerUpType')+slot]=kind;m[W.address(b,'Enemy_State')+slot]=state
        c=L.call(m,'NrPickupCollision',a=83,x=slot,y=46,p=0xf1)
        assert bool(c.p&1)==bool(kind>=2 or state&128) and c.x==slot and c.y==46
        cases['native_maturity_kind_state_slots4_5']+=1
    for age in (0,59):
      for tier in (0,1):
       for flags in (0x31,0xf1):
        expected,actual=prepared(seed,age,tier),prepared(seed,age,tier)
        a=L.call(expected,'GuestPowerupUpdate',a=83,x=4,y=46,p=flags)
        z=L.call(actual,'HuPowerup',a=83,x=4,y=46,p=flags)
        assert (a.a,a.x,a.y,a.p,a.sp)==(z.a,z.x,z.y,z.p,z.sp)
        assert L.app(expected)==L.app(actual)
        cases['ordinary_and_terminal_native_update_ABI_pairs']+=1
    for bank in (2,3):
        m=prepared(seed);m.ram[bank][0x1fe0+7]^=1
        before=L.app(m);c=L.call(m,'HuPowerup');assert not c.p&1 and L.app(m)==before
        cases['each_header_representative_fault_reject']+=1
    for owner,lives in ((0,2),(10,3)):
        m=prepared(seed);N.put(m,SelectedCharacter=owner,NumberofLives=lives)
        # The typed Thomas veneer is reached via its unchanged native entry;
        # HuPowerup intentionally dispatches to a different owner's code.
        target=W.address(b,'ThServiceVeneers')+33*3
        m[W.address(b,'SafecallA_SMC')+1]=83
        m[W.address(b,'FarcallJmpTarget_SMC')+1]=target&255
        m[W.address(b,'FarcallJmpTarget_SMC')+2]=target>>8
        c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a=213;c.x,c.y,c.p,c.sp=4,46,0x31,224;c.stPushWord(0x5aff)
        before=L.app(m);L.finish(m,c,(0x5b00,224));assert not c.p&1 and L.app(m)==before
        cases['foreign_owner_and_life_context_reject']+=1
    m=prepared(seed);N.put(m,GamePauseStatus=1);m.controller_pad=0
    P.Route.Frames.frame(m);assert N.get(m,'GuestPowerupAge')==0
    N.put(m,GamePauseStatus=0);P.Route.Frames.frame(m);assert N.get(m,'GuestPowerupAge')==1
    cases['actual_Main_pause_then_resume']+=1
    L.SAMPLES.clear();L.SAMPLE_KEYS.clear();L.PATHS.clear();L.DEEPEST=None
    wanted={0xb5b2,0xb5be,0xb5c0,0xb5cf};seen=set()
    for name,age in (('NrPickupCollision',0),('HuPowerup',0),('HuPowerup',59)):
        m=prepared(seed,age);m[W.address(b,'PowerUpType')+4]=0;m[W.address(b,'Enemy_State')+4]=128
        c=L.start(m,name,a=83,x=4,y=46,p=0x31)
        def observe(mem,cpu):
            if cpu.pc in wanted and cpu.pc not in seen and mem.rawtags[1]==3:
                seen.add(cpu.pc);q,d=L.clone(mem,cpu);L.SAMPLES.append(('changed_Thomas_policy',(0x5b00,224),q,d))
        L.finish(m,c,(0x5b00,224),observe)
    assert seen==wanted
    vectors=L.irq_checks(parent)
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,output_files=0,ROM_written=False,
        proposal_ROM_SHA256=sha256(image).hexdigest(),cases=dict(cases),representative_vectors=vectors,
        scope='Only changed maturity/progression policies:32 input cases,8 native update pairs, representative header/owner/life/pause rejection and four reached instruction contexts with real native vectors. Separate checker proves actual naturally earned first mushroom.')),flush=True)


if __name__=='__main__':main()
