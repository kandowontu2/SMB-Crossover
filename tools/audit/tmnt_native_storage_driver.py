"""Compile original TMNT source with optional exact arithmetic/storage changes.

Standalone source experiment only. It consumes no game bank/reservation and
keeps the accepted Parodius checkpoint and production source untouched.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from py65.disassembler import Disassembler
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
OB = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')
CURRENT = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
ORIGINAL = 'f220e8d069e321f392526d41e46f5d0f72966d5a22e56d2b269607c678bd58d9'
MOVED = (0x9f29, 0xa09a, 0xa429)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def source_data():
    q = json.loads((OB / 'probe-v2/coverage.json').read_text())
    raw = Path(q['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ORIGINAL
    m = [0] * 65536
    m[0x8000:0x8000 + len(raw) - 128] = raw[128:]
    c = NesMPU(memory=m)
    d = Disassembler(c)
    seen, pending = set(q['seen_instructions']), list(q['seen_instructions'])
    while pending:
        pc = pending.pop()
        width, _ = d.instruction_at(pc)
        op, mode = c.disassemble[m[pc]]
        assert op != '???'
        targets = []
        if mode == 'rel':
            v = m[pc + 1]
            targets = [pc + width, pc + width + (v - 256 if v >= 128 else v)]
        elif op in ['JMP', 'JSR']:
            if mode == 'abs': targets.append(m[pc + 1] + 256 * m[pc + 2])
            if op == 'JSR': targets.append(pc + width)
        elif op not in ['RTS', 'RTI', 'BRK']:
            targets = [pc + width]
        for target in targets:
            assert 0x8612 <= target < 0xc018, (hex(pc), hex(target))
            if target not in seen:
                seen.add(target)
                pending.append(target)
    assert len(seen) == 1289
    assert not any(MOVED[0] <= pc < MOVED[1] for pc in seen)
    words = set(q['pointer_words']) | {0x9014}
    assert len(words) == 369 and m[0x9014] + 256 * m[0x9015] == 0x918b
    assert m[MOVED[0] - 1] == m[MOVED[1] - 1] == 0xff
    return q, m, c, d, seen, words


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--duration', action='store_true')
    p.add_argument('--swap', action='store_true')
    p.add_argument('--parent', type=Path, default=ROOT / 'build/smb-crossover-mmc5-expanded.nes')
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    assert sha(a.parent) == CURRENT
    q, m, c, d, seen, words = source_data()
    native_move = lambda at: at + 0x2000 if at < 0xc000 else at - 0x2000

    def move(at):
        if a.swap and MOVED[0] <= at < MOVED[1]:
            return MOVED[2] + at - MOVED[0]
        assert 0x8612 <= at < 0xc02c, hex(at)
        return native_move(at)

    lines = ['; Pinned original TMNT source; generated source/storage experiment.',
             '.pushseg', '.segment "TMNT_NATIVE_AUDIO_PREFIX"', 'TnNativeImageStart:']
    apu, operands = [], []

    def region(start, end):
        pc = start
        while pc < end:
            if a.duration and pc == 0x8c7c:
                assert bytes(m[pc:pc + 10]) == bytes.fromhex('187d1001c6e2d0f8f003')
                lines.extend(['  .assert *=$ac7c,lderror,"Original duration entry"',
                              '  jsr TnFastDuration', '  jmp $ac89', '  .res 4,$ea'])
                pc += 10
            elif pc in seen:
                width, text = d.instruction_at(pc)
                op, mode = c.disassemble[m[pc]]
                if mode in ['abs', 'abx', 'aby', 'ind']:
                    at = m[pc + 1] + 256 * m[pc + 2]
                    suffix = ',x' if mode == 'abx' else ',y' if mode == 'aby' else ''
                    operand = (f'${move(at):04x}' if at >= 0x8000 else
                               f'::TnAudioRam+${at - 0x100:02x}' if 0x100 <= at <= 0x1ad else
                               f'::TnAudioZp+${at - 0xe0:02x}' if 0xe0 <= at <= 0xed else f'${at:04x}')
                    text = op + ' ' + ('(' + operand + ')' if mode == 'ind' else operand + suffix)
                    if op in ['STA', 'STX', 'STY'] and 0x4000 <= at <= 0x4017:
                        helper = 'TnSource' + op + f'{at - 0x4000:02X}' + ('X' if mode == 'abx' else 'Y' if mode == 'aby' else '')
                        apu.append(dict(pc=pc, operation=op, mode=mode, address=at, helper=helper))
                        text = '.if ::TN_RAW_APU\n  ' + text + '\n.else\n  jsr ::' + helper + '\n.endif'
                    if 0x100 <= at <= 0x1ad or at >= 0x8000:
                        operands.append(dict(pc=pc, address=at, new=move(at) if at >= 0x8000 else None))
                elif mode in ['zpg', 'zpx', 'zpy', 'inx', 'iny']:
                    at = m[pc + 1]
                    if 0xe0 <= at <= 0xed:
                        operand = f'::TnAudioZp+${at - 0xe0:02x}'
                        text = op + ' ' + ('(' + operand + '),y' if mode == 'iny' else '(' + operand + ',x)' if mode == 'inx' else operand + (',x' if mode == 'zpx' else ',y' if mode == 'zpy' else ''))
                elif mode == 'rel':
                    value = m[pc + 1]
                    target = pc + width + (value - 256 if value >= 128 else value)
                    assert move(target) - move(pc) == target - pc
                    text = f'.byte ${m[pc]:02x},${value:02x} ; {op} source${target:04x}'
                lines.append(f'  .assert *=${native_move(pc):04x},lderror,"Original instruction offset {pc:04x}"')
                lines.append('  ' + text)
                pc += width
            elif pc in words:
                target = m[pc] + 256 * m[pc + 1]
                lines.append(f'  .word ${move(target):04x} ; source pointer${pc:04x}')
                pc += 2
            else:
                values = [m[pc]]
                pc += 1
                while pc < end and pc not in seen and pc not in words and len(values) < 24:
                    values.append(m[pc])
                    pc += 1
                lines.append('  .byte ' + ','.join(f'${v:02x}' for v in values))

    region(0xc000, 0xc02c)
    lines.append('  .assert *=$a02c,lderror,"Unchanged source bootstrap"')
    if a.duration:
        lines += ['.segment "TMNT_DURATION_HELPER"', '.proc TnFastDuration',
                  ' lda z:TnAudioZp+2', ' asl', ' asl', ' asl', ' asl',
                  ' ora TnAudioRam+$10,x', ' tax', ' lda TnDurationProducts,x',
                  ' ldx #1', ' stx z:TnAudioZp+2', ' ldx TnAudioRam+$92',
                  ' clc', ' adc TnAudioRam+$10,x', ' dec z:TnAudioZp+2', ' rts',
                  '.endproc', '.assert TnFastDuration=$a200,lderror,"Duration helper reserve"',
                  '.segment "TMNT_DURATION_TABLE"', 'TnDurationProducts:']
        for n in range(16):
            lines.append(' .byte ' + ','.join(str(n * base) for base in range(16)))
        lines.append('.assert TnDurationProducts=$a300,lderror,"Duration table reserve"')
    if a.swap:
        lines += ['.segment "TMNT_MOVED_SOURCE"', 'TnMovedStreamBegin:']
        region(MOVED[0], MOVED[1])
        lines += ['TnMovedStreamEnd:', '.assert TnMovedStreamBegin=$a429,lderror,"Page-aligned source stream"',
                  '.assert TnMovedStreamEnd=$a59a,lderror,"Complete connected source interval"']
    lines += ['.segment "TMNT_NATIVE_AUDIO_A"', 'TnNativeSourceBegin:']
    region(0x8612, 0xa000)
    lines += ['  .assert *=$c000,lderror,"Native A footprint"']
    if a.swap:
        lines += ['.segment "TMNT_MENU_UI_PREFIX"', '  .incbin "bank99-prefix.bin"',
                  '.segment "TMNT_NATIVE_AUDIO_B"']
        region(0xa08a, 0xc000)
    else:
        lines.append('.segment "TMNT_NATIVE_AUDIO_B"')
        region(0xa000, 0xc000)
    lines += ['.assert *=$e000,lderror,"Native B footprint"',
              'TnNativeInit=$a000', 'TnNativePlay=$a644', 'TnNativeCommand=$b057',
              '.export TnNativeInit,TnNativePlay,TnNativeCommand', '.popseg']
    driver = out / 'tmnt-native.inc'
    driver.write_text('\n'.join(lines) + '\n')
    parent = a.parent.read_bytes()
    prefix = parent[16 + 99 * 8192:16 + 99 * 8192 + 138]
    (out / 'bank99-prefix.bin').write_bytes(prefix)
    (out / 'raw-test.s').write_text('TN_RAW_APU=1\nTnAudioRam=$7000\nTnAudioZp=$e0\n.include "tmnt-native.inc"\n')
    memory = [
        'P:start=$a000,size=$2c,file=%O,fill=yes,fillval=$ff;',
        'W:start=$a02c,size=$1d4,file=%O,fill=yes,fillval=$ff;',
        'H:start=$a200,size=$100,file=%O,fill=yes,fillval=$ff;',
        'L:start=$a300,size=$100,file=%O,fill=yes,fillval=$ff;',
        'MP:start=$a400,size=$29,file=%O,fill=yes,fillval=$ff;',
        'M:start=$a429,size=$1e9,file=%O,fill=yes,fillval=$ff;',
        'A:start=$a612,size=$19ee,file=%O,fill=yes,fillval=$ff;',
    ]
    segments = ['TMNT_NATIVE_AUDIO_PREFIX:load=P,type=ro;', 'TMNT_NATIVE_AUDIO_A:load=A,type=ro;',
                'TMNT_DURATION_HELPER:load=H,type=ro,optional=yes;', 'TMNT_DURATION_TABLE:load=L,type=ro,optional=yes;',
                'TMNT_MOVED_SOURCE:load=M,type=ro,optional=yes;']
    if a.swap:
        memory += ['U:start=$c000,size=$8a,file=%O,fill=yes,fillval=$ff;',
                   'B:start=$c08a,size=$1f76,file=%O,fill=yes,fillval=$ff;']
        segments.append('TMNT_MENU_UI_PREFIX:load=U,type=ro;')
    else:
        memory.append('B:start=$c000,size=$2000,file=%O,fill=yes,fillval=$ff;')
    segments.append('TMNT_NATIVE_AUDIO_B:load=B,type=ro;')
    (out / 'raw-test.cfg').write_text('MEMORY {\n' + '\n'.join(memory) + '\n}\nSEGMENTS {\n' + '\n'.join(segments) + '\n}\n')
    commands = [
        [str(ROOT / 'tools/Windows/cc65/bin/ca65.exe'), '--cpu', '6502', '-o', 'raw-test.o', 'raw-test.s'],
        [str(ROOT / 'tools/Windows/cc65/bin/ld65.exe'), '-C', 'raw-test.cfg', '-Ln', 'raw-test.lbl', '-o', 'raw-test.bin', 'raw-test.o'],
    ]
    for cmd in commands:
        r = subprocess.run(cmd, cwd=out, capture_output=True, text=True)
        (out / ('assemble.log' if 'ca65' in cmd[0] else 'link.log')).write_text(r.stdout + r.stderr)
        assert r.returncode == 0, (r.stdout + r.stderr)[-3000:]
    assert (out / 'raw-test.bin').stat().st_size == 16384
    result = dict(passed=True, source_only=True, production_changes=False, native_run=False,
                  parent_ROM_sha256=CURRENT, original_NSF_sha256=ORIGINAL,
                  duration_optimization=a.duration, bank99_storage_swap=a.swap,
                  moved_source_interval=list(MOVED) if a.swap else None,
                  moved_source_bytes=MOVED[1] - MOVED[0] if a.swap else 0,
                  page_aligned_native_pointer_delta=-0x1b00 if a.swap else 0,
                  original_closed_instructions=len(seen), all_original_pointer_words=sorted(words),
                  original_source_code_unmoved=True,
                  APU_stores=apu, relocated_operands=operands,
                  source_RAM_relocation_base=0x7000, source_ZP_base=0xe0,
                  raw_binary_sha256=sha(out / 'raw-test.bin'), driver_sha256=sha(driver),
                  parent_bank99_UI_prefix_sha256=hashlib.sha256(prefix).hexdigest(),
                  tool_sha256=sha(Path(__file__)),
                  scope='Reproducible standalone assembly only. Current game integration, complete dynamic closure, original goldens/state/ABI and native timing are not established by generation.')
    (out / 'preparation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'duration_optimization', 'bank99_storage_swap', 'moved_source_bytes', 'raw_binary_sha256']}))


if __name__ == '__main__':
    main()
