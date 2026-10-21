"""Import the user's Metroid PRG audio banks, relocating documented sound RAM.

Operand locations come from nmikstas/metroid-disassembly, not byte-pattern
replacement. The original code, song data and CPU addresses stay intact.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / '.upstream/metroid/Source_Files'

def main():
    rom = Path('C:/NES/Metroid (USA).nes').read_bytes()
    assert rom[:4] == b'NES\x1a' and rom[4] == 8 and not rom[6] & 4
    aliases = {k: int(v, 16) for k, v in re.findall(
        r'^\.alias\s+(\w+)\s+\$([0-9A-Fa-f]+)',
        (SOURCE / 'Metroid_Defines.asm').read_text(), re.M)}
    out = ROOT / 'src/audio/metroid'
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for bank in (0, 1, 2, 4, 5):
        data = rom[16 + bank * 0x4000 + 0x2000:16 + (bank + 1) * 0x4000]
        patches = {}
        source = (SOURCE / f'Bank{bank:02d}.asm').read_text()
        for match in re.finditer(r'^L([A-F0-9]{4}):\s*\*?\s*([A-Z]{3})\s+([^;\n]+)', source, re.M):
            address, opcode, operand = int(match[1], 16), match[2], match[3].strip()
            if not 0xb200 <= address < 0xc000 or operand.startswith('#'):
                continue
            name = operand.split(',')[0].strip()
            target = aliases.get(name)
            if target is None and re.fullmatch(r'\$[0-9A-Fa-f]{4}', name):
                target = int(name[1:], 16)
            if target is not None and 0x600 <= target <= 0x68d:
                pos = address - 0xa000 + 1
                assert int.from_bytes(data[pos:pos+2], 'little') == target, (bank, hex(address), operand)
                patches[pos] = target - 0x600
        lines = [f'.segment "METROID_AUDIO_{bank}"', f'MetroidAudio{bank}:']
        position = 0
        while position < len(data):
            if position in patches:
                lines.append(f'  .word SmAudioRam+${patches[position]:02x}')
                position += 2
            else:
                end = min(position + 16, len(data))
                end = min([end] + [p for p in patches if position < p < end])
                lines.append('  .byte ' + ','.join(f'${v:02x}' for v in data[position:end]))
                position = end
        (out / f'bank{bank}.inc').write_text('\n'.join(lines) + '\n')
        counts[str(bank)] = len(patches)
    commit = subprocess.check_output(['git', '-C', str(SOURCE.parent), 'rev-parse', 'HEAD'], text=True).strip()
    (ROOT / 'docs/reference/samus-audio.json').write_text(json.dumps({
        'source': 'https://github.com/nmikstas/metroid-disassembly', 'commit': commit,
        'rom_sha256': hashlib.sha256(rom).hexdigest(), 'relocated_operands': counts,
        'sound_engine': 'B3B4', 'initialization': 'B404', 'private_ram_bytes': 142,
    }, indent=2) + '\n')
    print('Imported Metroid audio:', counts)

if __name__ == '__main__':
    main()
