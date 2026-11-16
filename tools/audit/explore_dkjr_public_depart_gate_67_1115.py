"""One short ordinary source window explains the retained departure-gate miss."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import check_dkjr_public_low_depart_67_1115 as C


def main():
    raw = C.F.Old.NIGHTLY.read_bytes()
    text = C.source_text(raw)
    text = C.Cold.one(text, 'local function drive()\n', 'local departGateWindows=0\nlocal function drive()\n')
    marker = '   local descending=priorTop[u]and up>priorTop[u]\n'
    diagnostic = '''   if descending and up>=154 and up<=160 then
    departGateWindows=departGateWindows+1;remember('pipe1-gate-window',up)
    local q=events[#events];q.grounded=grounded;q.actual_carried=not not carried(u,up)
    q.source_y=ram(2,0x210);q.native_feet=y+32;q.previous_top=priorTop[u]
    q.last_carry=carries[tostring(u)];q.direction=bits;q.origin=ram(2,0x76);q.limit=ram(2,0x7b)
    if departGateWindows>=3 then finish(true,'source-departure-gate-window');return end
   end
'''
    text = C.Cold.one(text, marker, marker+diagnostic)
    _, memory = C.Cold.first_active_cold(raw)
    with redirect_stdout(io.StringIO()):
        result = C.B.route(memory, raw, 1800, controller_text=text)
    receipt = result['receipt'] or {}
    rows = [row for row in receipt.get('events', []) if row['event'] == 'pipe1-gate-window']
    report = dict(diagnostic_complete=result['passed'], gameplay_qualification=False,
                  actual_ROM_SHA256=C.F.Old.PIN, source_Lua_SHA256=sha256(text.encode()).hexdigest(),
                  reason=receipt.get('reason'), windows=rows, final=result['final'],
                  logical_updates=result['logical_updates'], output_files=0, game_bytes_changed=False)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_DEPART_GATE_WINDOW '+encoded, flush=True)
    print('DKJR_DEPART_GATE_WINDOW_SHA256 '+sha256(encoded.encode()).hexdigest(), flush=True)
    assert result['passed'] and len(rows) == 3


if __name__ == '__main__':
    main()
