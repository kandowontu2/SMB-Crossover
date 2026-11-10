"""Continue the actual controller after Prince's first native gap, in memory."""
import argparse
from collections import deque

import check_prince_sonic_transport_1110 as Combined

C, N = Combined.C, Combined.N
F = Combined.Prince.F


def second_gap(context, epoch, use_turn, *, request_min=1340):
    env, model, labels = context
    state = 'second-approach'
    events = []
    tail = deque(maxlen=12)
    pad = 1
    for tick in range(epoch, epoch+650):
        row = F.sample(model, tick)
        x, y = row['x'], row['y']
        tail.append(row)
        if row['engine'] != 8 or row['lives'] != 2 or not row['hp']:
            state = 'second-contact-or-death'
            break
        old = state
        idle = row['support'] and (row['frame'], row['mode'], row['a_lock']) == (15,0,0)
        if state == 'second-approach' and x >= 1320 and use_turn:
            state, pad = 'second-brake', 0
        elif state == 'second-brake' and idle:
            state, pad = 'second-left', 2
        elif state == 'second-left' and x <= 1312 and row['facing'] == 0:
            state, pad = 'second-left-brake', 0
        elif state == 'second-left-brake' and idle:
            state, pad = 'second-runup', 1
        elif state in ('second-approach', 'second-runup'):
            if request_min <= x <= 1356 and row['phase'] <= 1 and C.Recovery.running(model,row):
                columns = [C.Route.query_support(model, px, 208) for px in range(1360,1425,16)]
                assert columns == [0x54,0,0,0,0x54], (row, columns)
                state, pad = 'second-request', 129
            elif x >= 1361:
                state = 'second-missed-takeoff'
                break
        elif state == 'second-request' and row['action'] == 4:
            state, pad = 'second-flight', 1
        elif state == 'second-flight':
            if x >= 1440 and y == 176 and row['support']:
                state = 'second-far-ground'
            elif y > 215:
                state = 'second-below-lip'
        if state != old:
            events.append(dict(stage=state, state=row))
        if state in ('second-far-ground','second-below-lip'):
            break
        C.Route.controls(env, model, labels, pad)
        N.consume(model)
    return dict(outcome=state, terminal=row, events=events, tail=list(tail))


def post_pair(context, epoch, approach):
    env, seed, labels = context
    model = Combined.Q.Sonic.slim_fork(seed)
    state, pad = ('prepare-running', 1) if approach == 'running' else ('prepare-standing', 0)
    events = []
    tail = deque(maxlen=10)
    lowest_y = 255
    initial_pair = [actor['slot'] for actor in F.sample(model, epoch)['actors']
                    if actor['id'] == 6 and actor['y'] == 184 and actor['x'] >= 1540]
    assert len(initial_pair) == 2
    for tick in range(epoch, epoch+270):
        row = F.sample(model, tick)
        x, y = row['x'], row['y']
        tail.append(row)
        if row['engine'] != 8 or row['lives'] != 2 or not row['hp']:
            state = 'pair-contact-or-death'
            break
        old = state
        idle = row['support'] and (row['frame'], row['mode'], row['a_lock']) == (15,0,0)
        live = [a for a in row['actors'] if a['slot'] in initial_pair and a['id'] == 6 and a['state'] < 2]
        closest = min((a['x']-x for a in live if a['x']>=x), default=999)
        if state == 'prepare-standing' and idle:
            if approach == 'climb-A':
                assert 1484 <= x <= 1501 and y == 176
                assert C.Route.query_support(model,1504,144) == 0x58
                state, pad = 'climb-request', 8
            else:
                state, pad = 'standing-request', 128 if approach == 'standing-A' else 129
        elif state == 'climb-request' and row['action'] in (24,25,10):
            state = 'climbing'
        elif state == 'climbing' and row['action'] == 10 and idle and 111 <= y <= 115:
            assert any(C.Route.query_support(model,x+dx,144) == 0x58 for dx in (2,13))
            state, pad = 'standing-request', 128
        elif state == 'prepare-running' and 40 <= closest <= 115 and C.Recovery.running(model,row):
            state, pad = 'running-request', 129
        elif state in ('standing-request','running-request') and row['action'] == (3 if state.startswith('standing') else 4):
            state, pad = 'pair-flight', 1
        elif state == 'pair-flight':
            lowest_y = min(lowest_y,y)
            if x >= 1573 and y <= 176 and row['support'] and all(a['x']+13 < x+2 for a in live):
                state = 'pair-behind'
        if state != old:
            events.append(dict(stage=state,state=row))
        if state == 'pair-behind':
            assert lowest_y < 176
            break
        C.Route.controls(env, model, labels, pad)
        N.consume(model)
    return dict(approach=approach,outcome=state,terminal=row,events=events,tail=list(tail),lowest_native_Y=lowest_y), model


def retreat_pair(context, epoch, *, settle, turn_before_jump=True, standing_reverse=False, back_up=False):
    """Reverse with original jumps and wait for the authored walkers to fall."""
    env, seed, labels = context
    model = Combined.Q.Sonic.slim_fork(seed)
    slots = {actor['slot'] for actor in F.sample(model, epoch)['actors']
             if actor['id'] == 6 and actor['y'] == 184 and actor['x'] >= 1540}
    assert len(slots) == 2
    state, pad = ('reverse-settle', 0) if settle else ('reverse-approach', 2)
    events, falls = [], {}
    tail = deque(maxlen=8)
    for tick in range(epoch, epoch + 650):
        row = F.sample(model, tick)
        x, y = row['x'], row['y']
        tail.append(row)
        if (row['hp'], row['lives'], row['engine']) != (4,2,8):
            state = 'retreat-injury-or-death'
            break
        if y > 215:
            state = 'retreat-below-bank'
            break
        prior = state
        running = row['support'] and row['action'] == row['mode'] == 1 and 6 <= row['frame'] <= 13 and row['a_lock'] == 0
        active = {a['slot']:a for a in row['actors'] if a['id'] == 6 and a['slot'] in slots}
        idle = row['support'] and (row['frame'], row['mode'], row['a_lock']) == (15,0,0)
        if state == 'reverse-settle' and idle:
            state, pad = ('reverse-face', 2) if standing_reverse else ('reverse-approach', 2)
        elif state == 'reverse-face' and row['facing'] == 0:
            state, pad = 'reverse-face-settle', 0
        elif state == 'reverse-face-settle' and idle:
            assert row['facing'] == 0 and x+2 >= 1424
            state, pad = 'reverse-standing-request', 128
        elif state == 'reverse-standing-request' and row['action'] == 3:
            assert row['facing'] == 0
            state, pad = 'reverse-flight', 2
        elif state == 'reverse-approach':
            nearest = min((a['x'] for a in active.values() if a['x'] > x), default=0)
            on_far_bank = x+2 >= 1424 and C.Route.query_support(model,x+2,208) == 0x54
            if 1432 <= x <= 1478 and nearest-x >= 34 and running and on_far_bank and row['facing'] == 0 and row['phase'] <= 1:
                state, pad = 'reverse-request', 130
            elif x < 1432:
                state = 'reverse-missed-takeoff'
                break
        elif state == 'reverse-request' and row['action'] == 4:
            state, pad = 'reverse-flight', 2
        elif state == 'reverse-flight' and y == 176 and row['support']:
            if x+2 < 1376 and C.Route.query_support(model,x+2,208) == 0x54:
                state, pad = 'native-fall-wait', 0
        elif state == 'native-fall-wait':
            for slot, actor in active.items():
                if 1376 <= actor['x'] < 1424 and actor['y'] >= 204 and slot not in falls:
                    falls[slot] = dict(epoch=tick, actor=actor)
            if len(falls) == len(slots) and not active and row['support'] and (row['frame'],row['mode']) == (15,0):
                if back_up:
                    assert row['facing'] == 0 and row['camera_left'] + 16 <= x
                    state, pad = 'return-back-up', 2
                elif x >= 1340:
                    state, pad = ('return-turn', 1) if turn_before_jump else ('return-standing-request', 129)
                else:
                    state, pad = 'return-approach', 1
        elif state == 'return-back-up' and x <= row['camera_left'] + 4:
            state, pad = 'return-back-up-settle', 0
        elif state == 'return-back-up-settle' and idle:
            assert row['facing'] == 0 and x + 13 < 1376
            state, pad = 'return-turn', 1
        elif state == 'return-turn' and row['facing'] == 255:
            state, pad = 'return-turn-settle', 0
        elif state == 'return-turn-settle' and row['support'] and (row['frame'],row['mode'],row['a_lock']) == (15,0,0):
            if back_up:
                assert row['facing'] == 255 and x + 13 < 1376
                assert C.Route.query_support(model,x+13,208) == 0x54
            state, pad = 'return-standing-request', 128
        elif state == 'return-approach':
            if 1335 <= x <= 1358 and running and row['facing'] == 255 and row['phase'] <= 1:
                state, pad = 'return-request', 129
            elif x > 1362:
                state = 'return-missed-takeoff'
                break
        elif state == 'return-request' and row['action'] == 4:
            state, pad = 'return-flight', 1
        elif state == 'return-standing-request' and row['action'] in (3,4):
            state, pad = 'return-flight', 1
        elif state == 'return-flight' and x >= 1440 and y == 176 and row['support']:
            state = 'pair-native-falls-and-return'
        if prior != state:
            events.append(dict(stage=state,state=row))
        if state == 'pair-native-falls-and-return':
            break
        C.Route.controls(env, model, labels, pad)
        N.consume(model)
    approach = 'retreat' if settle else 'retreat-direct'
    if not turn_before_jump:
        approach = 'retreat-unturned'
    if standing_reverse:
        approach = 'retreat-standing'
    if back_up:
        approach = 'retreat-standing-backup'
    return dict(approach=approach, outcome=state, terminal=row, events=events,
                native_goomba_falls=falls, tail=list(tail)), model


def run_past_pair(context, epoch):
    env, model, labels = context
    for tick in range(epoch, epoch + 150):
        row = F.sample(model, tick)
        assert (row['engine'], row['hp'], row['lives']) == (8,4,2), row
        if row['x'] >= 1545 and row['y'] == 176 and row['support']:
            return row
        C.Route.controls(env, model, labels, 1)
        N.consume(model)
    raise AssertionError(('Original right run beyond the retired Goombas',row))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--turn', action='store_true')
    parser.add_argument('--earliest-second', action='store_true')
    parser.add_argument('--second-request-min', type=int, choices=range(1328,1341))
    parser.add_argument('--post-pair', action='store_true')
    parser.add_argument('--approach', choices=('retreat','retreat-direct','retreat-unturned',
                        'retreat-standing','retreat-standing-backup','climb-A',
                        'standing-A','standing-forward-A','running'))
    parser.add_argument('--sonic-scene', action='store_true')
    parser.add_argument('--installed', action='store_true', help='Read the verified 47a7 nightly directly')
    args = parser.parse_args()
    minimum = args.second_request_min
    if minimum is None:
        minimum = 1328 if args.earliest_second else 1340
    if args.approach == 'retreat-standing-backup' and not (args.turn and minimum == 1328):
        parser.error('retreat-standing-backup needs the wider run-up (--turn --earliest-second)')
    if args.installed:
        raw = Combined.Stage.NIGHTLY.read_bytes()
        expected = Combined.COMBINED[Combined.SCENE_PARENT]
        assert Combined.Q.digest(raw) == expected
        result = None, C.Start.W.bundle(raw), None, {'in_memory_SHA256':expected}, None, None, None
    else:
        result = Combined.proposal(sonic_scene=args.sonic_scene)
    route, _, context = Combined.first_gap(result)
    assert context is not None
    Combined.emit('PRINCE_SONIC_ROUTE', route)
    late = second_gap(context, route['first_gap']['epoch'], args.turn, request_min=minimum)
    Combined.emit('PRINCE_AFTER_FIRST_GAP', {k:v for k,v in late.items() if k!='tail' or late['outcome']!='second-far-ground'})
    if not args.turn and minimum == 1340:
        assert late['outcome'] == 'second-far-ground'
        finish = late['terminal']
        assert (finish['epoch'],finish['x'],finish['y'],finish['hp'],finish['lives']) == (1016,1461,176,4,2)
    if args.approach == 'retreat-standing-backup':
        assert late['outcome'] == 'second-far-ground'
        assert (late['terminal']['epoch'],late['terminal']['x']) == (1244,1440)
    if (args.post_pair or args.approach) and late['outcome'] == 'second-far-ground':
        approaches = (args.approach,) if args.approach else ('climb-A','standing-A','standing-forward-A','running')
        for approach in approaches:
            epoch = late['terminal']['epoch']
            if approach.startswith('retreat'):
                pair, model = retreat_pair(context, epoch, settle=approach != 'retreat-direct',
                                           turn_before_jump=approach != 'retreat-unturned',
                                           standing_reverse=approach.startswith('retreat-standing'),
                                           back_up=approach == 'retreat-standing-backup')
            else:
                pair, model = post_pair(context, epoch, approach)
            successful = pair['outcome'] in ('pair-behind','pair-native-falls-and-return')
            Combined.emit('PRINCE_POST_PAIR', {k:v for k,v in pair.items() if k!='tail' or not successful})
            if approach == 'retreat-standing-backup':
                assert pair['outcome'] == 'pair-native-falls-and-return'
                assert (pair['terminal']['epoch'],pair['terminal']['x']) == (1760,1441)
            if pair['outcome'] == 'pair-native-falls-and-return':
                resumed = context[0], model, context[2]
                finish = run_past_pair(resumed,pair['terminal']['epoch'])
                if approach == 'retreat-standing-backup':
                    assert (finish['epoch'],finish['x'],finish['action']) == (1856,1547,1)
                Combined.emit('PRINCE_PAST_GOOMBAS', finish)


if __name__ == '__main__':
    main()
