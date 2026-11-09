"""Attribute the current DK Jr idle cost to actual typed callbacks and mapper calls."""
from collections import Counter
from pathlib import Path
import json

import prepare_dkjr_current_route_1110_v1 as R

I, N = R.I, R.I.N


def main():
    raw, _, cookie, _ = R.pinned_inputs()
    cpu, invoke = N.NesMPU, N.invoke
    banks, service_calls, auth_cycles, edges, PCs = (Counter() for _ in range(5))
    active = False
    main_epoch = 0
    pending_auth = None

    class Trace(cpu):
        def step(self):
            nonlocal pending_auth
            if not active:
                return super().step()
            m = self.memory
            pc, sp, cycle = self.pc, self.sp, self.processorCycles
            bank = m.rawtags[(pc - 0x8000) // 8192] if pc >= 0x8000 else 'RAM'
            if pending_auth and (pc, sp) == pending_auth[:2]:
                auth_cycles[pending_auth[2]] += cycle - pending_auth[3]
                pending_auth = None
            if (bank, pc) == (193, 0xaee2):
                lo, hi = m[0x16c], m[0x16d]
                row = str((lo - 0x8c) // 3) if hi == 0xb0 and 0x8c <= lo <= 0xfb else f'{hi:02x}{lo:02x}'
                service_calls[row] += 1
                ret = (1 + m[0x101 + sp] + 256 * m[0x102 + sp]) & 0xffff
                assert pending_auth is None
                pending_auth = ret, sp + 2, row, cycle
            if pc == 0x15a:
                caller = (1 + m[0x101 + sp] + 256 * m[0x102 + sp]) & 0xffff
                bank_from = m.rawtags[(caller - 0x8000) // 8192] if caller >= 0x8000 else 'RAM'
                edges[f'{bank_from}:{caller:04x} to {self.a:02x}:{m[0x16d]:02x}{m[0x16c]:02x}'] += 1
            result = super().step()
            cost = self.processorCycles - cycle
            banks[str(bank)] += cost
            PCs[f'{bank}:{pc:04x}'] += cost
            return result

    def record(m, name, *args, **kwargs):
        nonlocal active, main_epoch
        if name == 'GameCoreRoutine':
            main_epoch += 1
        active = name == 'GameCoreRoutine' and 2 <= main_epoch <= 13
        try:
            return invoke(m, name, *args, **kwargs)
        finally:
            active = False
            assert pending_auth is None

    N.NesMPU, N.invoke = Trace, record
    try:
        result = I.cpu(raw, cookie)
    finally:
        N.NesMPU, N.invoke = cpu, invoke
    idle = result['controls'][0]
    assert idle['updates'] == 12 and sum(banks.values()) == round(idle['mean_CPU'] * 12)
    output = dict(passed=True, ROM_written=False, memory_only_SHA256=R.PIN, idle=idle,
                  banks=banks.most_common(), service_calls=service_calls, auth_cycles=auth_cycles,
                  farcalls=edges.most_common(), top_PCs=PCs.most_common(28),
                  scope='Actual linked CPU GameCore with a legal cold floor fixture. Twelve source Main updates, not video frames.',
                  bindings={str(p.relative_to(R.R)): I.sha(p.read_bytes())
                            for p in [Path(__file__), Path(R.__file__), R.OUT/'rebase.json']})
    (R.OUT/'idle-profile.json').write_text(json.dumps(output, indent=2) + '\n')
    print('DK Jr typed idle calls', dict(service_calls), 'auth CPU', sum(auth_cycles.values()) // 12, flush=True)


if __name__ == '__main__':
    main()
