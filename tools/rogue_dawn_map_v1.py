"""Bounded read-only Rogue Dawn 1.21 reference extraction; never runs an emulator.

The supplied cartridge is the authority. Original Metroid labels are comparison
anchors only. No complete ROM, patch, audio, CHR, or runtime tree is copied.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROM = Path('C:/NES/the stash/Metroid - Rogue Dawn 1.21 (header fixed).nes')
BASE = Path('C:/NES/Metroid (USA).nes')
ZIP = Path('C:/Users/kando/Downloads/Rogue_Dawn_V121.zip')
EXPECTED = '9271411a20cc26c09f4d4bffe74c0d69a1bf91b815f7716fcf4610c4cee61077'

# Deliberately finite code ranges. Inline dispatch tables are emitted as data.
# DC55/DC6C are BIT instructions whose operands are alternate-entry code;
# emit those alternate entries separately instead of pretending linear decoding
# is a complete control-flow graph.
RANGES = [
    (62, 0xc2be, 0xc2ca, 'shift helpers'),
    (62, 0xc4fa, 0xc508, 'logical 16K area mapping'),
    (62, 0xc716, 0xc71d, 'physical A61 mapping'),
    (62, 0xcc0d, 0xcc22, 'player update and indexed action dispatch'),
    (62, 0xcd40, 0xcd6b, 'running/wall jump continuation'),
    (62, 0xcd9c, 0xcdbf, 'Screw Attack action/pose admission; no morphball shortcut'),
    (62, 0xcf2e, 0xcf55, 'horizontal collision response'),
    (62, 0xcf6b, 0xcf77, 'animation reset'),
    (62, 0xcfc3, 0xd002, 'jump initialization'),
    (62, 0xd002, 0xd055, 'jump update, release cut, aim and fire'),
    (62, 0xd055, 0xd096, 'air horizontal control'),
    (62, 0xd0b5, 0xd0ea, 'unconditional morph; Spring Ball gateway'),
    (62, 0xd0eb, 0xd144, 'unmorph, ball continuation and bomb call'),
    (62, 0xd147, 0xd198, 'stop vertical movement and bomb allocation'),
    (62, 0xd1ee, 0xd2eb, 'beam allocation and horizontal/up fire'),
    (62, 0xd2eb, 0xd3a8, 'projectile initialization, missiles, Wave and Ice'),
    (62, 0xd4bf, 0xd4d3, 'three projectile update owners'),
    (62, 0xd4eb, 0xd58b, 'normal and Wave updates'),
    (62, 0xd5c1, 0xd609, 'Ice dispatch and projectile hit/offscreen handling'),
    (62, 0xd65e, 0xd6a7, 'bomb initialization, fuse and explosion update'),
    (62, 0xd9d4, 0xdac7, 'unmorph/support extension, air morph, wall jump, Wave/Ice and damage extensions'),
    (62, 0xdac7, 0xdb11, 'new projectile terrain handling and banked gateway'),
    (62, 0xdb11, 0xdb70, 'A61 call/return gateways'),
    (62, 0xdc3e, 0xdc73, 'environment-aware gravity/max speed'),
    (62, 0xdc56, 0xdc61, 'alternate entry: ordinary water gravity'),
    (62, 0xdc6d, 0xdc73, 'alternate entry: reduced wall-jump max speed'),
    (62, 0xdd97, 0xddb0, 'missile tank +5 saturating counters'),
    (61, 0xa257, 0xa279, 'gear item special-case and gear read'),
    (61, 0xa2ad, 0xa2ff, 'Spring Ball and A-release cut'),
    (61, 0xa5c4, 0xa70c, 'physical item draw/contact/commit/history'),
    (63, 0xe1cb, 0xe1db, 'Spring Ball banked call owner'),
    (63, 0xe294, 0xe2a9, 'environmental-suit damage admission'),
    (63, 0xe2e8, 0xe31a, 'downward collision: real morph-ball bounce or stop'),
    (63, 0xe37a, 0xe457, 'vertical and horizontal acceleration'),
    (63, 0xe7a2, 0xe7c0, 'up/down tile probes; partial continuation'),
    (63, 0xe880, 0xe8be, 'side tile probes; continuation excluded'),
    (63, 0xf2ca, 0xf2df, 'actual contact gates projectile-to-enemy flags'),
    (63, 0xf579, 0xf5f1, 'enemy weapon damage admission to DA92'),
    (63, 0xffdc, 0xfff0, 'MMC3 bank/shadow write gateway'),
    (2, 0x8296, 0x82a5, 'known physical02 Wave signed vertical decoder'),
    (2, 0x832f, 0x833f, 'known physical02 Wave signed horizontal decoder'),
]
DATA_RANGES = [
    (62, 0xcc22, 0xcc36, 'player action pointers'),
    (62, 0xccc0, 0xccc2, 'ground accelerations right/left'),
    (62, 0xd26f, 0xd275, 'horizontal beam offsets and velocities'),
    (62, 0xd2e5, 0xd2eb, 'upward beam offsets'),
    (62, 0xd33e, 0xd340, 'left/right missile animation IDs'),
    (62, 0xd4d3, 0xd4eb, 'projectile action pointers'),
    (62, 0xd58b, 0xd5c1, 'Wave orientation pointers and wave motion tables'),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def binding(path):
    data = Path(path).read_bytes()
    return {'path': str(Path(path).resolve()), 'bytes': len(data), 'sha256': digest(data)}


def patch_ips(base, patch):
    assert patch[:5] == b'PATCH'
    out = bytearray(base)
    p = 5
    while patch[p:p+3] != b'EOF':
        offset = int.from_bytes(patch[p:p+3], 'big')
        count = int.from_bytes(patch[p+3:p+5], 'big')
        p += 5
        if count:
            data = patch[p:p+count]
            p += count
        else:
            count = int.from_bytes(patch[p:p+2], 'big')
            data = bytes([patch[p+2]]) * count
            p += 3
        if offset + count > len(out):
            out.extend(bytes(offset + count - len(out)))
        out[offset:offset+count] = data
    p += 3
    if len(patch) - p == 3:
        del out[int.from_bytes(patch[p:p+3], 'big'):]
    else:
        assert p == len(patch)
    return bytes(out)


def cpu_image(raw, a_bank=61, lower_bank=0):
    """Explicit MMC3 mode-0 observation image, not automatic bank inference."""
    memory = bytearray(65536)
    for address, bank in [(0x8000, lower_bank), (0xa000, a_bank), (0xc000, 62), (0xe000, 63)]:
        start = 16 + bank * 8192
        memory[address:address+8192] = raw[start:start+8192]
    return memory


def disassemble(raw, bank, start, size):
    from py65.devices.mpu6502 import MPU
    from py65.disassembler import Disassembler
    assert 0 <= bank < 64 and start + size <= (start & 0xe000) + 8192
    m = cpu_image(raw)
    off = 16 + bank * 8192 + (start & 8191)
    m[start:start+size] = raw[off:off+size]
    d = Disassembler(MPU(memory=m))
    lines = []
    pc = start
    while pc < start + size:
        data_range = next((v for v in DATA_RANGES if v[0] == bank and v[1] <= pc < v[2]), None)
        if data_range:
            end = min(data_range[2], start + size)
            lines.append(f'{bank:02X}:{pc:04X}  .byte {m[pc:end].hex(" ").upper()} ; {data_range[3]}')
            pc = end
            continue
        length, instruction = d.instruction_at(pc)
        if pc + length > start + size:
            lines.append(f'{bank:02X}:{pc:04X}  {m[pc:start+size].hex(" ").upper():<8} .byte ; range boundary')
            break
        code = m[pc:pc+length]
        lines.append(f'{bank:02X}:{pc:04X}  {code.hex(" ").upper():<8} {instruction}')
        pc += length
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, default=ROM)
    ap.add_argument('--slice', help='physical PRG bank:CPU address:byte length, all hex')
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    raw = a.rom.read_bytes()
    assert digest(raw) == EXPECTED
    if a.slice:
        bank, start, size = [int(v, 16) for v in a.slice.split(':')]
        print('\n'.join(disassemble(raw, bank, start, size)))
        return
    with zipfile.ZipFile(ZIP) as z:
        ips = z.read('Rogue_Dawn_1.21.ips')
        readme = z.read('Rogue Dawn 1_21 Read Me.txt')
    original = BASE.read_bytes()
    patched = patch_ips(original, ips)
    changes = [{'file_offset': i, 'archive_patch_byte': x, 'supplied_byte': y}
               for i, (x, y) in enumerate(zip(patched, raw)) if x != y]
    assert len(patched) == len(raw) and changes == [dict(file_offset=10, archive_patch_byte=7, supplied_byte=112)]
    assert patched[16:] == raw[16:]
    assert raw[:4] == b'NES\x1a' and raw[4] == 32 and raw[5] == 32
    proof = {
        'scope': __doc__, 'native_run': False,
        'rom': binding(a.rom), 'original_base': binding(BASE), 'distribution_zip': binding(ZIP),
        'readme_archive_member': {'name': 'Rogue Dawn 1_21 Read Me.txt', 'bytes': len(readme), 'sha256': digest(readme)},
        'patch_archive_member': {'name': 'Rogue_Dawn_1.21.ips', 'bytes': len(ips), 'sha256': digest(ips)},
        'patch_provenance': {'payload_exact': True, 'only_header_differences': changes},
        'cartridge': {'header_hex': raw[:16].hex(), 'mapper': 4, 'prg_bytes': 524288, 'chr_bytes': 262144,
                      'physical_prg_banks_8k': 64, 'fixed_c_bank': 62, 'fixed_e_bank': 63,
                      'vectors': dict(nmi=0xcab7, reset=0xffb0, irq=0xcae9)},
        'static_mapping_scope': 'Fixed C/E plus explicitly requested physical A61. Other switchable call targets require actual bank context.',
        'tool': binding(__file__),
    }
    names = ['Bombs', 'High Jump', 'Wall Jump', 'Screw Attack', 'Spring Ball',
             'Environmental Suit', 'Wave Beam', 'Ice Beam']
    proof['gear_items'] = [dict(collector_id=i, mask=f'{1<<i:02X}', name=name,
                                commit='physical61:A667..A66D OR6878',
                                evidence='actual ROM; named Wall/Spring additionally in author1.21 readme')
                           for i,name in enumerate(names)]
    proof['resource_items'] = [
        dict(collector_id=8, name='Energy Tank', routine='physical61:A68D..A6A7',
             effect='TankCount6877 increments unless6; HealthHi0107=(TankCount<<4)|09, HealthLo0106=99'),
        dict(collector_id=9, name='Missile Tank', routine='physical61:A684..A68B -> physical62:DD97',
             effect='current6879 and max687A each+5 saturated255',
             limit='A684 also treats other IDs>=9 this way; valid extra spawn IDs not inferred'),
    ]
    proof['native_player_actions'] = dict(zip(map(str,range(10)),
        ['stand CC36','run/run-jump DA25->CCC2','jump DA0A->D002','morph D0E1',
         'aim-up D198','door D3A8','jump-aim DA72','dead D41A','dead2 D41F','elevator D423']))
    proof['ability_rules'] = [
        dict(name='Morph Ball and Long Beam', status='unconditional native code',
             source=['62:D0B5..D0D8','62:D252..D260','62:D4EB..D51E'],
             rule='No gear10 morph requirement; native long-range checks replaced with constant04. Item bits04/10 are Wall/Spring.'),
        dict(name='Wall Jump', source=['62:DA25..DA6F','63:E880/E88B','62:CD40','62:CFC3'],
             rule='gear04 + freshA + heldhorizontal; the selected side probe must return carryclear, then native jump/max-speed setup.',
             unresolved='Physical probe side/facing and actual dry/wet contact sequence still need original native observation.'),
        dict(name='Spring Ball', source=['63:E1CB..E1DA','61:A2AD..A2FE'],
             rule='freshA; support via frozenenemy7D or blocked-down probe; gear10. Same jump/high-jump environment helper. Releasing A after heldA clips upward VY belowFE toFE.'),
        dict(name='Air morph', source=['62:DA0A..DA3F'],
             rule='freshDown in active jump: Spring bit10 bypasses ground restriction; cooldown2A gates jump action2 path. Action1 path otherwise probes support.'),
        dict(name='Native ball landing bounce', source=['63:E2E8..E318'],
             rule='After actual downward collision, action3 halves VY/fraction then negates pair; impact with shifted VYzero stops. Other actions stop and clear gravity.'),
        dict(name='Bombs', source=['62:D150..D197','62:D65E..D6A6'],
             rule='gear01 + fresh/retriggerB40, no elevator; airborne VY restriction removed. Shared projectile slotsD0/E0/F0, action8->9 fuse12 odd-parity ticks->10 explosion.',
             unresolved='Complete explosion contact/block radius and animation lifetime require source continuation/native observations; no generic bomb damage substitute.'),
        dict(name='Wave plus Ice', source=['62:D359..D3A7','62:D5C1..D5C7','62:DA85..DA91','61:A667..A66D'],
             rule='gear40 and80 coexist; Ice overrides action to3 while keeping Wave metadata; Ice dispatcher uses Wave update when40. Source wave tablesD58B..D5C0.'),
        dict(name='Missiles', source=['62:D315..D358'],
             rule='native mode010E; real ammo debit6879 once per launch; removed D0-only restriction permits available shared3slots. Zero ammo clears missilemode.'),
        dict(name='Screw and Suit', source=['62:CD9C..CDBE','62:CEAC..CEBD','63:E294..E2A8'],
             rule='Screw requires action1 plus authentic pose/motion test; Suit20 halves native BCD damage and changes environmental hazard admission.',
             unresolved='Do not infer immunity to every host hazard or map enemy-type damage without actual source contact.'),
    ]
    proof['runtime_observations_needed'] = [
        'Actual dry and water780E bits; standing/run jump source action, input12/14/16,0310..0316 and per-Main pixel deltas.',
        'WallJumpDA4D, probe E880/E88B and actual carry at returnsDA5F/DA66; held direction/facing before and afterCD40.',
        'Spring entry A61:A2AD with actual support7D/E7AD result and releaseA2DE..A2FE; active bank7 shadow7829.',
        'Physical collection A61:A63F DC7F return/A643 and commitA667; item0748+0/8 and before/after6878/6877..7A.',
        'BombD150 allocation, D65E fuse init, D670 oddclock and D691 explosion; actual enemy contactF2CA and source damageDA92, bounded target/no-target controls.',
        'Earn40/80 in both acquisition orders; horizontal/up beam D359/D38E, actual wave metadata05D0..05F2, ice freeze and cleanup; missile debit/last-ammo/mode reset.',
    ]
    proof['source_search'] = dict(
        author_distribution='local Rogue_Dawn_V121.zip / exact1.21 readme and IPS',
        developer_announcement='https://forum.gamehacking.org/forum/video-game-hacking-and-development/miscellaneous-game-hacking/12411-nes-metroid-1-hack-metroid-rogue-dawn',
        release_thread='https://forum.metroidconstruction.com/index.php?topic=4221.0',
        editor_project='https://github.com/snarfblam/editroid/tree/5d80fcceb1b081cf6428d773652f1f79c488f06d',
        original_metroid='https://github.com/nmikstas/metroid-disassembly/tree/4270d57f9468daebdeea485686e31e26218a780c',
        limit='No complete Rogue gameplay source located in the inspected local distribution or Editroid tree. Original Metroid names are anchors, not Rogue source. Forum access intermittent/403.')
    aliases = {}
    for address,size in [(0x8296,15),(0x832f,16)]:
        sample=raw[16+2*8192+(address&8191):16+2*8192+(address&8191)+size]
        aliases[f'{address:04X}']=dict(bytes=size,sha256=digest(sample),identical_physical_banks=[bank for bank in range(64)
            if raw[16+bank*8192+(address&8191):16+bank*8192+(address&8191)+size]==sample])
    proof['wave_decoder_byte_aliases'] = aliases
    if a.output:
        text_path = a.output.with_suffix('.disassembly.txt')
        lines = ['Rogue Dawn 1.21 finite reference disassembly',
                 'ROM SHA256 '+EXPECTED,
                 'Bank notation is hexadecimal physical 8K PRG bank : CPU address.',
                 'Only fixed C62/E63 and explicitly banked A61 are asserted mappings.',
                 'These are bounded ranges, not a full source recovery. Data/alternate entries are marked.', '']
        spans = []
        for bank, start, end, name in RANGES:
            offset = 16 + bank * 8192 + (start & 8191)
            code = raw[offset:offset+end-start]
            spans.append(dict(bank_decimal=bank, bank_hex=f'{bank:02X}', cpu_start=f'{start:04X}',
                              cpu_end_exclusive=f'{end:04X}', name=name, file_offset=offset,
                              bytes=len(code), sha256=digest(code), type='code range'))
            lines.extend([f'\n; {name}', *disassemble(raw, bank, start, end-start)])
        for bank, start, end, name in DATA_RANGES:
            offset = 16 + bank*8192 + (start & 8191)
            code = raw[offset:offset+end-start]
            spans.append(dict(bank_decimal=bank, bank_hex=f'{bank:02X}', cpu_start=f'{start:04X}',
                              cpu_end_exclusive=f'{end:04X}', name=name, file_offset=offset,
                              bytes=len(code), sha256=digest(code), type='data'))
            lines.extend([f'\n; DATA: {name}', f'{bank:02X}:{start:04X} .byte '+code.hex(' ').upper()])
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text('\n'.join(lines)+'\n', encoding='utf-8')
        proof['bounded_spans'] = spans
        proof['disassembly'] = binding(text_path)
        proof['original_metroid_comparison_anchors'] = [binding(ROOT/'.upstream/metroid/Source_Files'/n)
                                                       for n in ['Bank07.asm', 'Metroid_Defines.asm']]
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    else:
        print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
