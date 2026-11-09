"""Measure first-pit takeoff against actual native 1-1 terrain and donor input."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_fourth_pipe_support_1110 as FourthSupport


Fourth,Approach,Recovery,Route,R,P,N,Current=(FourthSupport.Fourth,FourthSupport.Approach,
    FourthSupport.Recovery,FourthSupport.Route,FourthSupport.R,FourthSupport.P,FourthSupport.N,FourthSupport.Current)
I=Route.I
CAPTURE=R/'build/prince-fourth-pipe-native-1110/capture'
LEFT,RIGHT=1104,1136


def actual_failure():
    full=Current.read(CAPTURE/'full11.json')
    diag=Current.read(CAPTURE/'prince-diagnostic.json')
    third,group,fourth=(Current.read(CAPTURE/n) for n in ('third-pipe.json','third-goombas.json','fourth-pipe.json'))
    assert all(q['ROM_sha256']==Route.PIN for q in (full,diag,third,group,fourth))
    assert third['passed'] and group['passed'] and fourth['passed'] and not full['passed']
    assert (full['frames'],full['admitted'],full['HP'],full['state']['world_x'],full['state']['engine'])==(4967,2112,4,1121,11)
    assert not diag['first_pipe_route']['precontacts'] and 'combat' not in full['route']
    events=full['route']['events']
    request,admit,short=[r for r in events if r['Main'] in (1977,1979,2023)]
    assert [(r['tag'],r['world_x'],r['source_action']) for r in (request,admit,short)]==[
        ('takeoff',1012,1),('aerial',1012,4),('approach',1039,1)]
    assert full['route']['jump']['world_x']==1012 and full['route']['jump']['source_action']==4
    return dict(request=request,admission=admit,short_landing=short,terminal=full['state'])


def authored(base):
    m=N.Bus(base)
    N.put(m,AreaPointer=37,AreaType=1,WorldNumber=0,LevelNumber=0,SelectedCharacter=38)
    N.invoke(m,'GetAreaDataAddrs')
    assert N.get(m,'AreaDataLow')+256*N.get(m,'AreaDataHigh')==I.address(base,'L_GroundArea6')+2
    at=I.address(base,'AreaObjectLength')
    m[at:at+3]=[255]*3
    columns={}
    for col in range(80):
        N.put(m,CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32)
        N.invoke(m,'AreaParserCore')
        block=I.address(base,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
        columns[col]=[m[block+16*i+(col&15)] for i in range(13)]
    assert all(columns[c][11:13]==[0,0] for c in (69,70))
    assert columns[68][11] and columns[71][11]
    return columns


def start(base,columns):
    env,seed,labels,_=Approach.Earned.fixture(base)
    m,third=Fourth.arrival(env,seed,labels,707,779)
    assert third['terminal']=='cleared'
    last=None
    controls=Route.controls
    def capture(e,model,lab,pad):
        nonlocal last
        last=model
        return controls(e,model,lab,pad)
    Route.controls=capture
    try:
        fourth=FourthSupport.replay(env,m,labels,'standing-cap')
    finally:
        Route.controls=controls
    assert fourth['terminal']=='clear' and last is not None
    q=Recovery.sample(last,0)
    assert (q['x'],q['y'],q['hp'],q['lives'])==(962,176,4,2)
    for col in range(48,80):
        block=I.address(base,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
        for row,tile in enumerate(columns[col]):
            last[block+row*16+(col&15)]=tile
    return env,last,labels,q


def replay(env,seed,labels,threshold):
    m=N.fork(seed)
    phase='approach'
    at=0
    terminal='bound'
    events,poses=[],[]
    previous=None
    minimum=None
    for epoch in range(340):
        q=Recovery.sample(m,epoch)
        x,y,pose=q['x'],q['y'],q['frame']
        key=(phase,q['action'],pose,q['mode'],q['hp'])
        q['authored_lips']=[Route.query_support(m,i,208) for i in (1088,1104,1120,1136)]
        if phase!='approach' and key!=previous:
            poses.append(q)
        previous=key
        if q['authored_lips'][1:3]!=[0,0] or not q['authored_lips'][0] or not q['authored_lips'][3]:
            terminal='authored-lip-overwritten'
            break
        if q['hp']==0 or q['engine']!=8 or q['lives']!=2:
            terminal='death'
            break
        if phase=='approach' and threshold<=x<=1090 and Recovery.running(m,q):
            events.append(dict(type='A',state=q))
            phase,at='arm',epoch
        elif phase=='arm':
            if q['action']==4:
                phase,at='flight',epoch
                events.append(dict(type='original-action4',state=q))
            elif epoch-at>28:
                terminal='no-A-admission'
                break
        elif phase=='flight':
            minimum=q['foot'] if minimum is None else min(minimum,q['foot'])
            if x>=RIGHT+16 and y==176 and Recovery.grounded(m,q):
                events.append(dict(type='far-ground',state=q))
                terminal='clear'
                break
            if epoch-at>=12 and q['action']!=4 and x+13<LEFT and y==176 and Recovery.grounded(m,q):
                events.append(dict(type='short-ground',state=q))
                terminal='short'
                break
            if epoch-at>130:
                terminal='flight-bound'
                break
        if phase=='approach' and x>=1100:
            terminal='no-safe-takeoff'
            break
        Route.controls(env,m,labels,129 if phase=='arm' else 1)
    return dict(threshold=threshold,terminal=terminal,minimum_foot=minimum,events=events,poses=poses,end=q)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not (out/'proof.json').exists()
    native=actual_failure()
    raw=Route.ROM.read_bytes()
    assert sha256(raw).hexdigest()==Route.PIN
    template,_,_=Current.current()
    base=dict(template,raw=raw)
    columns=authored(base)
    env,seed,labels,initial=start(base,columns)
    print('Native parser columns',[(16*i,[(32+16*j,v) for j,v in enumerate(columns[i]) if v])
                                    for i in range(62,74)],flush=True)
    results=[]
    for threshold in (1010,1024,1036,1044,1052,1060,1068,1076,1084):
        q=replay(env,seed,labels,threshold)
        results.append(q)
        print(threshold,q['terminal'],q['end']['x'],q['end']['y'],q['end']['hp'],q['minimum_foot'],
              [(e['type'],e['state']['epoch'],e['state']['x']) for e in q['events']],flush=True)
    out.mkdir(exist_ok=True)
    refs=(Path(__file__),Path(FourthSupport.__file__),Path(Fourth.__file__),Route.ROM,R/'src/level_tiles.s',
          *(CAPTURE/n for n in ('third-pipe.json','third-goombas.json','fourth-pipe.json','full11.json','prince-diagnostic.json')))
    receipt=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,native_negative=native,
                 arrival=initial,authored_columns={16*i:columns[i] for i in range(60,75)},results=results,
                 scope='Actual compiled AreaParserCore terrain. Authored native columns are copied once at the CPU '
                       'fourth-pipe landing. The existing group parser and donor/native control run thereafter without '
                       'state writes. No natural Mesen crossing yet.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
