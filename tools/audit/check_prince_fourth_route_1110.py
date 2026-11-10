"""Controller-only Prince fourth-pipe/first-gap CPU exploration, stdout only.

The exact native AreaParserCore builds the terrain once in an explicitly
translated CPU scene. No cartridge, receipt, capture or native claim is made.
"""
import argparse
import json

import check_prince_landing_exit_1110 as Exit

C,N,I=Exit.C,Exit.C.N,Exit.C.I
REAL_NMI=False
FULL_ROUTE=False
POST_GAP=100
SECOND_AT=1340
CHAIN=False


def sample(m,tick):
    row=C.Recovery.sample(m,tick)
    row['support']=C.Recovery.grounded(m,row)
    return row


def authored(model,through=75):
    N.put(model,AreaPointer=37,AreaType=1,WorldNumber=0,LevelNumber=0,
          AreaDataOffset=0,AreaObjectPageLoc=0,AreaObjectPageSel=0,
          BackloadingFlag=0,BehindAreaParserFlag=0)
    N.invoke(model,'GetAreaDataAddrs')
    assert N.get(model,'AreaDataLow')+256*N.get(model,'AreaDataHigh')==I.address(model.bundle,'L_GroundArea6')+2
    at=I.address(model.bundle,'AreaObjectLength');model[at:at+3]=[255]*3
    columns={};cursor_model=None
    for col in range(through+1):
        N.put(model,CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32)
        N.invoke(model,'AreaParserCore')
        block=I.address(model.bundle,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
        columns[col]=[model[block+16*row+(col&15)] for row in range(13)]
        if col==65:cursor_model=N.fork(model)
    assert [columns[c][7] for c in (57,58)]==[0x10,0x11], {c:columns[c] for c in (46,47,57,58)}
    assert [columns[c][11] for c in (68,69,70,71)]==[0x54,0,0,0x54]
    if REAL_NMI:
        assert cursor_model is not None
        model=cursor_model
        for col in range(44,76):
            block=I.address(model.bundle,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
            for row,tile in enumerate(columns[col]):model[block+16*row+(col&15)]=tile
        N.put(model,CurrentPageLoc=4,CurrentColumnPos=2,BlockBufferColumnPos=2,
              AreaParserTaskNum=0,ScrollThirtyTwo=0)
    return columns,model


def terrain_signature(m):
    return {str(y):[C.Route.query_support(m,x,y) for x in (736,752,912,928,1088,1104,1120,1136)]
            for y in (144,160,176,192,208,224)}


def point_probes(seed):
    rows=[]
    for x,y in ((912,144),(920,176),(928,192),(1104,208),(1136,208)):
        model=N.fork(seed)
        model.ram[3][0x1369:0x136b]=x.to_bytes(2,'little')
        model.ram[3][0x136b:0x136d]=y.to_bytes(2,'little')
        result=I.invoke(model,3,0xb310,(83,71,109,0x61))['regs']
        rows.append(dict(x=x,y=y,native_tile=C.Route.query_support(seed,x,y),source_A=result[0],source_C=result[3]&1))
    return dict(actual_symbols={k:I.address(seed.bundle,k) for k in ('BlockBufferAddr','Block_Buffer_1','MTileAttribute')},
                old_bound_symbols=dict(BlockBufferAddr=0x95d8,Block_Buffer_1=0x300,MTileAttribute=0xef36),
                probes=rows)


def trial(env,seed,labels,policy,bound=1400):
    m=N.fork(seed);mode='run';landing=None;changed=0;events=[];previous_hp=5;cap=False
    max_x=0;last=None;poses=[];pipe_feet=[]
    def go(target,row):
        nonlocal mode,changed
        events.append(dict(event=f'{mode} to {target}',**{k:row[k] for k in
            ('epoch','x','y','foot','hp','action','frame','mode','camera_left','camera_right')}))
        mode,changed=target,row['epoch']
    for tick in range(bound):
        row=sample(m,tick);x,y=row['x'],row['y'];max_x=max(max_x,x)
        key=row['action'],row['frame'],row['mode']
        if 880<=x<=980 and key!=last and len(poses)<64:
            poses.append({k:row[k] for k in ('epoch','x','y','foot','support','action','frame','mode')})
        last=key
        if 912<=x<944:pipe_feet.append(row['foot'])
        if row['support'] and x+13>=912 and x<944 and 110<=y<=115 and not cap:
            cap=True;events.append(dict(event='actual native cap witness',tick=tick,x=x,y=y,foot=row['foot']))
        if row['hp']!=previous_hp:
            events.append(dict(event='HP change',tick=tick,x=x,before=previous_hp,after=row['hp']))
            previous_hp=row['hp']
        if row['hp']==0 or row['engine']!=8 or row['lives']!=2:
            mode='dead';break
        if tick%8==0 and row['camera_left']<912 and (C.Route.query_support(m,912,144)!=0x10 or C.Route.query_support(m,928,144)!=0x11):
            mode='fourth-pipe-overwritten';break
        if mode=='run' and 745<=x<=752 and abs(y-112)<=2 and C.Recovery.running(m,row):go('takeoff',row)
        elif mode=='takeoff' and row['action']==4:go('third-flight',row)
        if mode=='third-flight' and policy.startswith('air') and (row['mode'] in (2,6) or row['action']==10):
            go('climb',row)
        if landing is None and N.get(m,'Enemy_State',1)==4:
            landing=tick
            go('roll' if policy.startswith('roll') else 'settle' if policy=='settle' else 'up',row)
        age=tick-changed
        if mode=='roll' and (age>=8 or x>=896):go('up',row)
        elif mode=='settle' and row['support'] and row['frame']==15 and row['mode']==0 and row['a_lock']==0:go('up',row)
        elif mode=='up' and (row['mode'] in (2,6) or row['action']==10):go('climb',row)
        elif mode=='climb' and row['support'] and row['frame']==15 and row['mode']==0 and 899<=x<944 and 110<=y<=115:
            cap=True;go('cap-A',row)
        elif mode=='cap-A' and row['action']==3:go('cap-run',row)
        elif mode=='cap-run' and x>=960 and y==176 and row['support']:
            go('pit-approach',row)
        if mode in ('up','climb','cap-run') and x>=944 and y==176 and row['support']:
            events.append(dict(event='beyond fourth pipe',tick=tick,x=x,cap_witness=cap))
            go('pit-approach',row)
        if mode=='pit-approach' and 1059<=x<=1090 and row['phase'] in (0,1) and C.Recovery.running(m,row):go('pit-takeoff',row)
        elif mode=='pit-takeoff' and row['action']==4:go('pit-flight',row)
        elif mode=='pit-flight' and x>=1152 and y==176 and row['support']:
            go('second-approach' if FULL_ROUTE else 'first-gap-clear',row)
            if not FULL_ROUTE:break
        if mode=='second-approach' and SECOND_AT<=x<=min(1361,SECOND_AT+20) and row['phase'] in (0,1) and C.Recovery.running(m,row):go('second-takeoff',row)
        elif mode=='second-takeoff' and row['action']==4:go('second-flight',row)
        elif mode=='second-flight' and x>=(1424 if CHAIN else 1440) and y==176 and row['support']:
            go('post-takeoff' if CHAIN else 'post-approach',row)
        if mode=='post-approach' and row['support']:
            ahead=[a for a in row['actors'] if a['id']<7 and a['y']>=152 and a['state']<2 and a['x']>x]
            if ahead and POST_GAP<=min(a['x']-x for a in ahead)<=POST_GAP+20 and row['phase'] in (0,1) and C.Recovery.running(m,row):
                events.append(dict(event='post-pit enemy target',tick=tick,x=x,actors=ahead));go('post-takeoff',row)
        elif mode=='post-takeoff' and row['action']==4 and row['mode']==255:go('post-flight',row)
        elif mode=='post-flight' and x>=1625 and y==176 and row['support']:go('post-pair-clear',row);break
        if mode=='second-approach' and x>=1370:mode='second-no-safe-takeoff';break
        if mode=='post-approach' and x>=1550:mode='post-no-safe-takeoff';break
        if age>200 and mode not in ('run','third-flight'):
            mode+='-bound';break
        pads={'run':1,'takeoff':129,'third-flight':1,'roll':129,
              'settle':0,'up':9 if policy.endswith('right-up') else 8,
              'climb':8,'cap-A':128,'cap-run':1,'pit-approach':1,'pit-takeoff':129,'pit-flight':1,
              'second-approach':1,'second-takeoff':129,'second-flight':1,
              'post-approach':1,'post-takeoff':129,'post-flight':1}
        if mode=='third-flight' and policy.startswith('air') and x>=int(policy[3:]):pads[mode]=9
        C.Route.controls(env,m,labels,pads[mode])
        if REAL_NMI:N.consume(m)
    else:mode='bounded'
    result=dict(policy=policy,outcome=mode,maximum_x=max_x,events=events,terminal=row,
                terrain=terrain_signature(m),pipe_poses=poses,pipe_foot_range=[min(pipe_feet),max(pipe_feet)] if pipe_feet else None)
    return result,m


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--policy',default='roll-up')
    cli.add_argument('--inspect',action='store_true')
    cli.add_argument('--nmi',action='store_true')
    cli.add_argument('--full',action='store_true')
    cli.add_argument('--post-gap',type=int,default=100)
    cli.add_argument('--second-at',type=int,default=1340)
    cli.add_argument('--chain',action='store_true')
    args=cli.parse_args()
    global REAL_NMI,FULL_ROUTE,POST_GAP,SECOND_AT,CHAIN
    REAL_NMI=args.nmi
    FULL_ROUTE,POST_GAP=args.full,args.post_gap
    SECOND_AT=args.second_at
    CHAIN=args.chain
    raw=Exit.ROM.read_bytes();assert C.digest(raw)==Exit.PIN
    bundle=C.Start.W.bundle(raw);env,seed,labels=C.fixture(bundle)
    N.put(seed,CrossoverBehaviorVersion=0)
    if REAL_NMI:N.consume(seed)
    before=terrain_signature(seed)
    columns,seed=authored(seed)
    print('POINT PROBES '+json.dumps(point_probes(seed),separators=(',',':')),flush=True)
    print('NATIVE TERRAIN '+json.dumps(dict(ROM_sha256=Exit.PIN,before=before,
        after=terrain_signature(seed),profiles={str(16*c):[(32+16*i,t) for i,t in enumerate(columns[c]) if t]
        for c in (46,47,57,58,68,69,70,71)},
        real_NMI=REAL_NMI,cursor={k:N.get(seed,k) for k in ('AreaDataOffset','CurrentPageLoc','CurrentColumnPos','BlockBufferColumnPos','AreaParserTaskNum')}),separators=(',',':')),flush=True)
    if args.inspect:return
    for policy in args.policy.split(','):
        result,m=trial(env,seed,labels,policy)
        print('TRIAL '+json.dumps({k:v for k,v in result.items() if k!='pipe_poses'},separators=(',',':')),flush=True)


if __name__=='__main__':main()
