"""Controller-only CPU route for the selected Giant, with bounded failures."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mega_giant_f33_1110 as Q


S,C,G,M=Q.S,Q.C,Q.G,Q.M
PITS=((1104,1136),(1376,1424),(2448,2480))


def world(m, slot):
    return M.get(m,'Enemy_X_Position',slot)+256*M.get(m,'Enemy_PageLoc',slot)


def state(m):
    return dict(x=C.world_x(m),y=M.get(m,'Player_Y_Position'),page=M.get(m,'Player_Y_HighPos'),
                player_state=M.get(m,'Player_State'),speed=M.get(m,'Player_X_Speed'),
                engine=M.get(m,'GameEngineSubroutine'),lives=M.get(m,'NumberofLives'),
                timer=M.get(m,'TimerControl'),status=M.get(m,'PlayerStatus'),
                star_task=M.get(m,'StarFlagTaskControl'),music=M.get(m,'EventMusicBuffer'),
                display_timer=[M.get(m,'GameTimerDisplay',i) for i in range(3)],
                world=M.get(m,'WorldNumber')+1,level=M.get(m,'LevelNumber')+1,
                camera=M.get(m,'ScreenLeft_X_Pos')+256*M.get(m,'ScreenLeft_PageLoc'),
                actors=[(i,M.get(m,'Enemy_ID',i),world(m,i),M.get(m,'Enemy_Y_Position',i),
                         M.get(m,'Enemy_State',i)) for i in range(6) if M.get(m,'Enemy_Flag',i)==1])


def run(seed, labels, body, pit_lead, threat_lead, hold_time, settle, timed, limit):
    m=M.fork(seed)
    jumps, milestones, tail, counts = [], {}, [], Counter()
    first_jump = grounded = False
    launched = set()
    landings = set()
    hold = 0
    near = 0
    result = 'update_limit'
    minimum = 255
    scripted = {}
    for step in range(limit):
        s=state(m)
        x,y,ground = s['x'],s['y'],s['player_state']==0
        if s['level']==2 and s['engine']==8:
            result='active_1_2'; break
        if s['lives']!=2 or s['engine']==11:
            result='native_death'; break
        keys=65
        target=None
        if x<482:
            if x>=264 and not first_jump:
                first_jump=True
                hold=35
                target='first_goomba'
            if x>=402 and not grounded:
                if y==176 and ground:
                    grounded=True
                else:
                    keys=2 if 0<s['speed']<128 else 0
        elif s['engine']==8 and settle and any(mark<=x<mark+32 and mark not in landings for mark in (679,853)):
            mark=679 if x<800 else 853
            if y==176 and ground:
                landings.add(mark)
                target=f'pipe_{736 if mark==679 else 912}'
                hold=hold_time
            else:
                keys=2 if 0<s['speed']<128 else 0
        elif s['engine']==8 and ground and not hold:
            for lo,hi in PITS:
                if lo not in launched and lo-pit_lead<=x<lo:
                    target=f'pit_{lo}'
                    launched.add(lo)
                    break
            if target is None and not 0<near:
                for slot,eid,enemy_x,enemy_y,status in s['actors']:
                    if eid<=6 and status<32 and 10<=enemy_x-x<=threat_lead and abs(enemy_y-y-8)<24:
                        target=f'actor_{slot}_{enemy_x}'
                        break
            if target is None and x>=3128 and x<3168 and 3168 not in launched:
                target='flagpole_step'
                launched.add(3168)
            if target:
                hold=hold_time
                near=hold_time+2
        if target:
            jumps.append(dict(update=step,target=target,**s))
        keys |= 128 if hold and keys==65 else 0
        if s['engine']!=8:
            keys=1
        counts['active_updates'] += s['engine']==8
        if s['engine'] in (4,5,9,10) and s['engine'] not in scripted:
            scripted[s['engine']]=dict(update=step,**s)
        q=C.play(m,body,keys)
        counts['destructive_effect_calls'] += q['effects']
        minimum=min(minimum,q['SP_minimum'])
        hold=max(hold-1,0)
        near=max(near-1,0)
        M.consume(m)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        tail.append(dict(update=step,keys=keys,**s))
        tail=tail[-24:]
        for mark in (448,482,608,640,736,768,912,944,1104,1136,1376,1424,2448,2480,3168):
            if x>=mark and mark not in milestones:
                milestones[mark]=dict(update=step,**s)
        if (step>=100 and len(tail)==24 and x==tail[0]['x'] and keys in (1,65)
                and (not timed or all(row['engine']==8 for row in tail))):
            result='right_stall'; break
    return dict(passed=result=='active_1_2',reason=result,steps=step,endpoint=state(m),jumps=jumps,
                milestones=milestones,scripted=scripted,final_updates=tail,minimum_SP=minimum,counts=dict(counts),
                controls=dict(pit_lead=pit_lead,threat_lead=threat_lead,hold_time=hold_time,settle=settle,timed=timed))


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--pit-lead',type=int,default=30)
    cli.add_argument('--threat-lead',type=int,default=66)
    cli.add_argument('--hold',type=int,default=28)
    cli.add_argument('--settle',action='store_true')
    cli.add_argument('--timed-transitions',action='store_true')
    cli.add_argument('--limit',type=int,default=2100)
    args=cli.parse_args()
    old,new,patches,storage,labels,render_labels,cookie,meta,render,donor,records=Q.compose(args.output,C.HOST.read_bytes())
    seed,_=S.select_and_start(new,labels,cookie,meta,render)
    result=run(seed,labels,Q.read(G.RESIDENT)['storage']['symbols'],args.pit_lead,args.threat_lead,args.hold,
               args.settle,args.timed_transitions,args.limit)
    result.update(parent_SHA256=Q.PIN,expected_memory_only_SHA256=G.digest(new['raw']),ROM_written=False,
                  bindings={str(p):C.sha(p) for p in (Path(__file__),Path(Q.__file__),Q.SOURCE,Q.STAGE,C.DONOR)})
    suffix=('-settle' if args.settle else '')+('-timed' if args.timed_transitions else '')
    if args.limit!=2100:
        suffix+=f'-{args.limit}'
    dest=args.output/f'route-{args.pit_lead}-{args.threat_lead}-{args.hold}{suffix}.json'
    assert not dest.exists()
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(result['reason'],result['endpoint'],len(result['jumps']),dest,flush=True)


if __name__=='__main__':
    main()
