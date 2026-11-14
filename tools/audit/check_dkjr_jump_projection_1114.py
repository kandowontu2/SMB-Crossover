"""Declared jump/contact primitive: original fractional rise vs native sign."""
import json
import argparse
from unittest.mock import patch

import replay_dkjr_final_handoff_1114 as F

G,T=F.Gate,F.T
Q,P,H,N,W,L,C=G.Q,G.P,G.H,G.N,G.W,G.L,G.C


def view(m):
    r=m.ram[2]
    return dict(y=N.get(m,'Player_Y_Position'),source_y=r[0x210],source=r[0x6b],prior=r[0x6c],
        native_vy=N.get(m,'Player_Y_Speed'),native_state=N.get(m,'Player_State'),
        age=r[0x7e],fraction=r[0x7f],acceleration=r[0x82]+256*r[0x83],
        jump_impulse=r[0x86]+256*r[0x87],facing=r[0x6d],direction=r[0x54],
        footer=m[0x65b],top=N.get(m,'Enemy_Y_Position',C.SLOT))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--differential',action='store_true');args=ap.parse_args()
    parent,raw=F.load_inputs();e73=T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);C.SLOT=3
    base=C.setup(Q.mounted(seed,raw))
    C.field(base,'Enemy_Y_Speed',1)
    # Ordinary supported Left is an input preparation, not a state seed.
    for _ in range(16):
        C.source_step(base,2)
        if base.ram[2][0x6b]==base.ram[2][0x6c]==1 and base.ram[2][0x6d]==0 and base.ram[2][0x54]==3:break
    else:raise AssertionError(('No supported original Left',view(base)))
    if args.differential:
        return differential(base,raw)
    rows=[];first_zero_rise=None;previous=view(base)
    for age in range(32):
        C.source_step(base,129 if age<8 else 1);current=view(base)
        delta16=((current['source_y']-previous['source_y'])*256+current['fraction']-previous['fraction'])
        current.update(step=age+1,integer_delta=current['source_y']-previous['source_y'],observed_fractional_delta=delta16)
        if current['source']==3 and current['integer_delta']==0 and delta16<0:
            # Explicit contact fixture:1px between actual native footer and
            # top. Current sampler's2px footer affects only this component.
            q=L.clone(base);C.field(q,'Enemy_Y_Position',q[0x65b]+1)
            N.invoke(q,'GetEnemyOffscreenBits',x=C.SLOT);N.invoke(q,'RelativeEnemyPosition',x=C.SLOT)
            N.invoke(q,'LargePlatformBoundBox',x=C.SLOT)
            before=view(q);r=Q.direct(q,G.entry(raw),x=C.SLOT)
            contact=N.get(q,'PlatformCollisionFlag',C.SLOT)
            current['declared_gap1_contact']=dict(before=before,passenger=contact,
                source_after_sampler=q.ram[2][0x6b],CPU=r['CPU'])
            if first_zero_rise is None:first_zero_rise=current
        rows.append(current);previous=current
        if current['source']==5:break
    print('DKJR_JUMP_PROJECTION '+json.dumps(dict(candidate_SHA256=T.PIN,rows=rows,
        first_zero_integer_rising_step=first_zero_rise,outputs_written=0,
        original_controls_only_after_declared_component_setup=True,
        scope='Declared pipe/helper primitive and explicit1px contact query. Not a genuine final3040 route, full upstream platform lifecycle, or native physical proof.'),separators=(',',':')),flush=True)
    assert first_zero_rise is not None,rows


def differential(base,raw):
    """Same declared initial state/ordinary inputs; actual actor retirement."""
    cases=[];CPU=N.NesMPU
    for helper in(True,False):
        m=L.clone(base)
        if not helper:N.invoke(m,'EraseEnemyObject',x=C.SLOT)
        previous=view(m);rows=[];writes=[];lpc_calls=0
        class Probe(CPU):
            def step(self):
                nonlocal lpc_calls
                tag=m.rawtags[(self.pc-32768)//8192]if self.pc>=32768 else-1
                pc=self.pc;before=m.ram[2][0x6b]
                if(tag,pc)==(128,0xb453):lpc_calls+=1
                result=super().step();after=m.ram[2][0x6b]
                if before!=after:writes.append(dict(step=len(rows)+1,PC=pc,bank=tag,before=before,after=after,
                    source_y=m.ram[2][0x210],jump_age=m.ram[2][0x7e],native_vy=N.get(m,'Player_Y_Speed')))
                return result
        with patch.object(N,'NesMPU',Probe):
            for age in range(32):
                C.source_step(m,129 if age<8 else 1);s=view(m)
                s.update(step=age+1,integer_delta=s['source_y']-previous['source_y'],
                    observed_fractional_delta=(s['source_y']-previous['source_y'])*256+s['fraction']-previous['fraction'],
                    last_query_kind=m.ram[2][0x8db],
                    last_query_rectangles=list(m.ram[2][0x800:0x800+min(m.ram[2][0x8dd],60)]))
                rows.append(s);previous=s
                if s['source']==5:break
        assert lpc_calls==0,('Unexpected native LPC during donor-only source_step',lpc_calls)
        selected={1,5,6,8,9,13,20,22,23,25,32}
        cases.append(dict(helper_present=helper,rows=[r for r in rows if r['step']in selected],source_state_writers=writes,
            native_LPC_calls=lpc_calls,minimum_native_y=min(r['y']for r in rows)))
    print('DKJR_JUMP_HELPER_DIFFERENTIAL '+json.dumps(dict(candidate_SHA256=T.PIN,cases=cases,
        outputs_written=0,ordinary_inputs_after_component_setup=True,
        sole_differential_native_actor_retired=True,
        scope='Declared pipe/helper component. Actor removed by actual EraseEnemyObject in control. No native LPC or synthetic source state repair. Not the genuine final3040 route or Mesen.'),separators=(',',':')),flush=True)
    assert cases[0]['minimum_native_y']>cases[1]['minimum_native_y'],cases


if __name__=='__main__':main()
