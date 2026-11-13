"""Qualify a descending-only sizing lead without modifying any ROM bytes."""
from hashlib import sha256
from itertools import product
import json
from unittest.mock import patch

import check_dkjr_platform_contact_1113 as Q

P,H,N,W,L,T,C=Q.P,Q.H,Q.N,Q.W,Q.L,Q.T,Q.C


def main():
    parent=(P.B.R/'build/metal-flower-native-1112/candidate.nes').read_bytes()
    assert sha256(parent).hexdigest()==T.PARENT
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    source=T.F.SOURCE.read_text()
    source=P.once(source,'    lda EnemyID,x\n    cmp #$25\n    bcc PlatformFallback',
        '    lda EnemyID,x\n    sbc #$25\n    ora $8f,x\n    bmi PlatformFallback')
    source=P.once(source,'    adc #2\n    bcs DkContactReady\n    sta PlayerBottom',
        '    adc #2\n    sta PlayerBottom')
    linked=H.T.assemble(source,T.F.LAYOUT)
    assert linked['used']==dict(NATIVE=44,RESTORE=10,GENERIC_A=21,GENERIC_B=24)
    # Exact existing early player rejection executes before native bbox reads.
    at=W.location(seed.bundle,'CheckPlayerVertical')
    guard=parent[at:at+17]
    assert guard==bytes.fromhex('ada005c9f0b009a4a488d004a5bdc9d060')
    shapes=0;overflow=[];offsets=set()
    for state,facing,climb,y in product(range(1,6),(0,1),(0,1,2),range(256)):
        m=L.clone(seed)
        m.ram[2][0x6b]=state;m.ram[2][0x6d]=facing;m.ram[2][0x71]=climb
        N.put(m,Player_Y_Position=y,Player_Y_HighPos=1)
        N.invoke(m,'HuFullBox',x=0)
        footer=m[0x65b];offsets.add((footer-y)&255)
        if footer>=254:
            assert y>=208,(state,facing,climb,y,footer)
            overflow.append((state,facing,climb,y,footer))
        shapes+=1
    assert overflow
    clipped=0;reads=0
    for state,facing,climb,y,footer in overflow:
        for slot,high,hidden in product((0,5),(0,1,2),(None,240,255)):
            C.SLOT=slot;base=C.setup(seed)
            N.put(base,Player_Y_Position=y,Player_Y_HighPos=high,ObjectOffset=slot)
            N.invoke(base,'GetPlayerOffscreenBits',x=0)
            if hidden is not None:N.put(base,Player_OffscreenBits=hidden)
            base[0x65b]=footer
            C.field(base,'Enemy_Y_Position',255)
            C.field(base,'Enemy_Y_Speed',1)
            outcomes=[]
            for wrapped in(False,True):
                m=L.clone(base);m[0x65b]=(footer+2)&255 if wrapped and footer<255 else footer
                Bus=type(m)
                class Watch(Bus):
                    def __getitem__(self,at):
                        nonlocal reads
                        if isinstance(at,int)and at==0x65b and self.box_read_watch and footer==254:reads+=1
                        return super().__getitem__(at)
                m.__class__=Watch;m.box_read_watch=True
                result=Q.direct(m,0xb453,x=slot)
                m.box_read_watch=False;m[0x65b]=footer
                outcomes.append((Q.observables(m),tuple(result[k]for k in('A','X','Y','P','SP'))))
            if outcomes[0]!=outcomes[1]:
                shape=(state,facing,climb,y,footer,slot,high,hidden)
                assert shape==(3,0,2,239,254,0,0,None),shape
                print('DKJR_DESCENDING_OVERFLOW_NEGATIVE '+json.dumps(dict(
                    passed=True,proposed_sampler_safe=False,mandatory_overflow_guard=True,
                    parent_SHA256=sha256(parent).hexdigest(),actual_source_box_cases=shapes,
                    counterexample=dict(source_state=state,facing=facing,climb_phase=climb,
                        native_Y=y,source_footer=footer,slot=slot,native_Y_high=high,
                        hidden_override=hidden,old_AXYPSP=outcomes[0][1],wrapped_AXYPSP=outcomes[1][1]),
                    exact_CheckPlayerVertical_bytes=guard.hex(),ROM_written=False,outputs_written=0,
                    scope='Rejected sizing proposal. Typed source box and real native offscreen calculation; joint scene reachability is not claimed. No overflow branch removed from any candidate.'),separators=(',',':')),flush=True)
                return
            clipped+=1
    assert reads==0
    print('DKJR_DESCENDING_OVERFLOW '+json.dumps(dict(passed=True,
        parent_SHA256=sha256(parent).hexdigest(),proposed_source_SHA256=sha256(source.encode()).hexdigest(),
        proposed_fits=linked['used'],actual_legal_box_cases=shapes,actual_footer_offsets=sorted(offsets),
        overflow_boxes=len(overflow),overflow_all_native_Y_at_least_D0=True,
        hidden_high_and_slot_parity_cases=clipped,actual_LPC_bbox_reads_on_rejected_paths=reads,
        exact_CheckPlayerVertical_bytes=guard.hex(),ROM_written=False,outputs_written=0,
        scope='Sizing lead only: actual source box/early native rejection. Stale-box ordering and ISR observations remain pending; no branch removed from the candidate.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
