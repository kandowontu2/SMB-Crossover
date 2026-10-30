"""Source-compose qualified dense PN and Ice aliases onto the exact V13 union."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
P = R/'build/character-host-union-v13'
O = R/'build/character-host-union-resources-v1'
PN = R/'build/parodius-chr-compact-v1'
IC = R/'build/ice-pose-aliases-v2'
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
from prepare_cv3_dmc_mirror import prepare


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, text):
    path.write_text(text, newline='\n')


def main():
    assert not O.exists(), 'Keep rejected preparations; use a successor directory.'
    packet = P/'handoff.json'
    assert sha(packet) == 'dae38b677133adddaf0d6a07b9debf38077098696f536410728d9f519956489b'
    h = json.loads(packet.read_text())
    bindings = dict(h['bindings'])
    for path, digest in bindings.items():
        assert sha(path) == digest, path
    assert sha(P/'candidate.nes') == h['candidate_sha256']
    original = scoped_load(P/'candidate.nes')
    recipe = json.loads((P/'build-proof.json').read_text())['commands']
    assert recipe[0][-1] == str(P/'entrypoint.s')
    assert recipe[0][recipe[0].index('-o')+1] == str(P/'main.o')
    assert recipe[-1].count(str(P/'main.o')) == 1
    assert recipe[-1].count(str(P/'union.cfg')) == 1
    O.mkdir()

    def build(folder, entry, config, overrides):
        folder.mkdir()
        put(folder/'entrypoint.s', entry)
        put(folder/'private.cfg', config)
        for name, raw in overrides.items():
            (folder/name).write_bytes(raw)
        assembler = recipe[0].copy()
        assembler[1:1] = ['-I', str(folder)]
        assembler[assembler.index('-o')+1] = str(folder/'main.o')
        assembler[assembler.index('--create-full-dep')+1] = str(folder/'main.d')
        assembler[-1] = str(folder/'entrypoint.s')
        replacements = {str(P/'main.o'): str(folder/'main.o'), str(P/'union.cfg'): str(folder/'private.cfg')}
        for ext in ['nes', 'dbg', 'lbl', 'map']:
            replacements[str(P/('candidate.'+ext))] = str(folder/('candidate.'+ext))
        linker = [replacements.get(token, token) for token in recipe[-1]]
        idx = linker.index('--ld-args')+1
        assert linker[idx] == '--dbgfile,'+str(P/'candidate.dbg')
        linker[idx] = '--dbgfile,'+str(folder/'candidate.dbg')
        commands = []
        for command in [assembler, linker]:
            result = subprocess.run(command, cwd=R, capture_output=True, text=True)
            commands.append(dict(command=command, returncode=result.returncode,
                                 stdout=result.stdout, stderr=result.stderr))
            put(folder/'compile-log.json', json.dumps(commands, indent=2)+'\n')
            assert result.returncode == 0, result.stderr[-12000:]
        prepare(R, folder/'candidate.nes')
        dep = (folder/'main.d').read_text().replace('\\ ', ' ').replace('\\', '/')
        for name in overrides:
            if Path(name).suffix in ['.s', '.inc']:
                assert (folder/name).as_posix() in dep, ('Override not compiled', name)
        for path in folder.iterdir():
            if path.is_file():
                bindings[str(path)] = sha(path)
        return scoped_load(folder/'candidate.nes'), commands

    entry = (P/'entrypoint.s').read_text()
    cfg = (P/'union.cfg').read_text()
    repro, _ = build(O/'reproduce', entry, cfg, {})
    assert repro['raw'] == original['raw'], 'Exact V13 source reproduction required'
    # Reuse only the frozen, already source/native-qualified producers.
    pn_proof = json.loads((PN/'build-proof.json').read_text())
    for path, digest in pn_proof['source_bindings'].items():
        assert sha(path) == digest, path
        bindings[path] = digest
    overrides = {name: (PN/name).read_bytes() for name in
                 ['vic_viper.s', 'parodius.s', 'parodius_art.inc', 'parodius_death.s']}
    needle = 'PARODIUS_CHR_MEM: start=$d0000,size=$30000,type=ro,fill=yes,file=%O,fillval=$00;'
    assert cfg.count(needle) == 1
    cfg = cfg.replace(needle,
        'PARODIUS_CHR_MEM: start=$d0000,size=$9000,type=ro,fill=yes,file=%O,fillval=$00;\n'
        '    RECLAIMED_PARODIUS_CHR_MEM: start=$d9000,size=$27000,type=ro,fill=yes,file=%O,fillval=$00;')
    dense, commands = build(O/'pn', entry, cfg, overrides)
    expected = bytearray(original['raw'])
    for change in pn_proof['table_changes']:
        at = location(original, change['symbol'])
        assert at == location(dense, change['symbol'])
        assert list(expected[at:at+len(change['before'])]) == change['before']
        expected[at:at+len(change['after'])] = bytes(change['after'])
    chr_start = 1048592
    expected[chr_start+832*1024:] = (PN/'candidate.nes').read_bytes()[chr_start+832*1024:]
    assert bytes(expected) == dense['raw'], 'PN stage may change only the exact54data bytes and dense CHR'
    assert set(original['syms']) == set(dense['syms'])
    assert all(sym['val'] == dense['syms'][name]['val'] for name, sym in original['syms'].items())
    pn_output = dict(parent_sha256=h['candidate_sha256'], candidate_sha256=sha(O/'pn/candidate.nes'),
                     physical_page_aliases=pn_proof['physical_page_aliases'], commands=commands,
                     source_bindings=dict(bindings), exact_parent_reproduction=True,
                     no_runtime_instruction_or_RAM_changes=True)
    put(O/'pn/build-proof.json', json.dumps(pn_output, indent=2)+'\n')
    ic_proof = json.loads((IC/'build-proof.json').read_text())
    for path, digest in ic_proof['source_bindings'].items():
        assert sha(path) == digest, path
        bindings[path] = digest
    overrides.update({name: (IC/name).read_bytes() for name in ['ice_climbers.s', 'ice_climbers_art.inc']})
    aliased, commands = build(O/'ice', entry, cfg, overrides)
    first, end = 16+70*8192+0x380, 16+70*8192+0x860
    qualified_parent = (PN/'candidate.nes').read_bytes()
    assert dense['raw'][first:end] == qualified_parent[first:end]
    expected = bytearray(dense['raw'])
    expected[first:end] = (IC/'candidate.nes').read_bytes()[first:end]
    assert bytes(expected) == aliased['raw'], 'Ice stage changes only qualified descriptor bytes'
    assert aliased['raw'][16+70*8192+0x58f:end] == bytes([255])*721
    assert set(dense['syms']) == set(aliased['syms'])
    for name, sym in dense['syms'].items():
        if name == 'IcArtEnd' or re.fullmatch(r'IcPose\d+', name):
            continue
        assert sym['val'] == aliased['syms'][name]['val'], name
    paths = [Path(__file__).resolve(), packet, P/'build-proof.json', PN/'build-proof.json', IC/'build-proof.json',
             O/'pn/build-proof.json']
    bindings.update({str(path): sha(path) for path in paths})
    proof = dict(passed=True, source_only=True, native=False, parent_ROM_sha256=sha(O/'pn/candidate.nes'),
                 ROM_sha256=sha(O/'ice/candidate.nes'), original_V13_sha256=h['candidate_sha256'],
                 saved_PRG_bytes=721, dense_CHR_pages=[832, 868], unused_CHR_pages=[868, 1024],
                 all_runtime_instructions_unchanged=True, all_RAM_addresses_unchanged=True,
                 all_other_symbol_values_exact=True, aliases=ic_proof['aliases'],
                 source_bindings=bindings, commands=commands,
                 limits=['Exact source composition only. Adapted CPU renderer controls and native comparison remain required.',
                         'No new character behavior/admission flags or shared download changed.'])
    put(O/'ice/build-proof.json', json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(passed=True, PN=pn_output['candidate_sha256'], Ice=proof['ROM_sha256'],
                         reclaimed_CHR_bytes=159744, reclaimed_PRG_bytes=721)))


if __name__ == '__main__':
    main()
