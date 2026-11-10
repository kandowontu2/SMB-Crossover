"""Diagnose Prince's first post-gap Koopa with ordinary controller input."""
import argparse
from collections import deque

import check_prince_late_route_1110 as Late
import check_sonic_injury_prince_rebase_1110 as Current


C, N, F, Combined = Late.C, Late.N, Late.F, Late.Combined


def prefix(installed):
    if installed:
        raw = Combined.Stage.NIGHTLY.read_bytes()
    else:
        raw, _, _, _ = Current.reconstruct()
    assert Combined.Q.digest(raw) == Current.PIN
    image = C.Start.W.bundle(raw)
    route, _, context = Combined.first_gap((None, image, None, {'in_memory_SHA256':Current.PIN}, None, None, None))
    assert context is not None
    Combined.emit('PRINCE_FLAGPOLE_FIRST_GAP', route['first_gap'])
    late = Late.second_gap(context, route['first_gap']['epoch'], True, request_min=1328)
    assert (late['outcome'],late['terminal']['epoch'],late['terminal']['x']) == ('second-far-ground',1244,1440)
    pair, model = Late.retreat_pair(context,1244,settle=True,standing_reverse=True,back_up=True)
    assert (pair['outcome'],pair['terminal']['epoch'],pair['terminal']['x']) == ('pair-native-falls-and-return',1760,1441)
    context = context[0], model, context[2]
    pair_context = context[0], Combined.Q.Sonic.slim_fork(model), context[2]
    row = Late.run_past_pair(context,1760)
    assert (row['epoch'],row['x'],row['y'],row['hp'],row['lives']) == (1856,1547,176,4,2)
    Combined.emit('PRINCE_FLAGPOLE_START',row)
    return context, row['epoch'], pair_context


def view(model, row):
    x = row['x'] // 16 * 16
    last = min(x + 128, row['camera_right'] // 16 * 16)
    return dict(x_columns=list(range(x,last+1,16)),
                tiles={y:[C.Route.query_support(model,col,y) for col in range(x,last+1,16)]
                       for y in range(96,224,16)})


def enemies(context, epoch, limits, stop, *, takeoff=None, standing=False, stand_gap=None):
    env, seed, labels = context
    model = Combined.Q.Sonic.slim_fork(seed)
    floor = {'events':[], 'tail':deque(maxlen=10)}
    pad, state = 1, 'prepare' if takeoff is not None else 'approach'
    previous_x, last_motion = 0, epoch
    for tick in range(epoch,epoch+430):
        row = F.sample(model,tick)
        x, y = row['x'], row['y']
        floor['tail'].append(row)
        if row['engine'] != 8 or row['lives'] != 2 or not row['hp']:
            outcome = 'contact-or-death'
            break
        if x >= stop and row['support']:
            outcome = 'supported-stop'
            break
        if x > previous_x:
            previous_x, last_motion = x, tick
        elif tick-last_motion > (230 if state == 'wait-for-koopa' else 75):
            outcome = 'stalled'
            break
        actors = [a for a in row['actors'] if a['id'] in (0,1,2,3,6,14) and a['state'] < 2
                  and abs(a['y']-y-8) <= 24 and a['x'] >= x]
        enemy = min(actors,key=lambda a:a['x'],default=None)
        before = state
        if state == 'prepare' and x >= takeoff:
            if standing:
                state, pad = 'settle',0
            elif C.Recovery.running(model,row):
                state, pad = 'request-running-A',129
        elif state == 'settle' and row['support'] and row['facing'] == 255 and (row['frame'],row['mode'],row['a_lock']) == (15,0,0):
            state, pad = ('request-standing-A',128) if stand_gap is None else ('wait-for-koopa',0)
        elif state == 'wait-for-koopa' and enemy and enemy['id'] == 0 and enemy['dir'] == 2 and enemy['x']-x <= stand_gap:
            state, pad = 'request-standing-A',128
        elif state == 'approach' and enemy and limits[0] <= enemy['x']-x <= limits[1] and C.Recovery.running(model,row):
            state, pad = 'request-running-A',129
        elif state.startswith('request-') and row['action'] == (3 if state == 'request-standing-A' else 4):
            state, pad = 'flight',1
        elif state == 'flight' and row['support'] and row['action'] not in (3,4):
            state = 'approach'
        if before != state:
            last_motion = tick
            floor['events'].append(dict(stage=state,row=row,terrain=view(model,row)))
        C.Route.controls(env,model,labels,pad)
        N.consume(model)
    else:
        outcome = 'bound'
    return dict(outcome=outcome,limits=limits,takeoff=takeoff,standing=standing,stand_gap=stand_gap,terminal=row,terrain=view(model,row),
                events=floor['events'],tail=list(floor['tail'])), model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed',action='store_true',help='Require the exact 49295a Downloads ROM')
    parser.add_argument('--wait-koopa',action='store_true')
    args = parser.parse_args()
    context, epoch, pair = prefix(args.installed)
    if args.wait_koopa:
        trials = [(context,epoch,(115,136),1554,True,None)]
        trials += [(pair,1760,(115,136),x,True,gap) for x in (1510,1526) for gap in (60,74,88,102)]
    else:
        bands = ((115,136),(135,156),(94,116),(70,95),(155,177),(52,72),(40,62),(27,49))
        trials = [(context,epoch,band,None,False,None) for band in bands]
        trials += [(pair,1760,(115,136),x,True,None) for x in (1480,1494,1510,1526,1545,1560,1580,1595)]
        trials += [(pair,1760,(115,136),x,False,None) for x in (1470,1480,1494,1510,1526,1540)]
    for seed, tick, limits, x, standing, gap in trials:
        result, _ = enemies(seed,tick,limits,1740,takeoff=x,standing=standing,stand_gap=gap)
        Combined.emit('PRINCE_NEXT_NATIVE_ENEMIES',result)
        if result['outcome'] == 'supported-stop':
            break


if __name__ == '__main__':
    main()
