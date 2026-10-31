"""Rebase only frozen Benj v5 producers onto the current installed62 source.

Private stage: no menu admission or installation. Keeps FF/S2 lives fixes.
"""
from pathlib import Path
import difflib
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load, address, location

P = R / 'build/coherent62-lives-fixes-v1'
V = R / 'build/benj-mario-native-host-v5'
O = R / 'build/benj-current-host-1030-v5'
J = O / 'joint'


def once(t, a, b):
    assert t.count(a) == 1, (a, t.count(a))
    return t.replace(a, b)


def main():
    assert not O.exists()
    assert B.sha(P / 'handoff.json') == 'fae1ec38db9525a645a8907fd92608978de15f0f7cf4b12088cee0e0f0393a1c'
    assert B.sha(V / 'handoff.json') == '894a0b1f6b9c49cfc896b9eee7a341af520ec54755510d7beb1e4d6d45c07334'
    for p in [P / 'handoff.json', V / 'handoff.json']:
        B.bound(json.loads(B.read(p)))
    shutil.copytree(P / 'joint', J)
    def retarget(s):
        return s.replace(str(P / 'joint'), str(J)).replace((P / 'joint').as_posix(), J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s', '.inc', '.cfg']:
            B.write(p, retarget(B.read(p)))
    patch = []
    def change(p, s):
        old = B.read(p)
        B.write(p, s)
        patch.extend(difflib.unified_diff(old.splitlines(True), s.splitlines(True),
                     fromfile='installed62/' + p.relative_to(J).as_posix(),
                     tofile='benj-current/' + p.relative_to(J).as_posix()))

    old_base = R / 'build/celeste-menu-name-current-v2/joint'
    # These are the frozen v5 leaf's ONLY differences in the three source
    # producers. Apply exact original fragments to current, not whole old files.
    for name in ['player.s', 'collision.s', 'kamikaze_mario_render_v2.inc']:
        old, new = B.read(old_base / 'src' / name), B.read(V / 'src' / name)
        import difflib as D
        current = B.read(J / 'src' / name)
        edits = []
        ol, nl = old.splitlines(True), new.splitlines(True)
        for group in D.SequenceMatcher(None, ol, nl, autojunk=False).get_grouped_opcodes(3):
            # Merge adjacent edits before applying their shared context. The
            # two earlier private attempts stopped before compiling: v1 had
            # an unanchored insertion; v2 reused overlapping context.
            before = ''.join(ol[group[0][1]:group[-1][2]])
            after = ''.join(nl[group[0][3]:group[-1][4]])
            edits.append((before, after))
        for before, after in edits:
            current = once(current, before, after)
        change(J / 'src' / name, current)
    for name in ['benj_graphics.s', 'peach_float_core.s', 'BmReset.s', 'BmFloatReset.s',
                 'BmFresh.s', 'BmEnsure.s', 'BmHeadClassify.s', 'native-pose-map.bin',
                 'toad-visible-pairs.bin', 'peach-visible-pairs.bin', 'optimized-descriptors.json', 'pose-proof.json']:
        shutil.copyfile(V / name, J / name)
    change(J / 'src/kamikaze_mario_source_art_v2.inc', '.include "benj_graphics.s"\n')
    for p in [J / 'src/new_roster_dispatch.s', J / 'union.s']:
        s = B.read(p)
        assert '<CmHostFresh' in s and '>CmHostFresh' in s and '.bank(CmHostFresh)' in s
        change(p, s.replace('<CmHostFresh', '<BmFresh').replace('>CmHostFresh', '>BmFresh')
                   .replace('.bank(CmHostFresh)', '.bank(BmFresh)'))
    change(J / 'entrypoint.s', B.read(J / 'entrypoint.s') + '\n.export BmFresh\n')
    change(J / 'union_imports.inc', B.read(J / 'union_imports.inc') + '\n.import BmFresh\n')
    cfg = once(B.read(J / 'private.cfg'), '    PARODIUS_CHR:load=PARODIUS_CHR_MEM,type=ro;',
        '    PARODIUS_CHR:load=PARODIUS_CHR_MEM,type=ro;\n    BENJ_MARIO_CHR:load=UNALLOCATED_CHR_MEM,type=ro,start=$e1400;')
    change(J / 'private.cfg', cfg)
    art = R / 'build/benj-mario-source-art-1030-v1'
    B.write(J / 'benj-chr.s', '.segment "BENJ_MARIO_CHR"\n' + ''.join(
        '.incbin "' + (art / (n + '-source-52-pose.chr')).as_posix() + '"\n' for n in ['toad', 'peach']))
    recipes = []
    for label, log, source in [
        ('main-build', R / 'build/arthur-goku-select-remap-v3/main-build.json', 'entrypoint.s'),
        ('union-build', R / 'build/functional-roster-smb2-v1/union-build.json', 'union.s')]:
        c = json.loads(B.read(log))['command'][:]
        c[1:1] = ['-I', str(J / 'src'), '-I', str(J), '--bin-include-dir', str(J)]
        for flag in ['-o', '--create-full-dep', '--create-dep']:
            if flag in c:
                c[c.index(flag) + 1] = str(J / Path(c[c.index(flag) + 1]).name)
        c[-1] = str(J / source)
        recipes.append((label, c))
    recipes.append(('chr-build', [str(R / 'tools/Windows/cc65/bin/ca65.exe'), '-g', '-o', str(J / 'benj-chr.o'), str(J / 'benj-chr.s')]))
    link = json.loads(B.read(P / 'final-link.json'))['command'][:]
    for i, token in enumerate(link):
        if token.endswith('.o') and Path(token).name in ['main.o', 'consumer-18.o']:
            link[i] = str(J / Path(token).name)
    for flag in ['-o', '-Ln', '-m', '--dbgfile', '--mapfile', '-C']:
        if flag in link:
            link[link.index(flag) + 1] = str(J / Path(link[link.index(flag) + 1]).name)
    k = link.index('--ld-args') + 1
    parts = link[k].split(',')
    for i in range(1, len(parts), 2):
        parts[i] = str(J / Path(parts[i]).name)
    link[k] = ','.join(parts)
    link.append(str(J / 'benj-chr.o'))
    recipes.append(('final-link', link))
    B.write(O / 'output-preflight.json', json.dumps([dict(step=n, validation=validate(c, J, cwd=R)) for n, c in recipes], indent=2) + '\n')
    for n, c in recipes:
        validate(c, J, cwd=R)
        z = subprocess.run(c, cwd=R, text=True, capture_output=True)
        B.write(O / (n + '.json'), json.dumps(dict(command=c, returncode=z.returncode, stdout=z.stdout, stderr=z.stderr), indent=2) + '\n')
        assert z.returncode == 0, (n, z.stderr)
    from prepare_cv3_dmc_mirror import prepare
    prepare(R, J / 'candidate.nes')
    old, v5, base, out = [load(p / 'candidate.nes') for p in [old_base, V, P / 'joint', J]]
    expected = bytearray(base['raw'])
    points = [i for i, (a, b) in enumerate(zip(old['raw'], v5['raw'])) if a != b]
    old_fresh = {location(old, n) + 15 for n in ['HuLo', 'HuHi', 'HuBank']}
    new_fresh = [location(base, n) + 15 for n in ['HuLo', 'HuHi', 'HuBank']]
    assert old_fresh == {0x9f89e, 0x9f92e, 0x9f9be}
    for i in points:
        if i in old_fresh:
            continue
        assert expected[i] == old['raw'][i], ('Leaf conflicts with current source', hex(i))
        expected[i] = v5['raw'][i]
    # The current union's table moved14B. Rebind the genuine defaultFresh15
    # consumer, never transplant the old absolute tuple over current graphics1.
    target = address(out, 'BmFresh')
    for i, value in zip(new_fresh, [target & 255, target >> 8, 62 | 128]):
        expected[i] = value
    assert out['raw'] == bytes(expected), 'Rebased source differs from leaf plus genuine relocated Fresh15 tuple'
    for n in ['KmGraphics', 'KmSelect', 'KmPortrait', 'KmCoreEnd']:
        assert address(base, n) == address(out, n)
    for n in ['code.bin', 'data.bin', 'ram3.bin', 'ff-cookie.bin']:
        assert B.sha(J / n) == B.sha(P / 'joint' / n)
    B.write(O / 'source.patch', ''.join(patch))
    d = dict(status='PRIVATE_CURRENT62_BENJ_V5_EXACT_LEAF_REBASE_UNEXPOSED', source=True,
        candidate=B.sha(J / 'candidate.nes'), joint=str(J), parent=B.sha(P / 'joint/candidate.nes'),
        native=False, installed=False, ready=62, changed_bytes=len(points), exact_leaf_composition=True,
        preserved_FF_SMB2_lives_and_remap=True, bindings={str(p): B.sha(p) for p in [
            Path(__file__), P / 'handoff.json', V / 'handoff.json', J / 'candidate.nes', J / 'candidate.dbg',
            J / 'candidate.lbl', O / 'source.patch', O / 'output-preflight.json']})
    B.write(O / 'source-stage.json', json.dumps(d, indent=2) + '\n')
    print(json.dumps({k: v for k, v in d.items() if k != 'bindings'}, indent=2))


if __name__ == '__main__':
    main()
