"""Declared CPU components of proposed support guard; no ROM composition."""
from hashlib import sha256
import json

import measure_dkjr_oneway_fit_1114 as M

F=M.F;G=F.Gate
Q,P,H,N,W,L,C=G.Q,G.P,G.H,G.N,G.W,G.L,G.C


def overlay(memory,rows):
    for row in rows:
        at=row['payload_offset'];size=row['bytes']
        if at<8192:bank,offset=3,at
        elif at<9*1024:bank,offset=2,0x900+at-8*1024
        else:bank,offset=2,0x1000+at-9*1024
        assert bytes(memory.ram[bank][offset:offset+size])==bytes.fromhex(row['preimage_hex']),(row['role'],bank,offset)
        memory.ram[bank][offset:offset+size]=bytes.fromhex(row['proposed_hex'])


def state(m):
    r=m.ram[2]
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
        source=r[0x6b],prior=r[0x6c],source_y=r[0x210],age=r[0x7e],fraction=r[0x7f],
        acceleration=r[0x82]+256*r[0x83],impulse=r[0x86]+256*r[0x87],native_vy=N.get(m,'Player_Y_Speed'),
        lives=N.get(m,'NumberofLives'))


def main():
    parent,raw=F.load_inputs();proposal=M.fragments(raw);e73=F.T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);C.SLOT=3
    cases=[]
    for helper in(True,False):
        base=C.setup(Q.mounted(seed,raw))
        if not helper:N.invoke(base,'EraseEnemyObject',x=C.SLOT)
        for _ in range(16):
            C.source_step(base,2)
            if base.ram[2][0x6b]==base.ram[2][0x6c]==1 and base.ram[2][0x6d]==0 and base.ram[2][0x54]==3:break
        else:raise AssertionError(('No legal Left',state(base)))
        pair=[]
        for proposed in(False,True):
            m=L.clone(base)
            if proposed:overlay(m,proposal['fragments'])
            rows=[];land=None
            for age in range(48):
                C.source_step(m,129 if age<8 else 1);s=state(m)
                rows.append(s)
                if age>0 and rows[-2]['source']==3 and s['source']==1 and land is None:land=dict(step=age+1,state=s)
                if s['source']==5:break
            pair.append(dict(proposed=proposed,minimum_y=min(r['y']for r in rows),first_landing=land,
                rows=[dict(step=i+1,state=r)for i,r in enumerate(rows)if i in(0,4,5,8,12,20,22,24,31,39,47)],
                all_core_frames=[bytes(m.ram[2][:0x800]).hex()]if False else None,final=rows[-1]))
        if helper:
            assert pair[1]['minimum_y']<pair[0]['minimum_y'],pair
            assert pair[0]['first_landing']['step']==6,pair
            assert pair[1]['first_landing']and pair[1]['first_landing']['step']>22,pair
        else:
            assert pair[0]['rows']==pair[1]['rows']and pair[0]['final']==pair[1]['final'],pair
        cases.append(dict(helper_present=helper,arms=pair))
    print('DKJR_ONEWAY_COMPONENTS '+json.dumps(dict(passed=True,parent_SHA256=F.T.PIN,cases=cases,
        outputs_written=0,ROM_composed=False,linked_code_overlaid_in_declared_CPU_components=True,
        scope='Declared pipe/helper setup; ordinary original Left/Right+A inputs. Candidate source fragments overlaid only in CPU RAM after actual cold. No native LPC, full Main/ISR/cold/header/native qualification or allocated ROM.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
