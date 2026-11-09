"""Check the exact Mini fixed-route jump into its already selected native side leaf."""

import argparse
from collections import defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path

import check_mini_native_collision_routes_async_1109_v1 as Async
from check_mini_native_side_single_map_1109_v1 import N, R, bind, offset, sha
from prepare_mini_side_alias_1108 import compare_memory


BASE = R / 'build/mini-box-terrain-visible-1110/candidate.nes'
PIN = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
PROFILE = R / 'build/mini-final-peak-1110/capture/instruction-sample.json'
SOURCE = R / 'tools/reference/mini_native_side_single_map_1109_v1.s'
FILTER = R / 'tools/reference/mini_mario_idle_fast.s'
SITE = offset(126, 0x913e)


def image():
    raw = BASE.read_bytes()
    assert sha(BASE) == PIN
    assert raw[offset(126, 0x90e4):offset(126, 0x90ee)].hex() == '8d6a01ad02604929f04f'
    assert raw[SITE-1:SITE+6].hex() == 'a99b8d6c0130bb'
    assert raw[offset(126, 0x90ff):offset(126, 0x9109)].hex() == 'a9ad8d6d01a9fc4c5a01'
    assert raw[offset(124, 0xaad9):offset(124, 0xaadc)].hex() == '4c9bad'
    assert raw[offset(124, 0xad9b):offset(124, 0xadae)].hex() == '8d6a0108ad0260c929f0034c84aa28208b9508'
    assert raw[offset(126, 0x9c85):offset(126, 0x9c88)].hex() == '2097e4'
    assert raw[offset(126, 0x9cac):offset(126, 0x9caf)].hex() == '2097e4'
    return raw, raw[:SITE] + bytes([0xaa]) + raw[SITE+1:]


def leaves(before, after):
    seeds = [N.fresh(bind(raw)) for raw in (before, after)]
    cases = [(41, engine, y, (tile*37)&255, (8,31,32,135,206)[tile%5], tile, p)
             for engine,y,tile,p in product((4,8),(17,18,19,20),range(256),(0x20,0x61))]
    cases += [(owner, engine, y, 250, 135, tile, 0x61) for owner,engine,y,tile in
              product((0,2,4,6,10,11,14,15,19,23,25,32,37,38,39,40,42,255),(4,8),
                      (17,20),(0,0x12,0x26,0x54,0xc2,0xc3))]
    costs = defaultdict(list)
    for owner,engine,y,x,height,tile,p in cases:
        pair = [N.fork(m) for m in seeds]
        returns = []
        mapper = []
        for m in pair:
            N.put(m, SelectedCharacter=owner, GameEngineSubroutine=engine,
                  Player_X_Position=x, Player_PageLoc=1, Player_Y_Position=height, Player_Y_HighPos=1)
            N.invoke(m,'BlockBufferColli_Side',y=y)
            m[m[9]+256*m[10]+m[5]]=tile
            start=len(m.writes)
            returns.append(N.invoke(m,'SideFixed',a=height,x=0,y=y,p=p))
            mapper.append([q for q in m.writes[start:] if 0x5113<=q[0]<=0x5117])
        compare_memory(*pair)
        assert mapper[0]==mapper[1]
        for k in ('A','X','Y','P'):
            assert returns[0][k]==returns[1][k],(owner,engine,y,tile,k)
        expected = [0x16c] if owner==41 else []
        assert [i for i in range(0x15a,0x17b) if pair[0][i]!=pair[1][i]] == expected
        if owner==41:
            assert (pair[0][0x16c],pair[1][0x16c])==(0x9b,0xaa)
        costs[owner==41].append(returns[0]['CPU']-returns[1]['CPU'])
    assert len(set(costs[True]))==1 and set(costs[False])=={0}
    return {('Mini' if key else 'foreign'):dict(cases=len(value), cycles_saved=sorted(set(value)))
            for key,value in costs.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True)
    before, after = image()
    profile = json.loads(PROFILE.read_text())
    assert profile['scene']['frame']==1971 and profile['scene']['x']==1511
    peak_calls = sum(v for k,v in profile['farcall_edges'].items() if k.endswith('-> fc:ad9b'))
    assert peak_calls==4
    measures = leaves(before, after)
    print(json.dumps(measures),flush=True)
    interrupt = Async.check(after,head=True,adder=True)
    q = dict(passed=True, source_CPU_only=True, ROM_written=False, parent_SHA256=PIN,
        expected_memory_only_SHA256=hashlib.sha256(after).hexdigest(),
        patches=[dict(bank=126,pc=0x913e,file_offset=SITE,old_hex='9b',new_hex='aa')],
        leaves=measures, actual_peak_calls=peak_calls,
        expected_peak_cycles_saved=peak_calls*measures['Mini']['cycles_saved'][0],
        exact_non_Mini=True, transient_SMC_delta=0x16c, interrupt=interrupt,
        bindings={str(p.resolve()):sha(p) for p in (Path(__file__),BASE,PROFILE,SOURCE,FILTER,Path(Async.__file__))})
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k] for k in ('expected_memory_only_SHA256','expected_peak_cycles_saved','interrupt')}))


if __name__=='__main__':
    main()
