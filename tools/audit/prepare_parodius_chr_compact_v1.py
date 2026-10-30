"""Source-link a lossless dense Parodius CHR layout from the frozen v5 parent."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
P = R / 'build/character-host-union-v5'
O = R / 'build/parodius-chr-compact-v1'
sys.path.insert(0, str(R / 'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, s):
    p.write_text(s, newline='\n')


def main():
    assert not O.exists() or '--resume' in sys.argv, O
    parent = P / 'candidate.nes'
    assert sha(parent) == '1a71b8b5a5752aeec7440c4dc2de91a136d6285c98922c99b52f39f4047f2b25'
    handoff = json.loads((P / 'handoff.json').read_text())
    for path, h in handoff['bindings'].items():
        assert sha(path) == h, path
    old = scoped_load(parent)
    raw = old['raw']; chr_start = 16 + 1024 * 1024
    pages = [raw[chr_start + p * 1024:chr_start + (p + 1) * 1024] for p in range(832, 1024)]
    unique = []; aliases = {}
    for p, data in enumerate(pages, 832):
        if data not in unique:
            unique.append(data)
        aliases[p] = 832 + unique.index(data)
    assert len(unique) == 36
    O.mkdir(parents=True, exist_ok='--resume' in sys.argv)
    (O / 'parodius-compact.chr').write_bytes(b''.join(unique))
    for name in ['entrypoint.s']:
        put(O / name, (P / name).read_text())
    # Explicit local include copies prevent accidental selection of canonical
    # Parodius leaves by a caller-relative include search.
    for name in ['vic_viper.s', 'parodius.s', 'parodius_art.inc', 'parodius_death.s']:
        put(O / name, (R / 'src' / name).read_text())
    source = (O / 'parodius.s').read_text()
    assert source.count('.incbin "chr/characters/parodius.chr"') == 1
    put(O / 'parodius.s', source.replace('.incbin "chr/characters/parodius.chr"',
                                        '.incbin "' + (O / 'parodius-compact.chr').as_posix() + '"'))
    changes = []
    art = (O / 'parodius_art.inc').read_text()
    for name in ['PnPoolBodyLo', 'PnPoolSpecialLo', 'PnPoolPickupLo']:
        pos = location(old, name)
        original = raw[pos:pos+18]
        expected = [aliases[v + 768] & 255 for v in original]
        rx = r'(?m)^' + name + r':\s*\.byte[^\r\n]+'
        assert len(re.findall(rx, art)) == 1
        art = re.sub(rx, name + ': .byte ' + ','.join(map(str, expected)), art)
        changes.append(dict(symbol=name, file_offset=pos, before=list(original), after=expected))
    put(O / 'parodius_art.inc', art)
    death = (O / 'parodius_death.s').read_text()
    before = '.byte <892,<956,<1020'
    assert death.count(before) == 1
    expected = [aliases[p] & 255 for p in [892, 956, 1020]]
    put(O / 'parodius_death.s', death.replace(before, '.byte ' + ','.join(map(str, expected))))
    changes.append(dict(symbol='PnDeathGraphics::BodyLo', file_offset=location(old, 'PnDeathGraphics::BodyLo'),
                        before=[124,188,252], after=expected))
    cfg = (P / 'union.cfg').read_text()
    needle = 'PARODIUS_CHR_MEM: start=$d0000,size=$30000,type=ro,fill=yes,file=%O,fillval=$00;'
    assert cfg.count(needle) == 1
    cfg = cfg.replace(needle,
        'PARODIUS_CHR_MEM: start=$d0000,size=$9000,type=ro,fill=yes,file=%O,fillval=$00;\n'
        '    RECLAIMED_PARODIUS_CHR_MEM: start=$d9000,size=$27000,type=ro,fill=yes,file=%O,fillval=$00;')
    put(O / 'compact.cfg', cfg)
    original = json.loads((P / 'build-proof.json').read_text())
    main_cmd = original['commands'][0].copy()
    main_cmd[1:1] = ['-I', str(O)]
    for flag, value in [('--create-full-dep', O / 'main.d'), ('-o', O / 'main.o')]:
        main_cmd[main_cmd.index(flag)+1] = str(value)
    main_cmd[-1] = str(O / 'entrypoint.s')
    link_cmd = original['commands'][-1].copy()
    replacements = {str(P / 'main.o'): str(O / 'main.o'), str(P / 'union.cfg'): str(O / 'compact.cfg')}
    for suffix in ['nes', 'lbl', 'dbg', 'map']:
        replacements[str(P / ('candidate.'+suffix))] = str(O / ('candidate.'+suffix))
    link_cmd = [replacements.get(v, v) for v in link_cmd]
    idx = link_cmd.index('--ld-args') + 1
    link_cmd[idx] = '--dbgfile,' + str(O / 'candidate.dbg')
    commands = []
    for cmd in [main_cmd, link_cmd]:
        result = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
        commands.append(dict(command=cmd, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        put(O / 'compile-log.json', json.dumps(commands, indent=2)+'\n')
        assert result.returncode == 0, result.stderr[:10000]
    sys.path.insert(0, str(R / 'tools'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(R, O / 'candidate.nes')
    dependency_text = (O / 'main.d').read_text().replace('\\ ', ' ').replace('\\', '/')
    for name in ['vic_viper.s', 'parodius.s', 'parodius_art.inc', 'parodius_death.s']:
        assert (O / name).as_posix() in dependency_text, ('Override not compiled', name)
    new = scoped_load(O / 'candidate.nes')
    expected = bytearray(raw)
    for change in changes:
        at = change['file_offset']
        assert list(raw[at:at+len(change['before'])]) == change['before']
        assert location(new, change['symbol']) == at
        expected[at:at+len(change['after'])] = bytes(change['after'])
    expected[chr_start + 832*1024:] = b''.join(unique) + bytes(156*1024)
    assert bytes(expected) == new['raw'], 'Unexpected linked byte change'
    # All linker-visible numeric definitions and locations remain fixed.
    assert set(old['syms']) == set(new['syms'])
    for name, sym in old['syms'].items():
        assert sym['val'] == new['syms'][name]['val'], name
    prg_diff = [i for i, (a,b) in enumerate(zip(raw[:chr_start], new['raw'][:chr_start])) if a != b]
    assert len(prg_diff) <= 57
    proof = dict(status='SOURCE_LINKED_DENSE_CHR_CANDIDATE_CPU_NATIVE_PENDING',
                 parent_sha256=sha(parent), candidate_sha256=sha(O / 'candidate.nes'),
                 parent_handoff_sha256=sha(P / 'handoff.json'),
                 no_RAM_or_runtime_instruction_changes=True, PRG_changed_bytes=len(prg_diff),
                 unchanged_fixed_125_126_127=True,
                 old_pages=[832,1024], compact_pages=[832,868], reclaimed_pages=[868,1024],
                 unique_pages=36, reclaimed_bytes=156*1024,
                 physical_page_aliases=aliases, table_changes=changes, commands=commands,
                 parent_bindings_verified=len(handoff['bindings']),
                 source_bindings={str(p):sha(p) for p in [Path(__file__).resolve(), O / 'entrypoint.s',
                      O / 'vic_viper.s', O / 'parodius.s', O / 'parodius_art.inc', O / 'parodius_death.s',
                      O / 'compact.cfg', O / 'parodius-compact.chr', O / 'main.d']},
                 limits=['Publisher and rendered tile equivalence controls pending',
                         'No shared installation or new allocation from this preparation alone'])
    put(O / 'build-proof.json', json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ['candidate_sha256','PRG_changed_bytes','unique_pages','reclaimed_bytes']}))


if __name__ == '__main__':
    main()
