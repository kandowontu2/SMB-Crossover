"""Declared carry/camera fixtures and real native-wrapper ABI over actual6a3."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_carry_camera_route_1116 as Route

C, Cold, N = Route.C, Route.Cold, Route.N
H = lambda value: sha256(value).hexdigest()


def private(m, pc, **kw):
    return Cold.H.call(m, pc, **kw)


def prepare(seed, *, camera=848, delta=1, ready=215, state=1, distance=0):
    m=N.fork(seed)
    old_camera=(camera-delta)&65535
    world=(camera+80)&65535
    N.put(m,SelectedCharacter=40,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
        TimerControl=0,Player_X_Position=world&255,Player_PageLoc=world>>8,
        Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,
        ScreenLeft_X_Pos=old_camera&255,ScreenLeft_PageLoc=old_camera>>8,ObjectOffset=2)
    # Explicit source component records, not a controller-earned fixture.
    for i in range(64):
        if 4<=i<12:continue
        m.ram[2][0x200+4*i]=100+i%4
        m.ram[2][0x203+4*i]=(32+3*i)&255
    private(m,0xb24c);private(m,0xbad2)
    r=m.ram[2]
    r[0x6b]=r[0x6c]=state;r[0x76]=(r[0x210]-distance)&255;r[0x7b]=24
    r[0x437]=ready;r[0x56]=96;r[0x8f6]=0x5a
    N.put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
    for name,value in (('Enemy_Flag',1),('Enemy_ID',37),('Enemy_Y_Position',208),('Enemy_Y_HighPos',1)):
        m[N.address(m.bundle,name)+2]=value
    return m


def wrapper_snapshot(m,c):
    return dict(AXY=(c.a,c.x,c.y),P=c.p,SP=c.sp,
        scratch=bytes(m[3:11]),temps=bytes(m[0x6c63:0x6c68]),
        SMC=bytes(m[0x15a:0x17b]),maps=tuple(m.rawtags))


def public(m,p=0x31,*,entry='PositionPlayerOnVPlat'):
    entered=[];returned=[];helper=Counter();minimum=255;return_A_store=False;return_token=None
    Base=N.NesMPU
    class Observed(Base):
        def step(self):
            nonlocal minimum,return_A_store,return_token
            minimum=min(minimum,self.sp)
            tag=m.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1
            if (tag,self.pc)==(199,0xac2a):
                entered.append(wrapper_snapshot(m,self))
                ret=m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1
                return_token=(ret&65535,(self.sp+2)&255)
            if return_token==(self.pc,self.sp):
                returned.append(wrapper_snapshot(m,self));return_token=None
            if returned and self.pc==0x16e:
                assert bytes(m[0x16e:0x171])==bytes.fromhex('8d7901')
                assert m[0x178]==0xa9 and self.a==returned[-1]['AXY'][0]
                return_A_store=True
            if (tag,self.pc)==(3,0xb6a5):helper['carry_entry']+=1
            if (tag,self.pc)==(3,0xb770) and H(m.bundle['raw'])==C.CANDIDATE:helper['reconcile_entry']+=1
            return Base.step(self)
    with patch.object(N,'NesMPU',Observed):
        result=N.invoke(m,entry,a=83,x=2,y=91,p=p)
    assert len(entered)==len(returned)==1
    a,b=entered[0],returned[0]
    assert a['AXY']==b['AXY'] and a['P']|0x30==b['P']|0x30
    assert b['SP']==a['SP']+2
    for key in ('scratch','temps','maps'):assert a[key]==b[key],(key,a[key],b[key])
    # SafereturnA+1(179) is the nested farcall result, not a retained input.
    # AC29 is RTS directly to16E STA179; it overwrites that byte BEFORE178
    # can read it. Do not silently mask it: prove this actual path and require
    # every33 bytes exact again at the complete public farcall return.
    inner_differences={i for i,(x,y) in enumerate(zip(a['SMC'],b['SMC'])) if x!=y}
    assert inner_differences<={0x179-0x15a} and return_A_store
    expected_SMC=bytearray(a['SMC']);expected_SMC[0x179-0x15a]=result['A']
    assert bytes(m[0x15a:0x17b])==bytes(expected_SMC),('Complete public SMC33',bytes(expected_SMC),bytes(m[0x15a:0x17b]))
    return result,dict(helper),minimum


def check_pair(parent_seed,candidate_seed,case,p=0x31):
    pair=[prepare(seed,**case) for seed in (parent_seed,candidate_seed)]
    before=[bytes(m.ram[2][:0x900]) for m in pair]
    results=[public(m,p) for m in pair]
    assert tuple(results[0][0][k] for k in 'AXYP')==tuple(results[1][0][k] for k in 'AXYP')
    a,b=pair
    old,new=bytes(a.ram[2][:0x900]),bytes(b.ram[2][:0x900])
    state,distance=case.get('state',1),case.get('distance',0)
    delta,ready=case.get('delta',1),case.get('ready',215)
    fatal=state in (3,4) and distance>=24
    accepted=ready==215 and -8<=delta<=8
    assert b.ram[2][0x6b]==(5 if fatal else 1 if accepted else state)
    assert b.ram[2][0x76]==before[1][0x76] and b.ram[2][0x7b]==24
    assert b.ram[2][0x56]==96 and b.ram[2][0x8f6]==0x5a
    if fatal:
        assert results[1][1].get('reconcile_entry',0)==0
        assert before[1][0x210:0x230]==new[0x210:0x230]
        allowed={0x8f6}
        assert all(x==y or i in allowed for i,(x,y) in enumerate(zip(old,new)))
    elif accepted:
        assert results[1][1].get('reconcile_entry',0)==1
        assert new[0x210:0x230]==old[0x210:0x230]
        for i in range(64):
            if 4<=i<12:continue
            at=0x203+4*i
            assert new[at]==((before[1][at]-delta)&255 if before[1][at-3]!=255 else before[1][at])
        expected_camera=case.get('camera',848)
        assert int.from_bytes(new[0x435:0x437],'little')==expected_camera
        allowed={0x435,0x436,0x437,0x438,0x8f1,0x8f6}|{0x203+4*i for i in range(64)}
        differences={i for i,(x,y) in enumerate(zip(old,new)) if x!=y}
        assert differences<=allowed,sorted(differences-allowed)
        settled=bytes(b.ram[2][:0x900])
        again=private(b,0xbae5)
        assert again.p&1
        after=bytes(b.ram[2][:0x900])
        assert all(x==y or i==0x438 for i,(x,y) in enumerate(zip(settled,after)))
        assert after[0x438]==0
    else:
        assert results[1][1].get('reconcile_entry',0)==1
        assert new[0x200:0x300]==before[1][0x200:0x300]
        assert new[0x435:0x438]==before[1][0x435:0x438]
    return dict(parent_cycles=results[0][0]['CPU'],candidate_cycles=results[1][0]['CPU'],
                minimum_SP=min(results[0][2],results[1][2]))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent',type=Path,required=True)
    args=ap.parse_args()
    parent=args.parent.read_bytes();candidate,composition=C.proposal(parent)
    assert C.inverse(candidate)==parent
    print('DKJR_CAMERA_COMPONENT_PHASE cold',flush=True)
    parent_open,parent_seed=Route.cold(parent)
    candidate_open,candidate_seed=Route.cold(candidate)
    assert parent_seed.bundle['raw']==parent and candidate_seed.bundle['raw']==candidate
    counts=Counter();costs=[];minimum=255
    print('DKJR_CAMERA_COMPONENT_PHASE carry-camera',flush=True)
    for camera in (0,255,256,65535):
        for delta in (*range(-8,9),-9,9,-32,32):
            for ready in (0,215):
                row=check_pair(parent_seed,candidate_seed,dict(camera=camera,delta=delta,ready=ready))
                costs.append(row);minimum=min(minimum,row['minimum_SP']);counts['ground_camera']+=1
    for state in (3,4):
        for distance in (0,23,24,25):
            for delta in (-8,0,1,8,9):
                row=check_pair(parent_seed,candidate_seed,dict(state=state,distance=distance,delta=delta))
                costs.append(row);minimum=min(minimum,row['minimum_SP']);counts['air_fall_threshold']+=1
    for p in range(256):
        if not p&0x20:continue
        for state,distance in ((1,0),(4,23),(4,24)):
            row=check_pair(parent_seed,candidate_seed,dict(state=state,distance=distance),p)
            costs.append(row);minimum=min(minimum,row['minimum_SP']);counts['all_valid_P_public_wrapper']+=1
    print('DKJR_CAMERA_COMPONENT_PHASE headers-foreign',flush=True)
    for bank in (2,3):
        for i in range(16):
            m=prepare(candidate_seed);m.ram[bank][0x1fe0+i]^=1
            before=bytes(m.ram[2][:0x900]);_,entered,sp=public(m)
            assert not entered.get('carry_entry') and bytes(m.ram[2][:0x900])==before
            minimum=min(minimum,sp);counts['full_header_reject']+=1
    for owner in range(256):
        if owner==40:continue
        m=prepare(candidate_seed);N.put(m,SelectedCharacter=owner,Z2Variant=0)
        # This is the actual typed post-position callback. Some foreign
        # characters replace the upstream PositionPlayerOnVPlat route, so
        # directly test its selected!=40 early return rather than assuming
        # every character's different platform handler reaches AC2A.
        before=bytes(m.ram[2][:0x900]);_,entered,sp=public(m,entry='Z2RefreshPlatformBody')
        assert not entered.get('carry_entry') and bytes(m.ram[2][:0x900])==before
        minimum=min(minimum,sp);counts['foreign_owner_reject']+=1
    report=dict(passed=True,composition=composition,parent_cold=parent_open,candidate_cold=candidate_open,
        cases=dict(counts),minimum_SP=minimum,
        public_wrapper_AXYP_R0_RgTemps_SMC33_maps_exact=True,
        inner_SafereturnA_179=dict(dead_nested_result=True,exact_current_overwrite='16E:8D7901',
            before_read='178:A9',complete_public_return_all33_exact=True),
        CarryReason_only_removed_write=True,no_blanket_private_RAM_mask=True,
        source_cost=dict(parent_min=min(x['parent_cycles'] for x in costs),parent_max=max(x['parent_cycles'] for x in costs),
            candidate_min=min(x['candidate_cycles'] for x in costs),candidate_max=max(x['candidate_cycles'] for x in costs),
            delta_min=min(x['candidate_cycles']-x['parent_cycles'] for x in costs),
            delta_max=max(x['candidate_cycles']-x['parent_cycles'] for x in costs)),
        fixtures='Explicit declared source component state; not ordinary earned route or native cadence',
        reached_ISR_pending=True,ordinary_route_separate=True,output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CAMERA_COMPONENTS '+encoded,flush=True)
    print('DKJR_CAMERA_COMPONENTS_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
