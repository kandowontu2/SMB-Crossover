"""Build a private original Rescue Rangers player with uniform score-data addressing and cached pointers.

All original data, including unused songs, remains available through two PRG
tails. The first pure-code page is separately compiled and never read as data.
This avoids guessing which untyped bytes in the source are pointers. This
component does not yet dispatch from gameplay or qualify native performance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
EXPECTED = '6a8b3729742654a5cc59bf2a1be904086fdbbf53d51c3a1b40bf16c387298b3f'
BASE = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT) and not out.exists()
    plan = json.loads((ROOT / 'reference/new-roster-audio/playlist-plan.json').read_text())['chip']
    original = ROOT / plan['source']
    raw = original.read_bytes()
    assert sha(original) == EXPECTED and len(raw) == 12336
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == BASE
    mem = [0] * 65536
    mem[0x8000:0xafb0] = raw[128:]
    cpu = MPU(memory=mem)
    dis = Disassembler(cpu)
    dispatch_calls = {0x8169, 0x82dd, 0x8465, 0x86a1}
    # All four inline dispatch arrays end at actual native instructions.
    tables = [(0x816c, 0x817c), (0x82e0, 0x82ea), (0x8468, 0x849a), (0x86a4, 0x86ae)]
    destinations = sorted({mem[p] + 256 * mem[p + 1]
                           for lo, hi in tables for p in range(lo, hi, 2)})
    dispatch_targets = [mem[p]+256*mem[p+1] for lo,hi in tables for p in range(lo,hi,2)]
    dispatch_bases = {}
    cursor = 0
    for pc,(lo,hi) in zip(sorted(dispatch_calls),tables):
        dispatch_bases[pc] = (cursor-1)&255
        cursor += (hi-lo)//2
    pending = [0x8000, 0xaf99, 0x802c] + destinations
    seen = set()
    while pending:
        pc = pending.pop()
        if pc in seen:
            continue
        assert 0x8000 <= pc < 0x88f4 or 0xaf99 <= pc < 0xafa0, hex(pc)
        op, mode = cpu.disassemble[mem[pc]]
        assert op != '???', hex(pc)
        seen.add(pc)
        size, _ = dis.instruction_at(pc)
        value = mem[pc + 1] + 256 * mem[pc + 2]
        if mode == 'rel':
            pending.append(pc + 2 + (mem[pc + 1] - 256 if mem[pc + 1] >= 128 else mem[pc + 1]))
        if op == 'JSR':
            if value == 0x8023:
                assert pc in dispatch_calls, hex(pc)
                continue  # Real dispatcher consumes its inline-table return.
            pending.append(value)
        if op == 'JMP':
            if mode == 'abs':
                pending.append(value)
            else:
                assert mode == 'ind' and value == 0xc1
            continue
        if op not in ['RTS', 'RTI', 'BRK']:
            pending.append(pc + size)
    observed = json.loads((D / 'root-chip-native-music-source-v1/proof.json').read_text())
    assert set(observed['seen_instructions']) - set(range(0x8023, 0x802c)) <= seen
    instructions = sorted(seen)
    label = lambda pc: f'::ChNativeP{pc:04X}'
    long_branches = set()

    def width(pc):
        op, mode = cpu.disassemble[mem[pc]]
        v = mem[pc+1]
        n = dis.instruction_at(pc)[0] + (mode == 'zpg')
        if mode == 'iny': n = 2 if v in [0xc1,0xc5] else 3
        if mode == 'zpg' and op in ['STA','STX','STY','ASL','LSR','ROL','ROR','INC','DEC']:
            if v == 0xc1: n += 2 if op in ['STA','STX','STY'] else 3
            elif v == 0xc2: n += 3
        return n + (3 if pc in long_branches else 0) + (2 if pc == 0x8674 else 3 if pc == 0x867b else 0)

    for _ in range(30):
        positions, offset = {}, 0
        for pc in instructions:
            positions[pc] = offset
            offset += width(pc)
        add = []
        for pc in instructions:
            if cpu.disassemble[mem[pc]][1] == 'rel':
                to = pc + 2 + (mem[pc + 1] - 256 if mem[pc + 1] >= 128 else mem[pc + 1])
                if pc not in long_branches and not -128 <= positions[to] - positions[pc] - 2 <= 127:
                    add.append(pc)
        if not add:
            break
        long_branches.update(add)
    else:
        raise AssertionError('Relative branch closure did not converge')
    data_address = lambda at: at + 0x2200
    lines = ['; Full original NSF data; separately relocated genuine player.', '.pushseg',
             'ChNativeRam=XgLzHistory', 'ChNativeZp=XgLzHistory+$80',
             'ChNativeTempX=XgLzHistory+$a0', 'ChNativeTempY=XgLzHistory+$a1',
             'ChNativeTempA=XgLzHistory+$a2', 'ChNativeDispatchBase=XgLzHistory+$a3', 'ChNativePointer=XgLzCopy',
             'ChNativeMappedC5=XgLzPosition', 'ChNativeMappedC1=XgLzDistance',
             '.segment "CHIP_NATIVE_CODE"', 'ChNativeStart:',
             '.assert ChNativeStart=$d469,lderror,"Chip code follows relocated genuine Mac records"']
    intercepts = []
    for pc in instructions:
        op, mode = cpu.disassemble[mem[pc]]
        size, text = dis.instruction_at(pc)
        v = mem[pc + 1]
        word = v + 256 * mem[pc + 2]
        lines.append(label(pc) + ':')
        if mode == 'zpg':
            assert 0xc0 <= v <= 0xd8, (hex(pc), hex(v))
            text = f'{op} ::ChNativeZp+${v-0xc0:02x}'
        elif mode == 'iny':
            assert v in [0xc1, 0xc5, 0xd0] and op in ['LDA', 'CMP', 'ORA']
            text = f'{op} (ChNativeMapped{"C1" if v==0xc1 else "C5"}),y' if v in [0xc1,0xc5] else f'jsr ChNative{op}{v:02X}'
            intercepts.append([pc, op, mode, v])
        elif mode == 'rel':
            to = pc + 2 + (v - 256 if v >= 128 else v)
            text = ('j' + op[1:].lower() if pc in long_branches else op) + ' ' + label(to)
        elif mode in ['abs', 'abx', 'aby', 'ind']:
            if op == 'JSR' and word == 0x8023:
                text = f'jsr ChNativeDispatch{pc:04X}'
            elif op in ['JMP', 'JSR']:
                text = 'jmp ChNativeJump' if mode == 'ind' else op + ' ' + label(word)
            elif 0x4000 <= word <= 0x4015 and op in ['STA', 'STX', 'STY']:
                suffix = 'X' if mode == 'abx' else 'Y' if mode == 'aby' else ''
                helper = 'GuestNativeStatusSTA' if word == 0x4015 else f'GuestNativeStore{op}{word-0x4000:02x}{suffix}'
                assert helper + ':' in (ROOT / 'build/generated/guest-audio/writers.inc').read_text() or helper == 'GuestNativeStatusSTA', helper
                text = 'jsr ' + helper
                intercepts.append([pc, op, mode, word])
            else:
                if word >= 0x8000:
                    assert 0x8100 <= word < 0xafb0, ('Pure code page used as data', hex(pc))
                    operand = f'${data_address(word):04x}'
                elif 0x700 <= word < 0x780:
                    operand = f'::ChNativeRam+${word-0x700:02x}'
                else:
                    raise AssertionError(('Unexpected source absolute memory access', hex(pc), text))
                text = op + ' ' + operand + (',x' if mode == 'abx' else ',y' if mode == 'aby' else '')
        else:
            assert mode in ['imm', 'imp', 'acc'], (pc, mode)
        lines.append('  ' + text)
        if mode == 'zpg' and op in ['STA','STX','STY','ASL','LSR','ROL','ROR','INC','DEC']:
            if v == 0xc1:
                lines.append('  '+op+' ChNativeMappedC1' if op in ['STA','STX','STY'] else '  jsr ChNativeSyncC1Low')
            elif v == 0xc2:
                lines.append('  jsr ChNativeMapC1High')
        if pc == 0x8674:
            assert (op,mode,v) == ('STA','zpg',0xc5)
            lines.append('  sta ChNativeMappedC5')
        elif pc == 0x867b:
            assert (op,mode,v) == ('STA','zpg',0xc6)
            lines.append('  jsr ChNativeMapC5High')
    # Preserve ORIGINAL numeric inline-table pointers in the original state.
    # The four real source callsites route to genuine private entries.
    for pc in sorted(dispatch_calls):
        ret = pc + 2
        lines += [f'ChNativeDispatch{pc:04X}:', '  asl', '  tay', '  iny',
                  f'  lda #{dispatch_bases[pc]}', '  sta ChNativeDispatchBase',
                  '  pla', '  pla', f'  lda #${ret>>8:02x}', '  sta ChNativeZp+2', '  jsr ChNativeMapC1High',
                  f'  lda #${ret&255:02x}', '  sta ChNativeZp+1', '  sta ChNativeMappedC1', '  jmp ChNativeP802C']
    lines += ['ChNativeSyncC1Low:', '  php', '  pha', '  lda ChNativeZp+1',
              '  sta ChNativeMappedC1', '  pla', '  plp', '  rts']
    for ptr in [1,5]:
        high=ptr+1
        lines += [f'ChNativeMapC{ptr}High:', '  php', '  pha', f'  lda ChNativeZp+{high}',
                  '  clc', '  adc #$22', f'  sta ChNativeMappedC{ptr}+1', '  pla', '  plp', '  rts']
    lines += ['ChNativeLDAD0:', '  php', '  stx ChNativeTempX', '  ldx #16', '  jmp ChNativeRead']
    lines += ['ChNativeRead:', '  sty ChNativeTempY', '  tya', '  clc',
              '  adc ChNativeZp,x', '  sta ChNativePointer',
              '  lda ChNativeZp+1,x', '  adc #$22', '  sta ChNativePointer+1', '  ldy #0',
              '  lda (ChNativePointer),y', '  ldx ChNativeTempX', '  ldy ChNativeTempY',
              '  plp', '  ora #0', '  rts',
              'ChNativeJump:', '  php', '  pha', '  stx ChNativeTempX',
              '  tya', '  lsr', '  clc', '  adc ChNativeDispatchBase', '  tax',
              '  lda ChNativeTargetLo,x', '  sta ChNativePointer',
              '  lda ChNativeTargetHi,x', '  sta ChNativePointer+1', '  ldx ChNativeTempX',
              '  pla', '  plp', '  jmp (ChNativePointer)',
              'ChNativeSourceInit=ChNativePAF99', 'ChNativeSourcePlay=ChNativeP8000',
              'ChNativeEnd:', '.assert *<=$dfc0,lderror,"Chip code leaves original jump targets and gameplay bridge room"',
              '.segment "CHIP_NATIVE_JUMP_SOURCE"', 'ChNativeTargetLo:',
              ' .byte '+','.join('<'+label(p) for p in dispatch_targets),
              '.assert *<=$a300,lderror,"Chip low jump table exceeds real publisher gap"',
              '.segment "CHIP_NATIVE_JUMP_TARGET"', 'ChNativeTargetHi:',
              ' .byte '+','.join('>'+label(p) for p in dispatch_targets),
              '.assert *<=$dff0,lderror,"Chip genuine target table remains in C94"',
              '.segment "CHIP_NATIVE_DATA_A"', 'ChNativeDataA:',
              f'.incbin "{plan["source"]}",128+$100,$1d00',
              '.segment "CHIP_NATIVE_DATA_C"', 'ChNativeDataC:',
              f'.incbin "{plan["source"]}",128+$1e00,$11b0', '.popseg', '']
    out.mkdir(parents=True)
    stage = out / 'source'
    (stage / 'src').mkdir(parents=True)
    (stage / 'src/chip_native_music.s').write_text('\n'.join(lines))
    entry = (ROOT / 'src/entrypoint.s').read_text()
    entry += '\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "chip_native_music.s"\n.endif\n'
    (stage / 'src/entrypoint.s').write_text(entry)
    cfg = (ROOT / 'smb1base-mmc5-expanded.cfg').read_text()
    cfg = cfg.replace('    LM_GFX:load=X5_NEW_5E,type=ro;\n','')
    cfg = cfg.replace('\n}\nSYMBOLS {', '''
    CHIP_NATIVE_JUMP_SOURCE:load=X5_NEW_3E,type=ro,start=$a2b7;
    CHIP_NATIVE_DATA_A:load=X5_NEW_3E,type=ro,start=$a300;
    CHIP_NATIVE_DATA_C:load=X5_NEW_5E,type=ro,start=$c000;
    LM_GFX:load=X5_NEW_5E,type=ro,start=$d1b0;
    CHIP_NATIVE_CODE:load=X5_NEW_5E,type=ro,start=$d469;
    CHIP_NATIVE_JUMP_TARGET:load=X5_NEW_5E,type=ro;
}
SYMBOLS {''', 1)
    (stage / 'smb1base-mmc5-expanded.cfg').write_text(cfg)
    command = [sys.executable, '-B', str(ROOT / 'tools/build_mmc5_expanded.py'),
               '--source-overlay', str(stage), '--output', str(out / 'candidate.nes')]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (out / 'build.log').write_text(result.stdout + result.stderr)
    (out / 'preparation.json').write_text(json.dumps(dict(
        source_sha256=EXPECTED, baseline_ROM_sha256=BASE,
        original_ROM_data_bytes_preserved=11952, pure_code_page_compiled_separately=[0x8000,0x8100],
        runtime_indirect_data_lower_bound_still_requires_qualification=True, source_indirect_tables=tables,
        source_instruction_count=len(seen), source_jump_targets=destinations,
        expanded_branches=sorted(long_branches), intercepts=intercepts,
        gameplay_dispatch_added=False, native_run=False, accepted=False,
        generator_sha256=sha(__file__)), indent=2)+'\n')
    print(result.stdout + result.stderr)
    assert result.returncode == 0
    print(json.dumps(dict(candidate=str(out/'candidate.nes'), sha256=sha(out/'candidate.nes'),
                          instructions=len(seen), targets=len(destinations), native_run=False)))


if __name__ == '__main__':
    main()
