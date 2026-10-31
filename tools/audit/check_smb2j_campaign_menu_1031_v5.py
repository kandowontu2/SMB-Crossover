"""Check the source-only campaign frontend and unchanged roster consumers."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import bowser_split_loader_controls_v1 as T
import contra_force_menu_admission_controls_1031_v4 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

J = R / 'build/smb2j-cache-loader-source-1031-v3/joint'
P = R / 'build/contra-force-world-chr-publisher-1031-v1/joint'
O = R / 'build/smb2j-campaign-menu-controls-1031-v5'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    O.mkdir()
    q = dict(passed=False, source_CPU=True, native=False, installed=False)
    try:
        stage = json.loads((J.parent / 'source-stage.json').read_text())
        for name, digest in stage['bindings'].items():
            assert sha(name) == digest, name
        old, new = [scoped_load(p / 'candidate.nes') for p in [P, J]]
        seed = T.make(new)
        counters = dict(continue_values=0, reset_values=0, campaign_ready=0,
                        cursor_bounds=0, menu_profiles=0, ready_open=0, pending_decline=0)
        for byte, f in itertools.product([v|high for high in [0,128] for v in range(16)], range(64)):
            m = T.fork(seed)
            T.H.put(m, CrossoverContinue=byte)
            c, low = T.call(m, 'J2ContinueValue', a=77, x=83, y=19, p=T.flags(f))
            expected = byte & 128
            assert (c.a, c.x, c.y, c.sp) == (expected, 83, 19, 224)
            assert c.p == ((T.flags(f) & ~130) | (128 if expected else 2))
            assert T.H.get(m, 'CrossoverContinue') == byte
            counters['continue_values'] += 1
            m = T.fork(seed)
            T.H.put(m, CrossoverContinue=byte, FmAlts=213, FmGroups=189)
            T.call(m, 'J2SelectionReset', p=T.flags(f))
            assert T.H.get(m, 'CrossoverContinue') == (byte & 251 if byte & 4 else byte)
            expected = (213, 189) if byte & 4 else (0, 0)
            assert (T.H.get(m, 'FmAlts'), T.H.get(m, 'FmGroups')) == expected
            counters['reset_values'] += 1
            m = T.fork(seed)
            T.H.put(m, CrossoverContinue=byte)
            c, low = T.call(m, 'J2CampaignReady', p=T.flags(f))
            assert bool(c.p & 1) == (byte & 3 == 0)
            counters['campaign_ready'] += 1
        for choice, offset in itertools.product(range(4), range(85)):
            m = T.fork(seed)
            T.H.put(m, CrossoverContinue=choice | 128, VRAM_Buffer1_Offset=offset)
            at = address(new, 'VRAM_Buffer1')
            original = bytes((i * 13 + 7) & 255 for i in range(90))
            for i, v in enumerate(original):
                m[at + i] = v
            T.call(m, 'J2QueueCursor')
            if offset >= 72:
                assert bytes(m[at:at + 90]) == original
                assert T.H.get(m, 'VRAM_Buffer1_Offset') == offset
            else:
                assert list(m[at + offset:at + offset + 13]) == [33, 100, 1, 253 if choice in [0,3] else 36, 33, 196, 1, 253 if choice==1 else 36, 34, 36, 1, 253 if choice==2 else 36, 0]
                assert T.H.get(m, 'VRAM_Buffer1_Offset') == offset + 12
                assert bytes(m[at:at + offset]) == original[:offset]
                assert bytes(m[at + offset + 13:at + 90]) == original[offset + 13:]
            counters['cursor_bounds'] += 1
        # Exact compiled static commands: all lengths/addresses must remain
        # inside visible nametable rows. Source strings supply their own sizes.
        at = location(new, 'J2BuildMenu::J2TextData')
        texts = []
        while new['raw'][at]:
            high, low, size = new['raw'][at:at + 3]
            addr = high * 256 + low
            assert 0x2000 <= addr < 0x23c0 and (addr & 31) + size <= 32
            texts.append(dict(address=addr, length=size, tiles=list(new['raw'][at + 3:at + 3 + size])))
            at += 3 + size
        assert len(texts) == 6 and texts[1]['length'] == 17 and texts[2]['length'] == 19 and texts[3]['length']==len('ALL NIGHT NIPPON')
        rows = []
        for slot, count in enumerate(M.COUNTS):
            pair = []
            for bundle in [old, new]:
                m = M.C.fresh(bundle, 0)
                M.H.put(m, CrossoverMenuIndex=slot, FfVariant=0, FmAlts=0, CrossoverContinue=0)
                M.C.invoke(m, 'MenuResolveCharacter')
                M.C.invoke(m, 'QueueSelection')
                pair.append(m)
            for variant in range(count):
                if variant:
                    for m in pair:
                        M.H.put(m, CrossoverMenuButtons=0, SavedJoypad1Bits=32, SavedJoypad2Bits=0, VRAM_Buffer1_Offset=0)
                        M.C.invoke(m, 'CrossoverMenuInput')
                outcomes = []
                for m in pair:
                    result = M.C.invoke(m, 'FmPending')['AXYP_SP']
                    outcomes.append(dict(raw=M.H.get(m, 'SelectedCharacter'), name=result[0], pending=result[3] & 1, **M.snapshot(m)))
                assert outcomes[0] == outcomes[1], (slot, variant)
                counters['menu_profiles'] += 1
                m = T.fork(pair[1])
                keep = tuple(M.H.get(m, n) for n in ['SelectedCharacter', 'CrossoverMenuIndex', 'FmAlts', 'FmGroups'])
                M.H.put(m, CrossoverMenuButtons=0, SavedJoypad1Bits=16, SavedJoypad2Bits=0, VRAM_Buffer1_Offset=0)
                result = M.C.invoke(m, 'CrossoverMenuInput')
                assert result['AXYP_SP'][0] == 0
                if outcomes[1]['pending']:
                    assert M.H.get(m, 'CrossoverMenuState') == 2
                    counters['pending_decline'] += 1
                else:
                    assert M.H.get(m, 'CrossoverMenuState') == 9 and M.H.get(m, 'DisableScreenFlag') == 1
                    assert tuple(M.H.get(m, n) for n in ['SelectedCharacter', 'CrossoverMenuIndex', 'FmAlts', 'FmGroups']) == keep
                    counters['ready_open'] += 1
                    # This tests actual button-edge handling through the host
                    # dispatch, then the resume helper; it does not seed a new
                    # character or claim a native screen-rendering replay.
                    M.H.put(m, CrossoverMenuState=10, CrossoverContinue=1,
                            CrossoverMenuButtons=0, SavedJoypad1Bits=64)
                    M.C.invoke(m, 'CrossoverMenuInput')
                    assert M.H.get(m, 'CrossoverMenuState') == 1 and M.H.get(m, 'CrossoverContinue') == 5
                    M.C.invoke(m, 'J2SelectionReset')
                    assert M.H.get(m, 'CrossoverContinue') == 1
                    assert tuple(M.H.get(m, n) for n in ['SelectedCharacter', 'CrossoverMenuIndex', 'FmAlts', 'FmGroups']) == keep
                rows.append(dict(slot=slot, variant=variant, pending=outcomes[1]['pending']))
        assert counters['menu_profiles'] == 86 and counters['ready_open'] == 74 and counters['pending_decline'] == 12
        q.update(passed=True, candidate=sha(J / 'candidate.nes'), parent=sha(P / 'candidate.nes'),
                 counters=counters, text_commands=texts, profiles=rows,
                 no_new_global_or_ZP_bytes=True, old_character_names_art_admission_exact=True,
                 SMB2J_choice_does_not_launch_SMB1=True,
                 limits=['Source CPU component only, no native PPU deadline/menu replay or installation.',
                         'SMB2J/ANN engines and save remain unfinished.2J choice only loads a private data cache; neither new campaign starts gameplay.'])
    except Exception as error:
        q.update(error=repr(error), traceback=traceback.format_exc())
    refs = [Path(__file__), Path(T.__file__), Path(M.__file__), J.parent / 'source-stage.json',
            J / 'candidate.nes', J / 'candidate.dbg', P / 'candidate.nes', P / 'candidate.dbg']
    q['bindings'] = {str(p.resolve()): sha(p) for p in refs}
    (O / 'controls.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in q.items() if k not in ['bindings', 'profiles', 'text_commands', 'traceback']}))
    assert q['passed'], q.get('error')


if __name__ == '__main__':
    main()
