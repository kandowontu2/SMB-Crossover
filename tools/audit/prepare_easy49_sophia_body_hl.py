"""Private source-body correction, based on frozen H; no shared installation."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
D = V / 'root49-sophia-source-body-hl'
P = V / 'agent-lsr-link-firebar-h'
S = D / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(name, old, new):
    p = S / name
    raw = p.read_bytes()
    eol = '\r\n' if b'\r\n' in raw else '\n'
    a, b = (x.replace('\n', eol).encode() for x in (old, new))
    assert raw.count(a) == 1, name
    p.write_bytes(raw.replace(a, b))


def main():
    assert not D.exists()
    frozen = P / 'implementation-freeze.json'
    assert sha(frozen) == 'dbbcc5fb1511dd3595bebb14064c788816d51c26aa5fe4333f081b3a950ac52d'
    catalog = json.loads(frozen.read_text())['source_sha256']
    assert len(catalog) == 443
    for n, h in catalog.items():
        p = P / 'source' / n
        assert sha(p) == h, n
        q = S / n
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
    shutil.copytree(P / 'source/build/generated', S / 'build/generated')
    edit('src/ryu_source_body.s',
         '  lda SelectedCharacter\n  cmp #CHARACTER_RYU\n  bne Done\n  farcall RyuSourceBodyBox',
         '  lda SelectedCharacter\n  cmp #CHARACTER_SOPHIA\n  beq Project\n  cmp #CHARACTER_RYU\n  bne Done\nProject:\n  farcall CrossoverSourceBodyDispatch')
    edit('src/megaman_environment.s',
         '  cmp #CHARACTER_LINK\n  bne FirebarRestore\n  tsx',
         '  cmp #CHARACTER_LINK\n  beq FirebarSource\n  cmp #CHARACTER_SOPHIA\n  bne FirebarRestore\nFirebarSource:\n  tsx')
    edit('src/megaman_environment.s', '  farcall EasyLinkFirebarDisjoint', '  farcall CrossoverSourceFirebarDisjoint')
    edit('src/megaman_environment.s', '  .repeat 8\n    .byte $ea', '  .repeat 4\n    .byte $ea')
    edit('src/megaman_environment.s', '  .repeat 30\n    .byte $ea', '  .repeat 26\n    .byte $ea')
    edit('src/easy_link_firebar.s', '.segment "INVENTORY"', '.segment "SOPHIA_BODY_COLD"')
    edit('smb1base.cfg', '    XG_MUSIC_3A: load=XG_MUSIC_3A_MEM, type=ro, optional=yes;',
         '    XG_MUSIC_3A: load=XG_MUSIC_3A_MEM, type=ro, optional=yes;\n    SOPHIA_BODY_COLD: load=XG_MUSIC_3A_MEM, type=ro, optional=yes;')
    edit('src/entrypoint.s', '.include "easy_link_firebar.s"',
         '.include "easy_link_firebar.s"\n.include "sophia_source_body.s"')
    helper = R / 'tools/audit/templates/sophia_source_body_hl.s'
    shutil.copyfile(helper, S / 'src/sophia_source_body.s')
    driver = (P / 'build-driver.py').read_text()
    assert driver.count(repr(str(P / 'source'))) == 1
    (D / 'build-driver.py').write_text(driver.replace(repr(str(P / 'source')), repr(str(S))))
    names = list(catalog) + ['src/sophia_source_body.s']
    record = dict(status='PRIVATE_BODY_STAGE_PREPARED_NOT_ADMITTED',
        parent_H_freeze_sha256=sha(frozen), source_sha256={n: sha(S / n) for n in names},
        changed=[n for n, h in catalog.items() if sha(S / n) != h],
        new=['src/sophia_source_body.s'], script_sha256=sha(__file__),
        template_sha256=sha(helper), phase_ceiling_bytes=500000000,
        workspace_ceiling_bytes=60000000000,
        scope='Normal flat HRect19x15.5 exact fractional actor projection and native-firebar disjoint consumer. Terrain/head/side sampling and rotated forms remain required subsequent work. No whole-roster or release claim.',
        source_geometry_reference_sha256=sha(V / 'root49-sophia-body-lead-hj.json'),
        runtime_RAM_added=0, main_changed=False)
    (D / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(status=record['status'], sourcefiles=len(names), changed=record['changed'])))


if __name__ == '__main__':
    main()
