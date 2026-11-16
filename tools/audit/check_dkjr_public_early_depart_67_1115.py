"""Genuine current67 prefix through pipe3 and ordinary early enemy hop."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import replay_dkjr_public_early_depart_67_1115 as F
import check_dkjr_public_first_pipe_67_1115 as Cold


def source_controller(raw):
    text = F.controller(raw)
    text = Cold.one(text, "local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''", f'local rom="{F.Old.PIN}"')
    text = Cold.one(text, "os.getenv('SMB_TEST_VARIANT')=='0'", 'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'") == 2
    text = text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'", 'true')
    text = Cold.one(text, "emu.addEventCallback(guarded('input',function()",
                    "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\n"
                    "emu.addEventCallback(guarded('input',function()")
    return Cold.one(text, ' local player,y=x(),read(0xbd)\n',
                    " local player,y=x(),read(0xbd)\n"
                    " if player>=850 then finish(true,'source-early-depart-Goomba-window-clear');return end\n")


def main():
    raw = F.Old.NIGHTLY.read_bytes()
    text = source_controller(raw)
    opening, memory = Cold.first_active_cold(raw)
    ticks = 0
    first_injury = None
    injury_pc = Cold.W.address(memory.bundle, 'InjurePlayer')
    injury_bank = ((Cold.W.location(memory.bundle, 'InjurePlayer')-16)//8192)|128
    def observe(m, cpu):
        nonlocal first_injury
        if cpu.pc == injury_pc and m.rawtags[(cpu.pc-0x8000)//8192] == injury_bank and first_injury is None:
            first_injury = dict(PC=cpu.pc, SP=cpu.sp, tick=ticks, **Cold.B.state(m))
    def after(m):
        nonlocal ticks
        ticks += 1
        if ticks % 1000 == 0:
            print('DKJR_EARLY_DEPART_PROGRESS '+json.dumps(dict(tick=ticks, **Cold.B.state(m))), file=output, flush=True)
    output = __import__('sys').stdout
    with redirect_stdout(io.StringIO()):
        result = Cold.B.route(memory, raw, 5200, controller_text=text, observe_extra=observe, after_frame=after)
    receipt = result['receipt'] or {}
    events = [row for row in receipt.get('events', []) if row['event'] in
              ('pipe1-low-depart', 'third-static-ground-depart', 'third-depart-enemy-hop', 'enemy-hop')]
    early = [row for row in events if row['event'] == 'third-depart-enemy-hop']
    report = dict(passed=result['passed'], actual_ROM_SHA256=F.Old.PIN,
                  native_controller_Lua_SHA256=sha256(F.controller(raw).encode()).hexdigest(),
                  source_controller_Lua_SHA256=sha256(text.encode()).hexdigest(),
                  source_updates=result['logical_updates'], final=result['final'], reason=receipt.get('reason'),
                  first_native_injury=first_injury, selected_events=events[-8:],
                  early_hop_exercised=bool(early), first_three_crossings=receipt.get('crossings', [])[:3],
                  opening=opening, game_code_changed=False, game_state_seeds=False,
                  output_files=0, native_claim=False)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_PUBLIC_EARLY_DEPART '+encoded, flush=True)
    print('DKJR_PUBLIC_EARLY_DEPART_SHA256 '+sha256(encoded.encode()).hexdigest(), flush=True)
    assert result['passed'] and first_injury is None
    assert len(receipt.get('crossings', [])) >= 3 and result['final']['lives'] == 2
    assert early, 'Prefix passed but the new natural early-hop branch was not exercised'


if __name__ == '__main__':
    main()
