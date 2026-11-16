"""Currentbc5 ordinary first-four-pipe prefix, actual ride adoption and grounding."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import replay_dkjr_public_fourth_carried_bc5_1115 as F
import check_dkjr_public_first_pipe_67_1115 as Cold


def source_controller(raw):
    text = F.controller(raw)
    text = Cold.one(text, "local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''", f'local rom="{F.Prior.PIN}"')
    text = Cold.one(text, "os.getenv('SMB_TEST_VARIANT')=='0'", 'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'") == 2
    text = text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'", 'true')
    text = Cold.one(text, "emu.addEventCallback(guarded('input',function()",
                    "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\n"
                    "emu.addEventCallback(guarded('input',function()")
    return Cold.one(text, ' local player,y=x(),read(0xbd)\n',
                    " local player,y=x(),read(0xbd)\n"
                    " if player>=1020 and y==176 and ram(2,0x6b)==1 and read(0x1e)==0 then\n"
                    "  finish(true,'source-four-pipes-grounded-before-first-gap');return\n end\n")


def main():
    raw = F.Prior.Early.Old.NIGHTLY.read_bytes()
    reference, binding = F.Prior.normalize(raw, kind=F.Prior.KIND)
    text = source_controller(raw)
    opening, memory = Cold.first_active_cold(raw)
    _, payload = F.Prior.Early.Old.identity(reference)
    writers = {0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d6bc0')}
    first_bad = None
    ticks = 0
    def observe(m, cpu):
        nonlocal first_bad
        if cpu.pc in writers and m.rawtags[1] == 3 and cpu.a == 5 and first_bad is None:
            first_bad = dict(PC=cpu.pc, SP=cpu.sp, sourceY=m.ram[2][0x210],
                             origin=m.ram[2][0x76], limit=m.ram[2][0x7b], **Cold.B.state(m))
    def after(m):
        nonlocal ticks
        ticks += 1
        if ticks % 1000 == 0:
            print('DKJR_FOURTH_RIDE_PROGRESS '+json.dumps(dict(tick=ticks, **Cold.B.state(m))), file=output, flush=True)
    output = __import__('sys').stdout
    with redirect_stdout(io.StringIO()):
        result = Cold.B.route(memory, raw, 7000, controller_text=text, observe_extra=observe, after_frame=after)
    receipt = result['receipt'] or {}
    adoptions = [row for row in receipt.get('events', []) if row['event'] == 'fourth-actual-ride-adopted']
    selected = [row for row in receipt.get('events', []) if row.get('pipe') == 4]
    report = dict(passed=result['passed'], input=binding, opening=opening,
                  native_Lua_SHA256=sha256(F.controller(raw).encode()).hexdigest(),
                  source_Lua_SHA256=sha256(text.encode()).hexdigest(), source_updates=result['logical_updates'],
                  reason=receipt.get('reason'), final=result['final'], first_source5_writer=first_bad,
                  actual_fourth_ride_adoptions=adoptions, fourth_events=selected[-8:],
                  crossings=receipt.get('crossings', []), fourth_carries=receipt.get('carries', {}).get('944'),
                  current_game_code_unchanged=True, game_state_seeds=False, output_files=0, native_claim=False)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_PUBLIC_FOURTH_RIDE '+encoded, flush=True)
    print('DKJR_PUBLIC_FOURTH_RIDE_SHA256 '+sha256(encoded.encode()).hexdigest(), flush=True)
    assert result['passed'] and first_bad is None and adoptions
    assert len(receipt.get('crossings', [])) == 4 and result['final']['lives'] == 2


if __name__ == '__main__':
    main()
