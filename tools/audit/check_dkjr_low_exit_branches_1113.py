"""Bounded ordinary jumping exits from a genuine Main1000 clone; no writes."""
from hashlib import sha256
import json

import check_dkjr_descending_route_branches_1113 as Base

Q,N,L,T=Base.Q,Base.N,Base.L,Base.T


def main():
    candidate,seed,prefix=Base.prefix();rows=[]
    for threshold in(40,48,56,64,72,80):
        q=L.clone(seed);trace=[];jump=None
        for age in range(240):
            before=Base.view(q)
            if before['source']==5:break
            if jump is None and age>=threshold and before['source']==1:
                jump=age
            pad=129 if age<8 or jump is not None and jump<=age<jump+8 else 1
            Q.frame(q,pad)
            v=Base.view(q)
            if age%8==0 or jump is not None and age in(jump,jump+7):
                trace.append(dict(age=age+1,pad=pad,x=v['x'],y=v['y'],source=v['source'],
                    actor480=next((a for a in v['actors']if a['left']==480),None)))
            if v['x']>=530 and v['y']==176 and v['source']==1:break
        final=Base.view(q)
        rows.append(dict(second_fresh_A_not_before=threshold,actual_A_start=jump,
            updates=age+1,crossed=final['x']>=530 and final['y']==176 and final['source']==1,
            final=final,trace=trace))
    print('DKJR_LOW_EXIT_BRANCHES '+json.dumps(dict(candidate_SHA256=T.PIN,prefix=prefix,
        branches=rows,script_RAM_writes=False,outputs_written=0,
        scope='Ordinary controller-only clone suffixes, genuine prefix. No unbroken full-stage or physical claim.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
