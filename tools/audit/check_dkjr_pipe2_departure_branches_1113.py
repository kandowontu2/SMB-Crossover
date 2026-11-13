"""Real1330 prefix: compare ordinary riser departure directions and roof exits."""
from contextlib import redirect_stdout
import argparse
import io
import json
from hashlib import sha256

import replay_dkjr_descending_platform_1113 as R
import check_dkjr_descending_route_branches_1113 as Base

T,Q,P,H,N,L=R.T,R.Q,R.P,R.H,Base.N,Base.L


def view(m):
    v=Base.view(m);v['prior']=m.ram[2][0x6c];v['jump_age']=m.ram[2][0x7e]
    v['query']=[m.ram[2][0x8db],m.ram[2][0x8dd],m.ram[2][0x8ea],m.ram[2][0x8eb]]
    v['enemies']=[dict(slot=i,id=N.get(m,'Enemy_ID',i),x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
        y=N.get(m,'Enemy_Y_Position',i),state=N.get(m,'Enemy_State',i))for i in range(6)
        if N.get(m,'Enemy_Flag',i)and N.get(m,'Enemy_ID',i)!=37]
    return v


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--exit-jump',action='store_true');a=ap.parse_args()
    Q.T=T;parent,candidate=T.load_inputs(reuse_private=True)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    m=Q.mounted(seed,candidate)
    text=R.controller(candidate,pipes=(1,2,3,4))
    text=P.once(text,'local function drive()\n',
        "local function drive()\n if updates>=1330 then finish(true,'genuine-pipe2-riser');return end\n")
    with redirect_stdout(io.StringIO()):prefix=P.B.route(m,candidate,1500,controller_text=text)
    assert prefix['passed'];rows=[]
    for direction,takeoff in(('up',586),('up',589),('down',586),('down',589)):
        q=L.clone(m);phase='wait';launch=exit_at=None;events=[];trace=[];passed=False
        for age in range(650):
            v=view(q)
            if v['source']==5:break
            up=next((a for a in v['actors']if a['left']==560),None)
            down=next((a for a in v['actors']if a['left']==624),None)
            pad=0
            if phase=='wait':
                pad=1 if v['x']<takeoff else 2 if v['x']>takeoff else 0
                if up and v['x']==takeoff and v['source']==v['prior']==1 and 154<=up['top']<=160 and ((up['speed']>=128)==(direction=='up')):
                    launch=age;phase='air';events.append(dict(event='takeoff',age=age,state=v))
            if phase=='air':
                pad=129 if age-launch<8 else 1
                if age-launch>=8 and v['source']==1 and v['x']>=608:
                    phase='board';events.append(dict(event='postjump-support',age=age,state=v))
            if phase=='board':
                pad=1 if v['x']<655 else 0
                if v['source']==v['prior']==1 and v['x']>=633 and 160<=v['y']<=176:
                    exit_at=age;phase='exit';events.append(dict(event='low-exit',age=age,state=v))
            if phase=='exit':pad=129 if a.exit_jump and age-exit_at<8 else 1
            Q.frame(q,pad)
            after=view(q)
            if age%16==0:trace.append(dict(age=age+1,phase=phase,pad=pad,x=after['x'],y=after['y'],
                source=after['source'],prior=after['prior'],query=after['query'],
                actor624=next((a for a in after['actors']if a['left']==624),None)))
            if after['x']>=665 and after['y']==176 and after['source']==1:
                passed=True;break
        row=dict(departure=direction,takeoff=takeoff,exit_jump=a.exit_jump,passed=passed,updates=age+1,
            phase=phase,events=events,final=view(q),trace=trace)
        rows.append(row)
        print('DKJR_PIPE2_BRANCH '+json.dumps(row,separators=(',',':')),flush=True)
    print('DKJR_PIPE2_DEPARTURE_SCOPE '+json.dumps(dict(candidate_SHA256=T.PIN,
        prefix_controller_SHA256=sha256(text.encode()).hexdigest(),prefix=view(m),
        passing_branches=[(r['departure'],r['takeoff'])for r in rows if r['passed']],
        script_RAM_writes=False,outputs_written=0,
        scope='Genuine prefix and ordinary input clone suffixes. Not a continuous full route or native pass.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
