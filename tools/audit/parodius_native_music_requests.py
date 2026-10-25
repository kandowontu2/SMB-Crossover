"""Original Parodius request sites/tables; no tune-title inference by order."""
from pathlib import Path
import argparse, hashlib, json
from py65.disassembler import Disassembler
from mike_parodius_rom_probe import RomBus, SOURCE, EXPECTED
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    m = RomBus(SOURCE.read_bytes())
    c = NesMPU(memory=m)
    dis = Disassembler(c)
    lines = []
    for lo, hi in [(0xe200, 0xe2a0), (0xe850, 0xe8c0), (0xdd40, 0xdd80), (0x8001, 0x804a)]:
        lines.append(f'\nSPAN {lo:04X}..{hi:04X}')
        while lo < hi:
            n, text = dis.instruction_at(lo)
            lines.append(f'{lo:04X} {text}')
            lo += n
    (a.output / 'request-control.txt').write_text('\n'.join(lines) + '\n')
    cases = []
    for variant in range(4):
        for stage in range(9):
            for progress in [0, 3, 4, 255]:
                mm = RomBus(SOURCE.read_bytes())
                cpu = NesMPU(memory=mm)
                for at, value in {0x8f: variant, 0x81: stage, 0x60: progress, 0x96: 10}.items():
                    list.__setitem__(mm, at, value)
                cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0xe235, 0x55, 3, 7, 0x24, 0xfd
                trace = []
                for _ in range(100):
                    if cpu.pc == 0xfe20: break
                    trace.append(cpu.pc)
                    cpu.step()
                else: raise AssertionError(('Original stage request failed', variant, stage, progress, hex(cpu.pc)))
                want = m.peek(0xeada + (4 if stage >= 7 else variant)) if progress < 4 else m.peek(0xe937 + stage + 1)
                assert cpu.a == want
                cases.append(dict(original_variant=variant, source_stage_0081=stage,
                                  source_progress_0060=progress, source_selector_0096=10,
                                  actual_FE20_A=cpu.a, resulting_selector_0096=mm.peek(0x96), executed_original_PCs=trace))
    char_cases = []
    for variant in range(4):
        mm = RomBus(SOURCE.read_bytes())
        cpu = NesMPU(memory=mm)
        list.__setitem__(mm, 0x8f, variant)
        cpu.pc, cpu.sp = 0xe276, 0xfd
        for _ in range(8):
            if cpu.pc == 0xfe20: break
            cpu.step()
        assert cpu.pc == 0xfe20
        char_cases.append(dict(original_variant=variant, actual_FE20_A=cpu.a,
                               source_block_start=0xe276, source_FE20_call=0xe27b))
    q = dict(source_sha256=EXPECTED, source_only=True,
             table_EADA=[m.peek(x) for x in range(0xeada, 0xeaea)],
             table_E937=[m.peek(x) for x in range(0xe937, 0xe947)],
             source_FE20_request_wrapper=[m.peek(x) for x in range(0xfe20, 0xfe36)],
             character_selector_address=0x8f,
             character_request_cases=char_cases, stage_request_cases=cases,
             original_basic_block_execution_cases=len(cases) + len(char_cases),
             tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             limits='Original executable basic blocks with explicitly seeded valid selector/character/progress values, stopped at the actual FE20 request entry. This establishes the request inputs/tables, not a complete original gameplay route, tune title or final SMB area adaptation.')
    (a.output / 'tables.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q))


if __name__ == '__main__':
    main()
