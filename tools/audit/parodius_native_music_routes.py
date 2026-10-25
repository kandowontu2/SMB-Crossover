"""Actual compiled current audio routing for all37 playable identities.

CPU-only cold source contexts, both behavior values and every area/event bit.
Dispatch execution is evidence; included data/playlist names alone are not.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from mike_native_music_cpu import Run
from final_item_matrix import ROSTER

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
WATCH = ['AudioUpdate', 'RosterAudioUpdate', 'MegaManAudioUpdate', 'MegaManAudioNativeUpdate',
         'ProtoNativeAudioUpdate', 'SamusAudioUpdate', 'ExpandedAudioUpdate', 'ExpandedAudioTick',
         'VgAudioDispatch', 'GradiusAudioUpdate', 'LmNativeMusicUpdate', 'StNativeMusicUpdate',
         'KbAudioFamily']
PACKED = {6: 'Kid Icarus/Pit', 7: 'Rygar', 9: 'Mega Man10/Bass', 10: 'Ninja Gaiden/Ryu',
          11: 'Blaster Master/Sophia', 12: 'DuckTales/Scrooge', 13: "Kirby's Adventure/Kirby",
          14: "Kirby's Adventure/Meta Knight"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expected-sha256', default='9e0e5ed5d4957aac9baa040ea76616ee4a88233312700b78a8c55250c19f42d3')
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    b = scoped_load(a.rom)
    assert sha(a.rom) == a.expected_sha256
    watch = {name: (address(b, name), location(b, name)) for name in WATCH}
    scenarios = [(role, bit) for role in ['area', 'event'] for bit in range(7)]
    rows = []
    for identity, slot, character, variant, value, family in ROSTER:
        cases = []
        for mode in [0, 1]:
            for role, bit in scenarios:
                r = Run(b)
                for name, v in dict(SelectedCharacter=character, OperMode=1, CrossoverBehaviorVersion=mode,
                                   PlayerStatus=1, DisableScreenFlag=1, CurrentBank=215, CurrentBankC=166,
                                   XgAudioCharacter=255, RgAudioCharacter=255, GuestAudioCharacter=255).items():
                    r.set(name, v)
                if variant: r.set(variant, value)
                r.set('AreaMusicQueue' if role == 'area' else 'EventMusicQueue', 1 << bit)
                events = Counter()
                original = r.c.step

                def step():
                    pc = r.c.pc
                    if pc >= 0x8000:
                        physical = 16 + r.m.banks[(pc - 0x8000) // 8192] * 8192 + (pc & 8191)
                        for name, (target, off) in watch.items():
                            if pc == target and physical == off: events[name] += 1
                    original()

                r.c.step = step
                r.call('AudioUpdate', p=0x24)
                for _ in range(3): r.call('AudioUpdate', p=0x24)
                packed = r.get('XgAudioCharacter') if events['ExpandedAudioTick'] else None
                if character in [0, 8]: source = 'Original SMB audio'
                elif events['ProtoNativeAudioUpdate']: source = 'Original Mega Man3/Proto Man'
                elif events['MegaManAudioNativeUpdate']: source = 'Original Mega Man2/Mega Man'
                elif events['SamusAudioUpdate']: source = 'Original Metroid/Samus'
                elif events['RosterAudioUpdate']: source = {3: 'Original Contra/Bill', 4: 'Original Zelda1/Link', 5: 'Original Castlevania1/Simon'}[character]
                elif events['GradiusAudioUpdate']: source = 'Original Gradius/Vic Viper'
                elif events['LmNativeMusicUpdate']: source = "Original Punch-Out!!/Little Mac"
                elif events['StNativeMusicUpdate']: source = 'Original StarTropics/Mike Jones'
                else:
                    assert packed in PACKED, (identity, packed, events)
                    source = PACKED[packed]
                cases.append(dict(behavior_mode=mode, request_role=role, bit=bit, source_music=source,
                                  packed_family=packed, actual_entries=dict(events),
                                  XgAudioSelection=r.get('XgAudioSelection'), XgAudioEventSelection=r.get('XgAudioEventSelection'),
                                  resulting_banks=list(r.m.banks), final_SP=r.c.sp))
        sources = sorted({v['source_music'] for v in cases})
        row = dict(identity=identity, raw_character=character, variant_symbol=variant, variant=value,
                   source_music=sources, CPU_contexts=len(cases), cases=cases)
        rows.append(row)
        print(identity, sources, flush=True)
    encoding = ROOT / 'reference/new-roster-audio/encoding-report.json'
    report = json.loads(encoding.read_text())
    dependencies = [Path(__file__), ROOT / 'tools/audit/mike_native_music_cpu.py',
                    ROOT / 'tools/audit/final_item_matrix.py', ROOT / 'tools/audit/check_tmnt_render_oa.py',
                    ROOT / 'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
                    ROOT / 'src/music_drivers/audio.s', ROOT / 'src/expanded_audio.s',
                    ROOT / 'src/full_roster_music.inc', ROOT / 'src/expanded_music.inc',
                    ROOT / 'src/gradius_audio.s', ROOT / 'src/mac_native_music.s',
                    ROOT / 'tools/reference/build_new_roster_audio.py', encoding]
    q = dict(passed=True, source_only=True, ROM_sha256=sha(a.rom), identities=len(rows),
             cold_request_contexts=sum(r['CPU_contexts'] for r in rows), AudioUpdate_calls=4 * sum(r['CPU_contexts'] for r in rows),
             rows=rows, actual_compiled_routing=True, full_roster_encoded_roles=report['roles'],
             full_roster_DPCM_writes_not_encoded={k: v['dpcm_writes_not_encoded'] for k, v in report['streams'].items()},
             dependencies={str(f): sha(f) for f in dependencies},
             native_emulator_launched=False, production_changes=False,
             limits='Four actual audio updates per legal cold role/mode/identity context; not full tune/waveform/loop or native timing qualification. A shared source family is named explicitly, not certified authentic for each alternate.')
    (out / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')


if __name__ == '__main__':
    main()
