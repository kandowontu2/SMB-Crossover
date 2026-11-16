"""Root exact-control complete DK Jr source route, with actual grounded work."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import compose_dkjr_forced_entry_current_1116 as C
import replay_dkjr_forced_entry_current_1116 as F
import check_dkjr_carry_camera_route_1116 as Route

H = lambda value: sha256(value).hexdigest()
FACTORY_SHA = '1caa3929abf8ff82d53e735d2c5e5620230abcc81f17aa2515cdbf3fa40c3a73'
SOURCE_LUA_SHA = 'c2cd707c63eb97d3e0ee63fe213334bb505d85c280f6b0ddffb107192ea872d4'


def main():
    assert H(Path(F.__file__).read_bytes()) == FACTORY_SHA
    raw, composition = C.current_proposal(C.BT.ROM.read_bytes())
    text = F.controller(raw, source=True)
    assert H(raw) == C.CANDIDATE and H(text.encode()) == SOURCE_LUA_SHA
    opening, memory = Route.cold(raw)
    assert memory.bundle['raw'] == raw
    assert all(bytes(memory.ram[b][0x1fe0:0x1ff0]) == raw[534485:534501] for b in (2, 3))
    print('PHASE '+json.dumps(dict(candidate=H(raw), source_Lua_SHA256=SOURCE_LUA_SHA,
                                  actual_compiled_cold=opening), separators=(',', ':')), flush=True)
    tick = 0
    first_bad = None
    out = __import__('sys').stdout
    counts = Counter()
    def after(m):
        nonlocal tick
        tick += 1
        if tick % 1000 == 0:
            print('PROGRESS '+json.dumps(dict(tick=tick, **Route.B.state(m)),
                                         separators=(',', ':')), file=out, flush=True)
    def observe(m, cpu):
        nonlocal first_bad
        tag = m.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc >= 0x8000 else -1
        if (tag, cpu.pc) == (2, 0xd65e):
            counts['D65E_entries'] += 1
        if first_bad is None and m.ram[2][0x6b] == 5:
            first_bad = dict(tick=tick, PC=cpu.pc, tag=tag, SP=cpu.sp,
                             origin=m.ram[2][0x76], limit=m.ram[2][0x7b],
                             sourceY=m.ram[2][0x210], **Route.B.state(m))
    with redirect_stdout(io.StringIO()):
        result = Route.B.route(memory, raw, 15000, controller_text=text,
                               observe_extra=observe, after_frame=after)
    receipt = result.get('receipt') or {}
    passed = bool(result['passed'] and receipt.get('original_work_grounded_returns', 0) >= 25
                  and receipt.get('grounded_12_return_count', 0) >= 25)
    report = dict(passed=passed, actual_CPU_ROM_SHA256=H(raw), factory_SHA256=FACTORY_SHA,
                  source_Lua_SHA256=SOURCE_LUA_SHA, composition=composition, opening=opening,
                  logical_updates=result['logical_updates'], reason=receipt.get('reason'),
                  terminal=result['final'], first_source5=first_bad, counts=dict(counts),
                  receipt={k: v for k, v in receipt.items() if k not in ('events', 'carries', 'trace', 'samples')},
                  carries={k: dict(count=v.get('count'), first=v.get('first'), last=v.get('last'))
                           for k, v in receipt.get('carries', {}).items()},
                  event_tail=receipt.get('events', [])[-8:], gameplay_outcome_seeds=False,
                  exact_root_controls=True, native_Mesen=False, outputs=0)
    report['receipt_SHA256'] = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
