"""Authenticate original fall semantics and source-test one ordinary departure."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

import replay_dkjr_public_low_depart_67_1115 as F
import check_dkjr_public_first_pipe_67_1115 as Cold

B, N = Cold.B, Cold.N
HASH = lambda value: sha256(value).hexdigest()


def fall_code(raw):
    _, payload = F.Old.identity(raw)
    code = payload[:0x1fe0]
    # Original DA34: upward displacement is safe; delta>=limit is fatal.
    predicate = bytes.fromhex('ad10c2cd76c0900938ed76c0cd7bc0b003a90060a90160')
    at = code.find(predicate)
    assert at == 0x8e1 and code.find(predicate, at+1) == -1
    assert code[0x8db:0x8e1] == bytes.fromhex('a9058d6bc060')
    assert code[0x8ce:0x8d1] == bytes.fromhex('20e1a8')
    memory = [0]*65536
    memory[0xa000:0xa000+len(code)] = code
    decoder = Disassembler(MPU(memory=memory))
    listing = []
    pc = 0xa8ce
    while pc < 0xa8f8:
        size, instruction = decoder.instruction_at(pc)
        listing.append(dict(PC=pc, bytes=bytes(memory[pc:pc+size]).hex(), instruction=instruction))
        pc += size
    origins = [0xa000+i for i in range(len(code)-2) if code[i:i+3] == bytes.fromhex('8d76c0')]
    origin_windows = [dict(PC=pc, preceding_hex=code[pc-0xa000-6:pc-0xa000+3].hex()) for pc in origins]
    assert len(origins) == 3
    # These are the two original fall-entry writers and original jump's writer.
    assert all(code[pc-0xa000-3:pc-0xa000] in (bytes.fromhex('ad10c2'), bytes.fromhex('8d01c0')) for pc in origins)
    return dict(original_DA34_PC=0xa8e1, original_DA31_PC=0xa8dd,
                landing_listing=listing, original_origin_writers=origin_windows,
                observed_native_sourceY=159, observed_native_origin=101,
                observed_native_limit=24, calculated_drop=58, original_fatal_branch=True,
                native_receipt='3b87a46813d934605ff0db14c84a86afcc22bcad3a7724774f1be4c8173007f7')


def source_text(raw):
    text = F.controller(raw)
    text = Cold.one(text, "local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''", f'local rom="{F.Old.PIN}"')
    text = Cold.one(text, "os.getenv('SMB_TEST_VARIANT')=='0'", 'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'") == 2
    text = text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'", 'true')
    text = Cold.one(text, "emu.addEventCallback(guarded('input',function()",
                    "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\n"
                    "emu.addEventCallback(guarded('input',function()")
    # Component endpoint only; native factory keeps its original full route.
    return Cold.one(text, ' local player,y=x(),read(0xbd)\n',
                    " local player,y=x(),read(0xbd)\n"
                    " if player>=510 then finish(true,'source-first-pipe-component-clear');return end\n")


def main():
    raw = F.Old.NIGHTLY.read_bytes()
    semantics = fall_code(raw)
    print('DKJR_PUBLIC_FALL_CODE '+json.dumps(semantics, separators=(',', ':')), flush=True)
    opening, memory = Cold.first_active_cold(raw)
    text = source_text(raw)
    first_bad = None
    ticks = 0
    _, payload = F.Old.identity(raw)
    writers = {0xa000+i for i in range(0x1fde) if payload[i:i+3] == bytes.fromhex('8d6bc0')}
    def observe(m, cpu):
        nonlocal first_bad
        if cpu.pc in writers and m.rawtags[1] == 3 and cpu.a == 5 and first_bad is None:
            first_bad = dict(PC=cpu.pc, A=cpu.a, sourceY=m.ram[2][0x210],
                             origin=m.ram[2][0x76], limit=m.ram[2][0x7b], **B.state(m))
    def after(m):
        nonlocal ticks
        ticks += 1
        if ticks % 500 == 0:
            print('DKJR_LOW_DEPART_PROGRESS '+json.dumps(dict(tick=ticks, **B.state(m))), file=output, flush=True)
    output = __import__('sys').stdout
    with redirect_stdout(io.StringIO()):
        result = B.route(memory, raw, 2800, controller_text=text, observe_extra=observe, after_frame=after)
    receipt = result['receipt'] or {}
    departures = [row for row in receipt.get('events', []) if row['event'] == 'pipe1-low-depart']
    report = dict(passed=result['passed'], current_ROM_SHA256=F.Old.PIN,
                  native_controller_Lua_SHA256=HASH(F.controller(raw).encode()),
                  source_component_Lua_SHA256=HASH(text.encode()), first_source5_writer=first_bad,
                  departure=departures, source_updates=result['logical_updates'], final=result['final'],
                  reason=receipt.get('reason'), opening=opening,
                  only_first_pipe_controls_changed=True, game_code_changed=False,
                  native_claim=False, output_files=0)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_PUBLIC_LOW_DEPART '+encoded, flush=True)
    print('DKJR_PUBLIC_LOW_DEPART_SHA256 '+HASH(encoded.encode()), flush=True)
    assert result['passed'] and first_bad is None and len(departures) == 1
    assert result['final']['x'] >= 510 and result['final']['lives'] == 2


if __name__ == '__main__':
    main()
