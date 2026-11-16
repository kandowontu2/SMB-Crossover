"""Declared private carry rejection/lifecycle boundaries; no ordinary-route claims."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_carry_camera_components_1116 as K

Route,C,N=K.Route,K.C,K.N
H=lambda value:sha256(value).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent',type=Path,required=True)
    args=ap.parse_args()
    parent=args.parent.read_bytes();candidate,composition=C.proposal(parent)
    _,old_seed=Route.cold(parent);_,new_seed=Route.cold(candidate)
    assert old_seed.bundle['raw']==parent and new_seed.bundle['raw']==candidate
    counts=Counter();screen_differences=[]
    def pair(field,value,expected,*,slot=2):
        states=[];returns=[]
        for seed in (old_seed,new_seed):
            m=K.prepare(seed,delta=0)
            if field=='source':m.ram[2][0x6b]=m.ram[2][0x6c]=value
            elif field in ('GameEngineSubroutine','TimerControl','Player_Y_HighPos','Player_Y_Position'):
                N.put(m,**{field:value})
                if field=='Player_Y_Position':m[N.address(m.bundle,'Enemy_Y_Position')+2]=(value+32)&255
            elif field=='slot':
                for i in range(6):m[N.address(m.bundle,'Enemy_Flag')+i]=0
                if slot<6:
                    for name,v in (('Enemy_Flag',1),('Enemy_ID',37),('Enemy_Y_Position',208),('Enemy_Y_HighPos',1)):
                        m[N.address(m.bundle,name)+slot]=v
            else:m[N.address(m.bundle,field)+2]=value
            c=K.private(m,0xb6a5,x=slot,p=0xf1)
            returns.append(bool(c.p&1));states.append(bytes(m.ram[2][:0x900]))
        assert returns==[expected,expected],(field,value,slot,returns)
        differences={i for i,(a,b) in enumerate(zip(*states)) if a!=b}
        assert differences<={0x8f6},(field,value,sorted(differences))
        counts[field]+=1
    print('DKJR_CAMERA_GUARDS_PHASE rejected-fields',flush=True)
    for value in range(256):
        pair('source',value,value in (1,3,4))
        pair('GameEngineSubroutine',value,value==8)
        pair('TimerControl',value,value==0)
        pair('Enemy_ID',value,0x24<=value<0x2d)
        pair('Enemy_Flag',value,value!=0)  # Preserve old manual-ABI negative-flag behavior.
        pair('Enemy_Y_HighPos',value,value==1)
        pair('Player_Y_HighPos',value,value==1)
        pair('Player_Y_Position',value,value<224)
        pair('slot',value,value<6,slot=value)
    print('DKJR_CAMERA_GUARDS_PHASE rejected-representation',flush=True)
    for delta in (0,1):
        for relative in (0,7,8,231,232,255):
            pair_m=[];outputs=[];before=[]
            for seed in (old_seed,new_seed):
                m=K.prepare(seed,delta=delta)
                world=848+relative
                N.put(m,Player_X_Position=world&255,Player_PageLoc=world>>8)
                before.append(bytes(m.ram[2][:0x900]))
                c=K.private(m,0xb6a5,x=2)
                outputs.append(bool(c.p&1));pair_m.append(m)
            assert outputs==[8<=relative<232]*2
            a,b=pair_m
            immediate={i for i,(x,y) in enumerate(zip(a.ram[2][:0x900],b.ram[2][:0x900])) if x!=y}
            if not outputs[0] and immediate:
                # Record rather than hide early legal camera transport on an
                # unrepresentable ground anchor. Both paths still returnC0.
                screen_differences.append(dict(relative=relative,delta=delta,
                    differing_addresses=sorted(immediate),source_X_before=before[1][0x213],
                    source_X_old=a.ram[2][0x213],source_X_new=b.ram[2][0x213]))
            immediate_old=bytes(a.ram[2][:0x900])
            for m in pair_m:assert K.private(m,0xbae5).p&1
            # Rejected anchors converge after normal camera maintenance.
            # Valid anchors deliberately differ: old code shifts an already
            # imported player twice; candidate retains the corrected anchor.
            differences={i for i,(x,y) in enumerate(zip(a.ram[2][:0x900],b.ram[2][:0x900])) if x!=y}
            allowed={0x438,0x8f1}
            if outputs[0]:
                allowed|={0x213+4*i for i in range(8)}
                assert b.ram[2][0x213]==relative-8
                for i in range(8):
                    at=0x213+4*i
                    assert a.ram[2][at]==((immediate_old[at]-delta)&255
                        if immediate_old[at-3]!=255 else immediate_old[at])
            assert differences<=allowed,(relative,delta,sorted(differences))
            counts['screen_representation']+=1
    lifecycle=[]
    for seed in (old_seed,new_seed):
        m=K.prepare(seed)
        K.private(m,0xbdc4)
        assert m.ram[2][0x8fe]==0
        result=K.private(m,0xd65e)
        assert not result.p&1 and m.ram[2][0x8fe]==0
        fresh=K.private(m,0xbd45)
        assert m.ram[2][0x8fe]==1
        ready=K.private(m,0xbfc1)
        assert ready.p&1 and m.ram[2][0x8fe]==2
        assert int.from_bytes(m.ram[2][0x435:0x437],'little')==848
        lifecycle.append(dict(reset_ready0=True,Main_rejects_unconstructed=True,
            constructor_pending1=True,actual_anchor_ready2=True,cache_sync=True))
    report=dict(passed=True,composition=composition,cases=dict(counts),lifecycle=lifecycle,
        unrepresentable_ground_anchor_immediate_camera_transport=screen_differences,
        rejection_C_results_preserved=True,rejected_anchor_next_camera_prefix_converges=True,
        accepted_anchor_old_double_shift_explicitly_not_equivalent=True,
        manual_negative_actor_flag_behavior_preserved=True,
        scope='Declared primitive fixtures, not ordinary inputs/native/retire-UI proof',
        output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CAMERA_GUARDS '+encoded,flush=True)
    print('DKJR_CAMERA_GUARDS_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
