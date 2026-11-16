"""Owning footer cold/header/retire and actual native actor-reuse boundaries."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_footer_ryu_1116 as R
import check_dkjr_carry_camera_route_1116 as Route
import check_dkjr_carry_camera_lifecycle_1116 as Old
import dkjr_footer_source_input_1116 as Input

C,N,W,L,Q=R.C,R.N,R.W,R.L,R.Q
H=lambda value:sha256(value).hexdigest()


def header_contact(seed):
    rows=[]
    for bank,byte in product((2,3),range(16)):
        m=Q.C.setup(seed)
        N.put(m,Player_X_Position=929&255,Player_PageLoc=929>>8,
            Player_Y_Position=106,Player_Y_HighPos=1,Player_State=2,Player_Y_Speed=0,TimerControl=0,ObjectOffset=3)
        Route.Cold.H.call(m,0xb24c)
        for field,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,Enemy_BoundBoxCtrl=5,
            Enemy_X_Position=944&255,Enemy_PageLoc=944>>8,Enemy_Y_Position=138,Enemy_Y_HighPos=1,
            Enemy_Y_Speed=1,Enemy_Y_MoveForce=0,PlatformCollisionFlag=3).items():m[W.address(m.bundle,field)+3]=value
        N.invoke(m,'RelativePlayerPosition',x=0);N.invoke(m,'HuFullBox',x=0)
        assert m[0x65b]==136
        m.ram[bank][0x1fe0+byte]^=1;before=tuple(bytes(r)for r in m.ram)
        seen=Counter();Base=N.NesMPU
        class Observed(Base):
            def step(self):
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if tag in(2,3):seen['private_execution']+=1
                if(tag,self.pc)==(199,0xac29):seen['native_position_callback']+=1
                if(tag,self.pc)==(128,0xb442):assert m[0x65b]==136
                return Base.step(self)
        with patch.object(N,'NesMPU',Observed):N.invoke(m,'RunLargePlatform',x=3)
        assert not seen['private_execution'] and tuple(bytes(r)for r in m.ram)==before,(bank,byte,seen)
        rows.append(dict(bank=bank,byte=byte,native_position_callback=seen['native_position_callback']))
    return dict(cases=len(rows),private_execution_and_WRAM_changes=0,
        native_fallback_may_still_contact=True,footer_restored=True)


def reuse(seed):
    rows=[]
    for slot,kind,relative in product((0,3,5),(37,40),(256,272,287)):
        m=Q.C.setup(seed)
        camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc')
        hero=camera+80;world=camera+relative
        N.put(m,Player_X_Position=hero&255,Player_PageLoc=hero>>8,Player_Y_Position=112,
            Player_Y_HighPos=1,Player_State=0,Player_Y_Speed=0,TimerControl=0,ObjectOffset=slot)
        Route.Cold.H.call(m,0xb24c)
        N.invoke(m,'RelativePlayerPosition',x=0);N.invoke(m,'HuFullBox',x=0)
        footer=m[0x65b]
        # Deliberately retain an old actor's same-slot passenger through the
        # actual native erase/init chain. Do not assume initialization clears it.
        m[0x566+slot]=slot;N.invoke(m,'EraseEnemyObject',x=slot)
        for field,value in dict(Enemy_ID=kind,Enemy_Flag=1,Enemy_X_Position=world&255,
            Enemy_PageLoc=world>>8,Enemy_Y_Position=footer+2,Enemy_Y_HighPos=1).items():m[W.address(m.bundle,field)+slot]=value
        N.invoke(m,'InitEnemyObject',x=slot)
        m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+slot]=5 if kind==37 else 6
        initialized=N.get(m,'PlatformCollisionFlag',slot);positions=0;box=None
        Base=N.NesMPU
        class Observed(Base):
            def step(self):
                nonlocal positions,box
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if(tag,self.pc)==(128,0xb43f):box=list(m[0x65c+slot*4:0x660+slot*4])
                if(tag,self.pc)==(199,0xac29):positions+=1
                return Base.step(self)
        with patch.object(N,'NesMPU',Observed):N.invoke(m,'RunLargePlatform',x=slot)
        row=dict(slot=slot,kind=kind,birth_relative_left=relative,
            after_actual_init_passenger=initialized,actual_native_positions=positions,
            after_first_LPC_passenger=N.get(m,'PlatformCollisionFlag',slot),box=box)
        rows.append(row)
        assert positions==0 and row['after_first_LPC_passenger']==255,('stale actor contact at forward spawn',row)
    return dict(cases=len(rows),actual_native_erase_and_init=True,
        initializer_alone_is_not_assumed_to_clear=True,rows=rows,
        scope='Declared stale-slot fixtures at actual DK forward birth window256..287 and current native32/48 widths; not natural births')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--input-kind',required=True,choices=('exact-6a3','bt91dc-reference-only'))
    args=ap.parse_args();public,binding=Input.normalize(args.public.read_bytes(),kind=args.input_kind)
    parent,_=C.Camera.proposal(public);raw,composition=C.proposal(parent);_,seed=Route.cold(raw)
    print('DKJR_FOOTER_LIFECYCLE_PHASE cold-retire',flush=True)
    cold=Old.cold_cases(seed,raw);retire=Old.retire_cases(seed,raw)
    print('DKJR_FOOTER_LIFECYCLE_PHASE native-contact-bad-headers',flush=True)
    headers=header_contact(seed)
    print('DKJR_FOOTER_LIFECYCLE_PHASE native-actor-reuse',flush=True)
    actors=reuse(seed)
    report=dict(passed=True,composition=composition,input_binding=binding,
        actual_cold_fault_retry=cold,actual_shared_retire=retire,header_contact=headers,actor_reuse=actors,
        output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_LIFECYCLE '+encoded,flush=True);print('DKJR_FOOTER_LIFECYCLE_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
