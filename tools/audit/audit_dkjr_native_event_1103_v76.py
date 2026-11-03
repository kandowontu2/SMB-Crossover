"""Record the first actual stomp-route/original-state mismatch from75."""
import collections
import json
from pathlib import Path
import check_dkjr_native_event_1103_v75 as P


def main():
    b, m, L, q = P.fixture()
    m.ram[2][0x6b] = m.ram[2][0x6c] = 1
    m.ram[2][0x54] = m.ram[2][0x68] = 0
    oracle = P.D.D.Bus()
    oracle[:0x800] = P.source(m)
    oracle[0x6b] = 3
    P.D.original_call(oracle, 0xd257)
    P.N.put(m, Player_Y_Speed=0)
    counts, recent = collections.Counter(), []
    old = P.N.NesMPU
    class Trace(old):
        def step(self):
            bank = self.memory.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else -1
            if bank == 3 and self.pc in [L['DkNativeBounce'], L['DkjrJumpRestart']]:
                counts['event' if self.pc == L['DkNativeBounce'] else 'D257'] += 1
            if bank == 252:
                recent.append([self.pc, self.a, self.x, self.y, self.p])
            return super().step()
    P.N.NesMPU = Trace
    try:
        z = P.N.invoke(m, 'MegaManBounceVelocity', a=0, x=3, y=199, p=0x30)
    finally:
        P.N.NesMPU = old
    differences = [[i, a, c] for i, (a, c) in enumerate(zip(oracle[:0x800], P.source(m))) if a != c]
    out = dict(passed=True, qualification_complete=False, ROM_written=False,
        retained_negative='native-event-v75-negative.json', actual_event_calls=dict(counts),
        first_original_state_differences=differences[:32], native_return=z,
        actual124_trace=recent[:128],
        scope='Single first failing75 legal fixture, recording real current124 call chain and source-state witness; not a source-motion or native admission pass.',
        bindings={p.relative_to(P.R).as_posix(): P.A.sha(p.read_bytes()) for p in [Path(__file__), Path(P.__file__), P.O/'native-event-v75-negative.json']})
    (P.O/'native-event-v76-diagnostic.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['passed','actual_event_calls','first_original_state_differences','native_return','actual124_trace']}))


if __name__ == '__main__':
    main()
