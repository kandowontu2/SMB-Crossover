"""Separate ordinary roof/low-exit jumps; frozen old full controls stay exact."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json

import check_dkjr_descending_platform_1113 as D

T,Q,P,H=D.T,D.Q,D.P,D.H


def controller(raw,*,pipes=(1,),stop_after_pipe=None):
    assert pipes and all(i in(1,2,3,4)for i in pipes)and len(set(pipes))==len(pipes)
    text=T.controller(raw,full=True)
    selected='('+ ' or '.join('index=='+str(i)for i in pipes)+')'
    text=P.once(text," elseif phase=='roof'and carried(d,down)then",f''' elseif phase=='roof'and {selected} and down and player>=d-2 and ram(2,0x6b)==1 then
  hold=updates+8;rearm=updates+47;remember('original-roof-jump',down);setPhase('jump-down',down)
 elseif phase=='roof'and carried(d,down)then''')
    text=P.once(text," if phase=='lower'and down then",f''' if phase=='lower'and down and {selected} and ram(2,0x6b)==1 and player>=d+9 and y>=160 and y<=176 then
  hold=updates+8;rearm=updates+47;remember('original-low-exit-jump',down);setPhase('depart',down)
 end
 if phase=='lower'and down then''')
    if stop_after_pipe is not None:
        assert stop_after_pipe in(1,2,3,4)
        gate=f'index>{stop_after_pipe}'if stop_after_pipe<4 else"phase=='to-gap'"
        text=P.once(text,'local function drive()\n',
            f"local function drive()\n if {gate} then finish(true,'ordinary-pipe-prefix-{stop_after_pipe}');return end\n")
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pipes',default='1');ap.add_argument('--stop-after-pipe',type=int)
    ap.add_argument('--max-updates',type=int,default=12000)
    a=ap.parse_args();Q.T=T
    parent=T.load_parent()
    candidate,_=T.transform(parent)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    text=controller(candidate,pipes=tuple(int(i)for i in a.pipes.split(',')),stop_after_pipe=a.stop_after_pipe)
    m=Q.mounted(seed,candidate)
    with redirect_stdout(io.StringIO()):result=P.B.route(m,candidate,a.max_updates,controller_text=text)
    r=result.get('receipt',{})
    print('DKJR_ORDINARY_LOW_EXIT '+json.dumps(dict(candidate_SHA256=T.PIN,
        controller_SHA256=sha256(text.encode()).hexdigest(),pipes=a.pipes,stop_after_pipe=a.stop_after_pipe,
        passed=result['passed'],logical_updates=result['logical_updates'],final=result['final'],
        reason=r.get('reason'),crossings=r.get('crossings'),events=r.get('events'),
        births=r.get('births'),carries=r.get('carries'),injury=r.get('injury'),
        receipt_SHA256=sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        script_RAM_writes=False,ROM_written=False,outputs_written=0,physical_cadence_claim=False),
        separators=(',',':')),flush=True)
    assert result['passed'],'Ordinary-control route did not meet its unchanged or explicitly partial endpoint.'


if __name__=='__main__':main()
