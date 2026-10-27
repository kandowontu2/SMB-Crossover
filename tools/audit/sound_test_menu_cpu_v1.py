"""Assembled menu/audio controls; not a native playback or PPU timing verdict."""
from pathlib import Path
import argparse
import hashlib
import json
import traceback

from check_tmnt_render_oa import address
from current3cee_postdma_mask_cpu_v4 import Bus
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from verify_native_relocation import NesMPU

TEMP = ['OperMode', 'SelectedCharacter', 'GamePauseStatus', 'PlayerStatus',
        'Player_State', 'GameEngineSubroutine', 'MmDeathFlag', 'MmChargeFrames']
ROLES = ['OVERWORLD', 'UNDERWATER', 'UNDERGROUND', 'CASTLE', 'SKY BONUS', 'PIPE INTRO',
         'STAR POWER', 'DEATH', 'GAME OVER', 'VICTORY', 'CASTLE CLEAR', 'ALT GAME OVER',
         'LEVEL CLEAR', 'TIME LOW']


def tiles(text):
    return bytes(0x24 if c == ' ' else 0x28 if c == '-' else ord(c)-65+10
                 if 'A' <= c <= 'Z' else int(c) for c in text)


def queue(q):
    data = bytes(q.m[address(q.b, 'VRAM_Buffer1'):address(q.b, 'VRAM_Buffer1')+85])
    count = q.get('VRAM_Buffer1_Offset')
    assert count == 78 and data[count] == 0
    rows = {}
    cursor = 0
    while cursor < count:
        at = data[cursor]*256+data[cursor+1]
        length = data[cursor+2]
        assert 0 < length <= 24 and not length & 0xc0
        rows[at] = data[cursor+3:cursor+3+length]
        cursor += 3+length
    assert cursor == count and len(rows) == 4
    return rows


def nmi(q):
    b = q.b
    q.put(NmiDisable=0, DisableScreenFlag=0, Mirror_PPUCTRL=0xa8,
          Mirror_PPUMASK=30, Sprite0HitDetectFlag=0, ReloadCHRBank=0)
    m = Bus(b, bytes(q.m[:0x8000]), pads=(0, 0))
    for window, bank in enumerate(q.m.banks):
        m.page(window, bank)
    operands = [address(b, n)+1 for n in ['NextBank_SMC', 'SafecallA_SMC',
                'SafereturnA_SMC', 'FarcallJmpTarget_SMC']]+[address(b, 'FarcallJmpTarget_SMC')+2]
    before = ([m[x] for x in operands], m.banks[:], q.get('CurrentBank'),
              q.get('CurrentBankC'), [q.get(n) for n in TEMP])
    cpu = NesMPU(memory=m, pc=0x5b00)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0xa7, 73, 19, 0x71, 0xfd
    m.cpu = cpu
    cpu.nmi()
    minimum = cpu.sp
    for step in range(150000):
        if cpu.pc == 0x5b00 and cpu.sp == 0xfd:
            break
        cpu.step()
        minimum = min(minimum, cpu.sp)
        if m.pending_dma:
            cpu.processorCycles += 513+(cpu.processorCycles & 1)
            m.pending_dma = False
    else:
        raise AssertionError(('complete NMI timeout', hex(cpu.pc), m.banks))
    q.m = m
    after = ([m[x] for x in operands], m.banks[:], q.get('CurrentBank'),
             q.get('CurrentBankC'), [q.get(n) for n in TEMP])
    assert before == after, ('NMI SMC/banks/player flags', before, after)
    assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xcf, cpu.sp) == (0xa7, 73, 19, 0x71 & 0xcf, 0xfd)
    assert minimum >= 128
    return cpu.processorCycles, minimum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    b = scoped_load(args.candidate)
    catalog = json.loads(args.catalog.read_text())['identities']
    assert len(catalog) == 37
    result = dict(passed=False, scope=__doc__, candidate_sha256=hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
                  music_cases=0, sfx_cases=0, complete_nmis=0, minSP=255, max_modeled_nmi_cycles=0)
    try:
        for hero, entry in enumerate(catalog):
            q = Arena(b, entry['owner'])
            q.put(OperMode=0, CrossoverMenuState=8, SoundTestHero=hero, SoundTestKind=0,
                  GamePauseStatus=1, PlayerStatus=2, MmDeathFlag=1, MmChargeFrames=3)
            variant = entry['variant_variable']
            if variant:
                q.set(variant, 0)
            for kind, cues in [(0, ROLES), (1, entry['sfx'])]:
                for index, cue in enumerate(cues):
                    result['current'] = [entry['character'], kind, index]
                    q.put(SoundTestKind=kind, SoundTestIndex=index,
                          CrossoverMenuPressed=128, VRAM_Buffer1_Offset=0)
                    q.invoke('SoundTestInput')
                    assert q.get('SoundTestPlaying') == q.get('SoundTestCommand') == 1
                    if variant:
                        assert q.get(variant) == entry['variant']
                    rows = queue(q)
                    assert rows[0x2145] == tiles(entry['character'].ljust(22))
                    name = cue['name'] if kind else cue
                    assert rows[0x2224] == tiles(name.ljust(24))
                    if kind:
                        assert q.get('SoundTestCueKind') == cue['kind']
                        expected = int(cue['value']) if cue['value'].isdigit() else address(b, cue['value'])
                        assert q.get('SoundTestCueValue') == expected
                    else:
                        assert q.get('SoundTestCueValue') == 1 << (index % 7)
                    for unused in range(2 if not kind and index >= 7 else 1):
                        cycles, minimum = nmi(q)
                        result['complete_nmis'] += 1
                        result['minSP'] = min(result['minSP'], minimum)
                        result['max_modeled_nmi_cycles'] = max(result['max_modeled_nmi_cycles'], cycles)
                    q.put(CrossoverMenuPressed=16, VRAM_Buffer1_Offset=0)
                    q.invoke('SoundTestInput')
                    assert q.get('SoundTestPlaying') == 0
                    if variant:
                        assert q.get(variant) == 0
                    result['sfx_cases' if kind else 'music_cases'] += 1
            q.put(CrossoverMenuPressed=64, VRAM_Buffer1_Offset=0)
            q.invoke('SoundTestInput')
            assert q.get('CrossoverMenuState') == q.get('CrossoverOptionsFocus') == 3
            assert q.get('DisableScreenFlag') == 1 and q.get('SoundTestPlaying') == 0
            print(json.dumps(dict(character=entry['character'], music=result['music_cases'],
                                  sfx=result['sfx_cases'])), flush=True)
        result['passed'] = True
        result.pop('current')
    except Exception:
        result['error'] = traceback.format_exc()
        raise
    finally:
        args.output.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
