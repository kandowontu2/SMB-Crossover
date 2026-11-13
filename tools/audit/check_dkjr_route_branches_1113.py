"""Controller-only branches from one genuine DK stage prefix; no files."""
from hashlib import sha256
import argparse
import json

import compose_dkjr_helper_retire_1113 as P
import check_dkjr_head_bridge_1113 as H

B,N,W,L=P.B,H.N,H.W,H.L


def actors(m):
    return [dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),
        state=N.get(m,'Enemy_State',i),x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
        y=N.get(m,'Enemy_Y_Position',i))for i in range(6)if N.get(m,'Enemy_Flag',i)]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--riser',action='store_true')
    ap.add_argument('--retreat',action='store_true');args=ap.parse_args()
    assert not args.retreat or args.riser
    raw=B.C.ROM.read_bytes();candidate,info=P.proposal_current(raw)
    _,seed=H.cold(candidate,bytes.fromhex(info['cookie']))
    prefix=P.controller(candidate,full=True,fourth_window=True,ledge_wait=True,stationary_wait=args.riser)
    stop_at=7000 if args.riser else 4990
    updates=0;branch=None
    class AtBranch(Exception):pass
    def after(m):
        nonlocal updates,branch
        updates+=1
        if updates%1000==0:print('DKJR_BRANCH_PREFIX '+json.dumps(dict(updates=updates,player=B.state(m)),separators=(',',':')),flush=True)
        if updates==stop_at:
            branch=L.clone(m);raise AtBranch
    try:B.route(seed,candidate,stop_at+10,controller_text=prefix,after_frame=after)
    except AtBranch:pass
    assert branch is not None and B.state(branch)['source_state']==1
    assert B.state(branch)['x']==(2127 if args.riser else 1168)
    print('DKJR_BRANCH_BINDING '+json.dumps(dict(candidate_SHA256=sha256(candidate).hexdigest(),
        prefix_controller_SHA256=sha256(prefix.encode()).hexdigest(),prefix_Main_updates=updates,
        branch_state=B.state(branch),branch_actors=actors(branch),RAM_seed_writes=0,
        scope='One actual menu/stage/controller prefix cloned at complete Main. Only controller bytes differ after this point; not Mesen.'),separators=(',',':')),flush=True)
    if args.riser:
        terrain=[]
        for x in range(2080,2193,16):
            page=x>>8;base=0x300 if not(page&1)else 0x3d0
            terrain.append(dict(x=x,tiles={y:branch[base+((y-32)&240)+((x>>4)&15)]for y in range(128,209,16)}))
        print('DKJR_BRANCH_TERRAIN '+json.dumps(dict(rows=terrain,source_fields={hex(i):branch.ram[2][i]for i in(0x54,0x6b,0x6c,0x6d,0x76,0x7e)},source_rect=list(branch.ram[2][0x3e:0x46])),separators=(',',':')),flush=True)
    rows=[]
    if args.retreat:
        for back in(32,40,48):
            for turn in(12,16,20,24):
                m=L.clone(branch);injury=None;lowest=255;samples=[]
                sequence=[(2,back),(0,4),(128,8),(0,turn-8),(1,40),(0,40)]
                tick=0
                for pad,duration in sequence:
                    for _ in range(duration):
                        m.controller_pad=pad;B.Frames.frame(m);s=B.state(m);lowest=min(lowest,s['y'])
                        if s['source_state']==5 and injury is None:injury=tick
                        if tick%8==0:samples.append((tick,s['x'],s['y'],s['source_state']))
                        tick+=1
                rows.append(dict(left_retreat_updates=back,stationary_jump_updates_before_right=turn,
                    injury_tick=injury,minimum_player_y=lowest,final=B.state(m),samples=samples))
        print('DKJR_RETREAT_JUMP_BRANCHES '+json.dumps(dict(rows=rows,output_files=0,
            inventory_enemy_and_game_state_unmodified=True,physical_cadence_claim=False),separators=(',',':')),flush=True)
        return
    cases=((direction,delay,hold)for direction in(0,1,2)for delay in(0,8)for hold in(8,40))if args.riser else((direction,delay,8)for direction in(0,1,2)for delay in(0,4,8,12))
    for direction,delay,hold in cases:
            m=L.clone(branch);injury=None;flat=None;lowest=255
            for tick in range(90):
                m.controller_pad=(128|direction)if delay<=tick<delay+hold else 0
                B.Frames.frame(m);s=B.state(m);lowest=min(lowest,s['y'])
                if s['source_state']==5 and injury is None:injury=tick
                if N.get(m,'Enemy_State',0)in(4,32,34)and flat is None:flat=tick
                if injury is not None:break
            rows.append(dict(held_direction=direction,A_hold=hold,neutral_delay=delay,injury_tick=injury,
                first_Goomba_defeat_state_tick=flat,minimum_player_y=lowest,final=B.state(m),actors=actors(m)))
    print('DKJR_CONTROLLER_BRANCHES '+json.dumps(dict(rows=rows,output_files=0,
        inventory_enemy_and_game_state_unmodified=True,physical_cadence_claim=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
