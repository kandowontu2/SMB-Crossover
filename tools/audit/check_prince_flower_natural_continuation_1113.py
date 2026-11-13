"""Controller continuations from an actual naturally earned flower prefix.

CPU/Main/NMI model only. No injected positions, items or inventory, no files,
and no physical raster/cadence claim. Each branch clones the same real prefix.
"""
from hashlib import sha256
import argparse
import json

import check_prince_natural_sword_1113 as P


def state(model):
    return dict(x=P.N.get(model,'Player_X_Position')+256*P.N.get(model,'Player_PageLoc'),
        y=P.N.get(model,'Player_Y_Position'),action=model.ram[2][0x616],
        mode=model.ram[2][0x618],facing=model.ram[2][0x615],
        sword=model.ram[2][0x6ee],lives=P.N.get(model,'NumberofLives'),
        health=model.ram[2][0x6cf],item=P.N.get(model,'Enemy_Flag',5))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--held',type=int,choices=(1,2,4,8,12,16,24))
    parser.add_argument('--direction',type=int,choices=(1,2),default=1)
    parser.add_argument('--limit',type=int,default=420)
    args=parser.parse_args()
    assert 260<=args.limit<=600
    raw=P.Base.C.ROM.read_bytes()
    model,opening=P.cold(raw)
    prefix=P.route(model,raw,2541)
    initial=state(model)
    assert not prefix['stopped'] and (initial['x'],initial['y'],initial['sword'])==(1214,176,0)
    assert P.N.get(model,'Enemy_ID',5)==46 and P.N.get(model,'PowerUpType',5)==1
    assert P.N.get(model,'Enemy_State',5)==128 and initial['item']==1
    print(json.dumps(dict(prefix_natural=True,ROM_SHA256=sha256(raw).hexdigest(),
        controller_SHA256=prefix['controller_SHA256'],opening=opening,initial=initial)),flush=True)
    rows=[]
    for direction in (args.direction,):
      for held in ((args.held,) if args.held is not None else (1,2,4,8,12,16,24)):
        trial=P.Base.C.L.clone(model)
        minimum=176;climbed=False;earned=None;rest=None
        for tick in range(args.limit):
            s=state(trial)
            if tick<8:pad=0
            elif tick<8+held:pad=direction
            elif tick<68+held:pad=0
            elif not climbed:pad=8
            else:pad=2 if s['x']>1252 else 1 if s['x']<1240 else 0
            trial.controller_pad=pad
            P.Frames.frame(trial)
            s=state(trial);minimum=min(minimum,s['y'])
            if tick==67+held:rest=s
            climbed|=s['y']<=114
            assert s['lives']==2 and s['health']>0
            if s['sword']:
                assert s['item']==0
                earned=dict(tick=tick,state=s);break
        row=dict(direction=direction,held=held,rest=rest,minimum_y=minimum,
            climbed=climbed,earned=earned,terminal=state(trial))
        rows.append(row)
        if earned:break
      if earned:break
    print(json.dumps(dict(passed=True,rows=rows,actual_natural_sword=any(r['earned'] for r in rows),
        runtime_injections=0,output_files=0,physical_Mesen=False)),flush=True)


if __name__=='__main__':main()
