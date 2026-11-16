"""Explicit new temporary-footer path during pause and actual hosted growth."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_footer_ryu_1116 as R
import check_dkjr_carry_camera_route_1116 as Route
import dkjr_footer_source_input_1116 as Input

C,N,W,L,Q=R.C,R.N,R.W,R.L,R.Q
H=lambda value:sha256(value).hexdigest()


def check(seed,parent,candidate,timer,*,growth=False):
    base=Q.C.setup(seed)
    N.put(base,Player_State=2,Player_Y_Speed=0,Player_Y_Position=106,ObjectOffset=3)
    base[0x65b]=136;base[0xbe+3]=138;base[0x566+3]=3
    if growth:
        before=N.get(base,'PlayerStatus')
        for field,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=0,
            Enemy_X_Position=N.get(base,'Player_X_Position'),Enemy_PageLoc=N.get(base,'Player_PageLoc'),
            Enemy_Y_Position=N.get(base,'Player_Y_Position'),Enemy_Y_HighPos=1).items():base[W.address(base.bundle,field)+5]=value
        N.invoke(base,'NrPrepare',a=0,x=5);N.invoke(base,'HandlePowerUpCollision',a=0,x=5)
        assert N.get(base,'GuestPowerupActive') and N.get(base,'GameEngineSubroutine')==9
        # This hosted guest's native status is committed by its powerup
        # update, not synchronously by the collector. Do not force status.
        assert not N.get(base,'Enemy_Flag',5)
        timer=N.get(base,'TimerControl')
    else:N.put(base,TimerControl=timer)
    assert timer
    # The last ordinary body/contact cache is deliberately made eligible.
    # Growth itself above was granted through the actual collector callbacks.
    N.put(base,Player_State=2,Player_Y_Speed=0);base[0x65b]=136;base[0xbe+3]=138;base[0x566+3]=3
    models=[];ends=[];rows=[];cuts=[]
    for raw in(parent,candidate):
        m=R.mount(base,raw);events=Counter();lpc=None;restored=None;cut=None
        Base=N.NesMPU
        class Observed(Base):
            def step(self):
                nonlocal lpc,restored,cut
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if(tag,self.pc)==(186,0xbf5c):events['prepare']+=1
                if(tag,self.pc)==(186,0xbf83):events['finish']+=1
                if(tag,self.pc)==(128,0xb453):
                    lpc=dict(footer=m[0x65b],plane=m[0xbe+3],passenger=m[0x566+3],
                        state=N.get(m,'Player_State'),timer=N.get(m,'TimerControl'),PC=self.pc,SP=self.sp)
                if(tag,self.pc)==(128,0xb442):
                    restored=m[0x65b];cut=L.clone(m,self)
                return Base.step(self)
        with patch.object(N,'NesMPU',Observed):result=N.invoke(m,'RunLargePlatform',a=85,x=3,y=91,p=0x79)
        assert restored==136 and cut is not None
        models.append(m);ends.append(result);cuts.append(cut)
        rows.append(dict(events=dict(events),LPC=lpc,restored_footer=restored))
    assert rows[0]['events']==dict(prepare=1,finish=1) and rows[1]['events']=={}
    assert rows[0]['LPC']['footer']==136 and rows[1]['LPC']['footer']==138
    assert R.native_data(models[0])==R.native_data(models[1])
    assert tuple(ends[0][k]for k in('A','X','Y','P'))==tuple(ends[1][k]for k in('A','X','Y','P'))
    differing={at for at in range(0x15a,0x17b)if cuts[0][0][at]!=cuts[1][0][at]}
    outputs=[];accesses=Counter()
    for state,cpu in cuts:
        m,c=L.clone(state,cpu);Trace=R.Old.tracked(m,c,differing)
        with patch.object(N,'NesMPU',Trace):
            L.finish(m,c,(0x5b00,224))
            Q.frame(m,0)
        accesses.update(op for op,_,_ in m.smc_events)
        outputs.append((R.native_data(m),bytes(m[0x15a:0x17b]),m.contact_frame_registers))
    assert outputs[0]==outputs[1],('paused direct actual public and next Main continuation',timer,growth)
    return dict(timer=timer,growth_from_actual_collector=growth,old=rows[0],new=rows[1],
        complete_native_AXYP_private_maps_and_body_exact=True,
        intermediate_SMC=sorted(differing),SMC_first_consumer_accesses=dict(accesses),
        all_differing_fields_read_only_after_current_writer=True,next_actual_Main_all33_and_AXYP_exact=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--input-kind',required=True,choices=('exact-6a3','bt91dc-reference-only'))
    args=ap.parse_args();public,binding=Input.normalize(args.public.read_bytes(),kind=args.input_kind)
    parent,_=C.Camera.proposal(public);candidate,composition=C.proposal(parent);_,seed=Route.cold(candidate)
    rows=[check(seed,parent,candidate,timer)for timer in(1,254,255)]
    rows.append(check(seed,parent,candidate,0,growth=True))
    report=dict(passed=True,composition=composition,input_binding=binding,rows=rows,
        scope='Declared eligible cached contact; one actual mature-actor collector fixture creates hosted growth. No natural item/full-route/native claim',output_files=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_PAUSED_DIRECT '+encoded,flush=True);print('DKJR_FOOTER_PAUSED_DIRECT_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
