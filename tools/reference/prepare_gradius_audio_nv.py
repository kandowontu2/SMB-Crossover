"""Prepare a relocatable original Gradius music engine from observed provenance.

This writes a review packet outside the workspace. Installation is separate.
Native channel state occupies the otherwise inactive compressed-audio history;
only its indirect pointer pairs and pause input require borrowed CPU zero page.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv')
KEPT = {0xdd, 0xde, 0xf6, 0xf7, 0xfa, 0xfb}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='gradius-relocated-v1')
    args = parser.parse_args()
    coverage = ARCHIVE / 'gradius-native-v2/coverage.json'
    info = json.loads(coverage.read_text())
    raw = (ROOT / info['source']['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == info['source']['source_sha256']
    base = info['load']; body = raw[128:]; end = base + len(body)
    memory = [0] * 65536; memory[base:end] = body
    cpu = MPU(memory=memory); dis = Disassembler(cpu)
    seen = set(info['seen_instructions']); pending = list(seen)
    # Include both sides of source branches, even when the observed song set
    # held a flag constant. Stop at returns and computed dispatches.
    while pending:
        pc = pending.pop(); width, _ = dis.instruction_at(pc)
        op, mode = cpu.disassemble[memory[pc]]
        targets = []
        if mode == 'rel':
            value = memory[pc + 1]
            targets = [pc + width, pc + width + (value - 256 if value >= 128 else value)]
        elif op in ('JMP', 'JSR'):
            if mode == 'abs': targets.append(memory[pc + 1] + 256 * memory[pc + 2])
            if op == 'JSR': targets.append(pc + width)
        elif op not in ('RTS', 'RTI', 'BRK'): targets = [pc + width]
        for target in targets:
            assert base <= target < end, (hex(pc), hex(target))
            if target not in seen: seen.add(target); pending.append(target)
    words = set(info['pointer_words'])
    def label(address):
        assert base <= address < end, hex(address)
        return f'Vg{address:04X}'
    def ram(address):
        return f'$%02x' % address if address in KEPT or not 0xb0 <= address < 256 else f'::VgAudioRam+${address - 0xb0:02x}'
    lines = ['; Original Gradius NSF engine/data, generated from executed operand/pointer provenance.',
             '; Six pointer bytes retain their native zero-page addresses; channel state uses shared history.',
             '.pushseg', '.segment "VIC_NATIVE_AUDIO"', '.scope GradiusMusic']
    moved = 0; apu = []; pc = base
    while pc < end:
        lines.append(label(pc) + ':')
        if pc in seen:
            width, text = dis.instruction_at(pc)
            op, mode = cpu.disassemble[memory[pc]]
            value = memory[(pc + 1) & 65535]
            address = value + 256 * memory[(pc + 2) & 65535]
            for offset in range(1, width): lines.append(f'{label(pc + offset)} = *+{offset}')
            if mode == 'rel':
                target = pc + width + (value - 256 if value >= 128 else value)
                text = 'j' + op[1:].lower() + ' ' + label(target)
            elif mode in ('abs', 'abx', 'aby', 'ind'):
                operand = label(address) if base <= address < end else ram(address)
                text = op + ' ' + ('(' + operand + ')' if mode == 'ind' else
                                    operand + (',x' if mode == 'abx' else ',y' if mode == 'aby' else ''))
                if op == 'STA' and 0x4000 <= address <= 0x400f:
                    suffix = 'X' if mode == 'abx' else 'Y' if mode == 'aby' else ''
                    helper = f'::GuestNativeStoreSTA{address - 0x4000:02x}{suffix}'
                    apu.append(dict(pc=pc, address=address, index=suffix, helper=helper))
                    text = '.if ::VG_RAW_APU\n  ' + text + '\n.else\n  jsr ' + helper + '\n.endif'
            elif mode == 'zpg':
                operand = ram(value); moved += operand.startswith('::')
                text = op + ' ' + operand
            elif mode in ('zpx', 'zpy'):
                accesses = info['accesses'].get(str(pc), [])
                # The source indexes its channel slabs with X=$b0/$c1/$d2/$e3.
                # The retained indirect-pointer addresses are never channel-indexed.
                if accesses:
                    assert all(0xb0 <= a < 256 and a not in KEPT for a in accesses), (hex(pc), accesses)
                operand = f'::VgAudioRam-${0xb0 - value:02x}'
                index = 'x' if mode == 'zpx' else 'y'
                text = op + ' ' + operand + ',' + index; moved += 1
                if op == 'STY' and index == 'x':
                    text = 'php\n  pha\n  tya\n  sta ' + operand + ',x\n  pla\n  plp'
                elif op == 'STX' and index == 'y':
                    text = 'php\n  pha\n  txa\n  sta ' + operand + ',y\n  pla\n  plp'
            lines.append('  ' + text); pc += width
        elif pc in words:
            target = memory[pc] + 256 * memory[pc + 1]
            lines.append(label(pc + 1) + ' = *+1')
            lines.append('  .word ' + label(target)); pc += 2
        else:
            lines.append(f'  .byte ${memory[pc]:02x}'); pc += 1
    lines += ['.endscope', 'GradiusNativeInit = GradiusMusic::VgEC48',
              'GradiusNativePlay = GradiusMusic::VgED30', '.popseg']
    out = ARCHIVE / args.name; out.mkdir(parents=True, exist_ok=False)
    driver = out / 'gradius-native.inc'; driver.write_text('\n'.join(lines) + '\n')
    (out / 'raw-test.s').write_text('.macpack longbranch\nVG_RAW_APU=1\nVgAudioRam=$7000\n'
                                   '.include "gradius-native.inc"\n'
                                   '.export GradiusNativeInit,GradiusNativePlay\n')
    (out / 'raw-test.cfg').write_text('MEMORY { A:start=$a000,size=$2000,file=%O,fill=yes,fillval=$ff; }\n'
                                     'SEGMENTS { VIC_NATIVE_AUDIO:load=A,type=ro; }\n')
    commands = [[str(ROOT / 'tools/Windows/cc65/bin/ca65.exe'), '--cpu', '6502',
                 '-o', str(out / 'raw-test.o'), str(out / 'raw-test.s')],
                [str(ROOT / 'tools/Windows/cc65/bin/ld65.exe'), '-C', str(out / 'raw-test.cfg'),
                 '-Ln', str(out / 'raw-test.lbl'), '-o', str(out / 'raw-test.bin'), str(out / 'raw-test.o')]]
    logs = ''
    for command in commands:
        result = subprocess.run(command, cwd=out, capture_output=True, text=True)
        logs += result.stdout + result.stderr
        (out / 'build.log').write_text(logs)
        assert result.returncode == 0, result.stdout + result.stderr
    report = dict(source=info['source'], coverage_sha256=hashlib.sha256(coverage.read_bytes()).hexdigest(),
                  driver_sha256=hashlib.sha256(driver.read_bytes()).hexdigest(), moved_channel_operands=moved,
                  closed_code_instructions=len(seen), observed_code_instructions=len(info['seen_instructions']),
                  pointer_words=len(words), retained_pointer_zero_page=sorted(KEPT),
                  borrowed_pause_zero_page=0x15, APU_stores=apu,
                  original_payload_bytes=len(body), installed_game_assets_changed=False,
                  raw_test_binary_sha256=hashlib.sha256((out / 'raw-test.bin').read_bytes()).hexdigest())
    (out / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
