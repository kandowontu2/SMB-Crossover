"""Inclusive native-frame CPU cycle attribution, stdout only."""

import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from unittest.mock import patch

import audit_current_roster_powerups_1110 as Roster
import check_roster_powerup_continuation_1110 as Frames
import replay_steve_armor_native_1113 as Native


def profile(raw, *, invoke=0xc3bf):
    bundle = Roster.W.Symbols.bundle()
    bundle['raw'] = raw
    opening,m = Roster.cold(bundle,dict(name='STEVE HERMANN',slot=15,cycle=2,raw=16))
    N = Roster.N
    for _ in range(30):
        m.controller_pad = 0
        Frames.frame(m)
    assert N.get(m,'Player_State') == 0 and N.get(m,'Player_Y_Position') == 176
    results = {}
    base_cpu = N.NesMPU
    for phase,pad,count in (('idle',0,25),('walk',1,16)):
        costs = Counter()
        services = defaultdict(list)
        pending = None
        class ProfileCPU(base_cpu):
            def step(self):
                nonlocal pending
                pc,mem = self.pc,self.memory
                bank = mem.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
                if bank == 2 and pc == invoke:
                    assert pending is None
                    target = mem[0x101+self.sp]+256*mem[0x102+self.sp]+1
                    pending = (self.a,self.processorCycles,target,(self.sp+2)&255)
                key = f'bank{bank}'
                if bank == 2 and 0xc3bf <= pc < 0xc3fb:
                    key = 'raw2_auth'
                elif bank == 2 and 0xcd00 <= pc < 0xcd88:
                    key = 'raw2_bridge'
                elif bank == 1:
                    key = 'raw1_runtime'
                elif 0x15a <= pc < 0x17b:
                    key = 'farcall_RAM'
                cycles = self.processorCycles
                result = super().step()
                costs[key] += self.processorCycles-cycles
                if pending and (self.pc,self.sp) == pending[2:]:
                    mode,start,_,_ = pending
                    services[mode].append(self.processorCycles-start)
                    pending = None
                return result
        with patch.object(N,'NesMPU',ProfileCPU):
            for _ in range(count):
                m.controller_pad = pad
                Frames.frame(m)
                assert not any(0 < N.get(m,'Enemy_Flag',slot) < 128 and
                               N.get(m,'Enemy_ID',slot) < 21 for slot in range(6))
        assert pending is None
        results[phase] = dict(updates=count,total_cycles=sum(costs.values()),
            cycles_per_update=sum(costs.values())/count,
            region_cycles=dict(costs),services={str(mode):dict(calls=len(values),
                total=sum(values),mean=sum(values)/len(values),minimum=min(values),maximum=max(values))
                for mode,values in services.items()},
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))
    return dict(ROM_SHA256=Native.Packet.Entry.digest(raw),opening=opening,phases=results,
                source_CPU_cycles=True,Mesen_run=False,output_files=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=Native.Packet.Entry.ROOT/'build/metal-flower-native-1112/candidate.nes')
    args = parser.parse_args()
    parent = Native.Live.Art.D.HOST.read_bytes()
    candidate = args.candidate.read_bytes()
    assert Native.Packet.Entry.digest(parent) == 'aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1'
    assert Native.Packet.Entry.digest(candidate) in (
        '2aa5096391ddc303c4dc346293db1b628ddee36222fb3a7eaa20649c003b6cea',
        Native.IDLE_CANDIDATE)
    print(json.dumps(dict(parent=profile(parent),candidate=profile(candidate)),sort_keys=True),flush=True)
