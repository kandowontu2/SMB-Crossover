"""Measure genuine Prince cap departures against the native Goomba group."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_roof_scroll_seam_1110 as Seam


R, P, I, N, Current = Seam.R, Seam.P, Seam.I, Seam.N, Seam.Current
ROOT = R/'build/prince-roof-scroll-native-1110'
ROM = ROOT/'prince-private.nes'
PIN = '4699c73befdd331b7e49a8b992a4f15f52d14eed81ac2d76f3b69c63ba3c846e'
CAPTURE = ROOT/'native/capture'


def controls(env, model, labels, pad):
    model.controller_pad = pad
    N.put(model,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
    for name in ('writes','ram_writes','ppu_log','blocked'):
        getattr(model,name).clear()
    return env['run'](model,'GameLoop',labels)


def tiles(left):
    def tile(x,y):
        if y>=208:
            return 0x54
        if not left<=x<left+32 or y<144:
            return 0
        return (0x12 if y<160 else 0x14)+int(x>=left+16)
    return tile


def roof(base):
    seed,_ = P.Q.C.C.cold(base,38)
    env,model,labels = P.Q.first8(base,seed)
    Seam.terrain(model,tiles(192))
    for epoch in range(257):
        pad = 1 if epoch<77 or epoch>=217 else 0 if epoch<113 else 8
        controls(env,model,labels,pad)
    row = Current.row(model,257)
    assert (row['x'],row['y'],row['action'],row['mode'],row['frame'],row['hp'],row['lives'])==(201,112,1,1,6,5,2)
    return env,model,labels,row


def install_group(model):
    b = model.bundle
    ptr = I.address(b,'E_GroundArea6')
    offset = I.location(b,'E_GroundArea6')
    stream = bytes.fromhex('1ec2006b068b8663b70f05030623064bb7bb005bb7fb373bb70f0b1b37ff')
    assert b['raw'][offset:offset+len(stream)]==stream
    # Restart at the first future 1-1 group after the two previous Goombas.
    # The parser itself admits and creates both actors as the camera advances.
    N.put(model,EnemyDataLow=ptr&255,EnemyDataHigh=ptr>>8,EnemyDataOffset=7,
          EnemyObjectPageLoc=2,EnemyObjectPageSel=0)
    for i in range(6):
        model[I.address(b,'Enemy_Flag')+i]=0
        model[I.address(b,'EnemyMetasprite')+i]=0


def actors(model):
    return [dict(slot=i,id=N.get(model,'Enemy_ID',i),
                 x=N.get(model,'Enemy_X_Position',i)+256*N.get(model,'Enemy_PageLoc',i),
                 y=N.get(model,'Enemy_Y_Position',i),state=N.get(model,'Enemy_State',i),
                 dir=N.get(model,'Enemy_MovingDir',i),speed=N.get(model,'Enemy_X_Speed',i))
            for i in range(6) if N.get(model,'Enemy_Flag',i)==1]


def query_support(model,x,y):
    block = 'Block_Buffer_2' if x&0x100 else 'Block_Buffer_1'
    at = I.address(model.bundle,block)+((x&255)>>4)+16*((y-32)>>4)
    return model[at]


def replay(env,seed,labels,threshold,extra_camera):
    model = N.fork(seed)
    Seam.terrain(model,tiles(224))
    Seam.layout(model,513+extra_camera,745,scroll=0)
    install_group(model)
    events,poses,maximum_cap = {},[],0
    attempted = admitted = False
    terminal = None
    pad = 1
    for epoch in range(185):
        row = Current.row(model,epoch)
        left,right = Seam.xcamera(model)
        live = actors(model)
        row.update(left=left,right=right,actors=live,pad=pad)
        if live and 'first_group' not in events:
            events['first_group'] = row
        if row['hp']<5 or row['engine']!=8 or row['lives']!=2:
            terminal = 'actual-contact-or-life'
            events['contact'] = row
            break
        support = row['native_state']==0 and row['y']==112 and any(
            query_support(model,row['x']+dx,144)&0xfc==0x10 for dx in (2,13))
        ready = support and row['action']==1 and row['mode']==1 and 6<=row['frame']<=13 and not model.ram[2][0x6c0]
        if ready:
            maximum_cap=max(maximum_cap,row['x'])
        if ready and row['x']>=threshold and not attempted:
            events['takeoff']=row
            attempted=True
        if attempted and not admitted and row['action']==4:
            events['admission']=row
            admitted=True
        if admitted and (not poses or poses[-1]['frame']!=row['frame']):
            poses.append(row)
        if admitted and row['x']>=784 and row['y']==176 and row['native_state']==0:
            events.setdefault('far_ground',row)
        if admitted and 'far_ground' in events and 'first_group' in events and row['x']>=864:
            terminal = 'cleared-group-ground'
            break
        if not attempted and row['y']>151:
            terminal = 'left-cap-without-legal-running-A'
            break
        pad=129 if attempted and not admitted else 1
        controls(env,model,labels,pad)
    return dict(threshold=threshold,explicit_camera_advance=extra_camera,maximum_supported_run_ready_X=maximum_cap,
                events=events,poses=poses,terminal=terminal or 'bound',end=row)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not (out/'route.json').exists()
    assert sha256(ROM.read_bytes()).hexdigest()==PIN
    proof=Current.read(ROOT/'candidate.json')
    third,full,diag=(Current.read(CAPTURE/n) for n in ('third-pipe.json','full11.json','prince-diagnostic.json'))
    assert proof['candidate_SHA256']==third['ROM_sha256']==full['ROM_sha256']==diag['ROM_sha256']==PIN
    assert third['passed'] and not full['passed'] and full['HP']==0 and full['admitted']==1294
    contact,=diag['first_pipe_route']['precontacts']
    hp=diag['first_pipe_route']['HP_bus_writes'][1:]
    assert [w['write_value'] for w in hp]==[4,3,2,1,0] and all(w['PC']==0xa345 for w in hp)
    assert contact['native_player_world']==[803,185,815,209] and contact['native_enemy_world']==[815,198,825,204]
    template,_,_=Current.current()
    base=dict(template,raw=ROM.read_bytes())
    env,seed,labels,start=roof(base)
    results=[]
    for offset,threshold in ((0,745),(0,749),(0,752),(0,755),(0,758),(0,761),(0,764),(0,766),
                             (16,745),(32,745),(48,745)):
        row=replay(env,seed,labels,threshold,offset)
        results.append(row)
        print(offset,threshold,row['maximum_supported_run_ready_X'],row['terminal'],
              {k:(v['epoch'],v['x'],v['right'],[(a['x'],a['dir']) for a in v['actors']])
               for k,v in row['events'].items()},flush=True)
    out.mkdir(exist_ok=True)
    refs=(Path(__file__),ROM,ROOT/'candidate.json',CAPTURE/'third-pipe.json',CAPTURE/'full11.json',
          CAPTURE/'prince-diagnostic.json',R/'src/level_tiles.s',R/'src/object.s',R/'src/collision.s',
          R/'build/prince-actor-1101-v1/contact-core.s',R/'build/prince-actor-1101-v1/native-battle-v149.s')
    receipt=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=PIN,contact=contact,
                 reference_supported_run=start,results=results,
                 scope='CPU fixtures set cap/world camera origin, the flat typed metatiles, and the genuine 1-1 group parser cursor. '
                       'Native parser creates actors. All following inputs are controller-only. Nonzero extra camera is an explicit '
                       'sensitivity fixture and needs independently controller-earned camera advance before native use.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'route.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
