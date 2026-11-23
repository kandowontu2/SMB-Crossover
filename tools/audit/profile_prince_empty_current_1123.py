"""Exact6201 Prince empty-opening exclusive CPU profile; stdout only.

Uses the established real compiled menu/cold front end, then serial pads and
normal logical NMI. No gameplay/image edits, extracted files, or emulator.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import profile_dkjr_empty_current_1123 as D
import probe_prince_hidden_life_current_1123 as Prince

W, N, B = D.W, D.N, D.Opening
PIN = D.PIN


def authentication(raw):
    assert sha256(raw).hexdigest() == PIN
    head, parts, sizes = Prince.Packet.extract(raw)
    assert sha256(head).hexdigest() == Prince.HEADER
    assert tuple(sha256(p).hexdigest() for p in parts) == Prince.PARTS
    assert raw[Prince.Packet.COOKIE:Prince.Packet.COOKIE+16].hex() == Prince.COOKIE
    return dict(packet_header_SHA256=Prince.HEADER, part_SHA256=Prince.PARTS,
        packed_sizes=sizes, cookie=Prince.COOKIE)


def cold(raw):
    # Keep the current front end and its actual PauseRoutine rebind intact.
    # Only replace its obsolete unrelated-ROM hash gate with exact6201 plus
    # the same immutable Prince code/data/cookie authentication.
    function = Prince.clone(Prince.cold, dict(authenticate=authentication))
    m = function(raw)
    for _ in range(4):
        B.main_step(m, 0)
    return m


def snapshot(m):
    r = m.ram[2]
    return dict(x=B.position(m),y=N.get(m,'Player_Y_Position'),high=N.get(m,'Player_Y_HighPos'),
        native=N.get(m,'Player_State'),action=r[0x616],pose=r[0x617],mode=r[0x618],
        foot=r[0x84]+256*r[0x85],phase=r[0xa6],input=N.get(m,'SavedJoypad1Bits'))


def grounded(m, strict=True):
    # Same authored floor/support contract as retained prince40a E161:
    # running source poses can export Y177 before the next native clamp.
    s = snapshot(m)
    assert s['high']==1 and s['native'] in (0,2) and 174<=s['y']<=178 and 207<=s['foot']<=211,s
    def solid(x,y):
        tile = m[0x300+((x//256)&1)*208+(y&240)-32+((x&255)//16)]
        return m[W.address(m.bundle,'MTileAttribute')+tile]&1
    assert solid(s['x']+2,s['y']+32) or solid(s['x']+13,s['y']+32),('Actual authored floor support',s)
    if strict:
        assert s['native']==0,s
    return s


def run(raw, count):
    bound = authentication(raw)
    m = cold(raw)
    phases = {}
    for phase, pad in (('standing', 0), ('walking', 1)):
        warmup = []
        if pad:
            initial_x = B.position(m)
            for age in range(96):
                before = B.position(m)
                main,nmi = B.main_step(m,pad)
                warmup.append(dict(age=age,x_before=before,x_after=B.position(m),
                    main_cycles=main,NMI_cycles=nmi))
                assert not any(B.flags(m)) and N.get(m,'NumberofLives')==2
                grounded(m,False)
                if B.position(m)>initial_x:
                    break
            else:
                raise AssertionError(('No actual walking after ordinary Right warmup',warmup[-4:]))
        trace, rows = D.Trace(m), []
        excluded, all_costs = [], []
        for tick in range(count*4):
            before = B.position(m)
            assert not any(B.flags(m))
            previous = grounded(m,False)
            counters = ('cycles','instructions','calls','counts','entries')
            checkpoint = {name:getattr(trace,name).copy() for name in counters}
            cycles, nmi = B.main_step(m, pad, trace)
            assert not any(B.flags(m)) and N.get(m,'NumberofLives') == 2
            assert N.get(m,'SelectedCharacter') == 38 and N.get(m,'GameEngineSubroutine') == 8
            assert m.ram[2][0x6cf] == 5
            actual = grounded(m,False)
            all_costs.append(cycles)
            if previous['native']!=0 or actual['native']!=0:
                # Keep this real source-floor transient visible, but avoid
                # calling its native State2 a strictly grounded sample.
                excluded.append(dict(before=previous,after=actual,cycles=cycles))
                for name,value in checkpoint.items():
                    setattr(trace,name,value)
                continue
            rows.append(dict(update=tick,x_before=before,x_after=B.position(m),y=actual['y'],
                source=actual,main_cycles=cycles,NMI_cycles=nmi))
            if len(rows)==count:
                break
        assert len(rows)==count,('Finite fully grounded sample',phase,len(rows),excluded[-2:])
        row = trace.summary(rows)
        row['all_ordinary_returns'] = dict(count=len(all_costs),mean_cycles=sum(all_costs)/len(all_costs),
            excluded_native_State2=len(excluded),first_excluded=excluded[:1])
        row['warmup'] = dict(updates=len(warmup),first=warmup[:1],last=warmup[-1:])
        groups = dict(full_header=(193,0xaf27,0xaf50),shared_selector=(193,0xa743,0xa7bf),
            shared_transport=(193,0xaaf7,0xab72),SMC_transport=(-1,0x15a,0x17b))
        row['exclusive_cycles_per_Main'] = {name:sum(cycles for (tag,pc),cycles in trace.cycles.items()
            if tag==bank and low<=pc<high)/count for name,(bank,low,high) in groups.items()}
        row['hot_instructions'] = row['hot_instructions'][:12]
        row['hot_regions'] = row['hot_regions'][:20]
        # Includes deeply nested wrappers. These totals are explicitly
        # inclusive and must not be added to exclusive instruction costs.
        row['hot_FarCallCommon'] = row['hot_FarCallCommon'][:22]
        phases[phase] = row
        if pad:
            assert rows[-1]['x_after']>rows[0]['x_before'], 'Actual sampled walk displacement'
    result = dict(passed=True,ROM_SHA256=PIN,authentication=bound,
        source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_CPU_only=True,Mesen_run=False,retained_outputs=0,
        normal_logical_NMI=True,physical_cadence_qualified=False,phases=phases)
    canonical = json.dumps(result,sort_keys=True,separators=(',',':'))
    print('PRINCE EMPTY RECEIPT '+json.dumps(dict(result=result,
        receipt_SHA256=sha256(canonical.encode()).hexdigest()),separators=(',',':')),flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--count',type=int,default=16)
    a = ap.parse_args()
    assert 4 <= a.count <= 24
    run(D.Old.ROM.read_bytes(),a.count)


if __name__ == '__main__':
    main()
