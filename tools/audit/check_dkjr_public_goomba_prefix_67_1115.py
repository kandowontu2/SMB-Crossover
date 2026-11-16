"""Current67 unmodified-code source prefix and bounded native-probe API check."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import replay_dkjr_public_goomba_probe_67_1115 as F
import check_dkjr_public_first_pipe_67_1115 as Cold


def main():
    raw = F.F.Old.NIGHTLY.read_bytes()
    text, labels = F.controller(raw)
    text = Cold.one(text, "local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''", f'local rom="{F.F.Old.PIN}"')
    text = Cold.one(text, "os.getenv('SMB_TEST_VARIANT')=='0'", 'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'") == 2
    text = text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'", 'true')
    text = Cold.one(text, "emu.addEventCallback(guarded('input',function()",
                    "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\n"
                    "emu.addEventCallback(guarded('input',function()")
    text = Cold.one(text, ' local player,y=x(),read(0xbd)\n',
                    " local player,y=x(),read(0xbd)\n"
                    " if player>=850 then finish(true,'source-three-pipes-forward-Goomba-window');return end\n")
    opening, memory = Cold.first_active_cold(raw)
    ticks = 0
    def after(m):
        nonlocal ticks
        ticks += 1
        if ticks % 1000 == 0:
            print('DKJR_GOOMBA_PREFIX_PROGRESS '+json.dumps(dict(tick=ticks, **Cold.B.state(m))), file=output, flush=True)
    output = __import__('sys').stdout
    with redirect_stdout(io.StringIO()):
        result = Cold.B.route(memory, raw, 4200, controller_text=text, after_frame=after)
    receipt = result['receipt'] or {}
    selected = {key: value for key, value in receipt.items() if key.startswith('goomba3_')}
    report = dict(source_diagnostic_complete=result['stopped'], source_window_passed=result['passed'],
                  actual_ROM_SHA256=F.F.Old.PIN, source_Lua_SHA256=sha256(text.encode()).hexdigest(),
                  native_Lua_SHA256=sha256(F.controller(raw)[0].encode()).hexdigest(),
                  source_updates=result['logical_updates'], final=result['final'], reason=receipt.get('reason'),
                  opening=opening, witnesses=selected, latest_events=receipt.get('events', [])[-3:],
                  actual_hook_bindings=labels, game_code_changed=False, game_state_seeds=False,
                  output_files=0, native_claim=False)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_GOOMBA_PREFIX '+encoded, flush=True)
    print('DKJR_GOOMBA_PREFIX_SHA256 '+sha256(encoded.encode()).hexdigest(), flush=True)
    assert result['stopped']


if __name__ == '__main__':
    main()
