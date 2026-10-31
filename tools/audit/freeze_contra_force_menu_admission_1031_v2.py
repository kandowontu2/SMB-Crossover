"""Compact source-only CF menu/cold-consumer checkpoint; no Git/native."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

R = Path(__file__).resolve().parents[2]
P = R / 'build/contra-force-menu-admission-1031-v2'
O = R / 'docs/qa/checkpoints/2026-10-31/contra-force-menu-admission-v2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    assert not O.exists()
    O.mkdir()
    stage = json.loads((P / 'source-stage.json').read_text())
    assert stage['candidate'] == 'd3f4386829582d4d7014a4ee0898651136d88723d06f8e6ea814cd79749d757a'
    for name, digest in stage['bindings'].items():
        assert sha(name) == digest, name
    control_paths = [R / 'build/contra-force-menu-admission-controls-1031-v4/controls.json',
                     R / 'build/contra-force-menu-cold-parser-1031-v1/controls.json']
    for path in control_paths:
        doc = json.loads(path.read_text())
        assert doc['passed']
        for name, digest in doc['bindings'].items():
            assert sha(name) == digest, name
    raw = (P / 'joint/main.dep').read_text().split(':\t', 1)[1].splitlines()[0]
    dependencies = [Path(v.replace('\\ ', ' ')).resolve() for v in re.split(r'(?<!\\)[ \t]+', raw.strip()) if v]
    assert len(dependencies) >= 400
    closure = {str(p): sha(p) for p in dependencies}
    put(O / 'actual-main-dependency-closure.json', dict(source_CPU=True, actual_full_dep_file=str(P / 'joint/main.dep'),
         dependency_count=len(dependencies), unique_dependencies=len(closure), bindings=closure))
    scope = dict(status='FROZEN_CF_MENU_GATE_AND_REAL_COLD_SOURCE_CONSUMERS_NATIVE_PENDING',
        source=True, native=False, installed=False, admitted=False,
        parent=stage['parent'], candidate=stage['candidate'], source_menu_ready=74,
        all86_identities_checked=True, previous70_ready_preserved=True,
        actual_Start_masks_cases=10240, actual_classes_cold_Start=4,
        actual_source_gameplay_Main_updates=128, explicit_ready_block_or_Selected_bypass=False,
        actual_body_and_lives_physical_patterns_and_P0=True,
        BT_CF_kernels_cookies_carriers_CHR_shared59_restore67_exact=True,
        code_scope='Three own menu source files only plus their genuine PN JMP QueueVariantHint+3 relocation. Original248B pending andC8C menu spans retained; seven identical20B hints alias one.',
        retained_negatives=[
            'Sourcev1 diff guard omitted actual cross-segment PN operand consumer, one low byte changed BE→C2. V2 binds real JMP operand/target from same character_select.s producer.',
            'Menucontrolv1 demanded all12CHR state bytes equal for newly readyCF. Native prepare legitimately fills unused4..7; V2+ checks actual0..3 sprite consumers and all BG8..11.',
            'Menucontrolv2 demanded bothP0/P1 for everyclass; authenticSmith usesP1-only andBeansP0-only. Exact old/new OAM/patterns and per-class roles retained.',
            'Menucontrolv3 reused older83-entry census omitting2currentSMB3 and1BT. Observed83pairs remain valid; correctedv4 executes actual86 and proves70→74 readiness.',
            'Root BT lives scroll/native timing remains independently open; source menu gate is not publication/native approval.'],
        next='Separate root-approved BT P2 source helper, upcoming BT lives-palette optimization, then root-bound fourCF native firstlooks before installation.')
    put(O / 'scope-and-negatives.json', scope)
    (O / 'README.md').write_text('''# Contra Force menu source admission

This immutable child enables only the four existing CF menu gates, routes their ready previews through the authentic existing helper, drops their four name stars and losslessly aliases identical hints. Every gameplay/cache/CHR byte remains exact to the qualified BT9987 parent. One genuine cross-segment PN pointer follows the relinked hint label.

Actual source controls pass all86 menu identities, old70 ready→74 menu-ready,10240Start masks, and all4 real menu→Start→native cold parser→lives→128total gameplay Main updates. No forced future-ready entry, Selected31 projection or guest RAM preload is used. ROM guard authentication precedes eachA2 entry, and each class loads/constructs once.

Source CPU results are not native or installation approval. Root's BT lives-scroll issue and later bounded fourCF native packets remain outstanding. All fixture/consumer negatives are retained explicitly. source-only.zip omits NES/objects/EXEs/DBG/LBL/carriers and duplicate parent archives. Git staging/commit was not performed.
''', encoding='utf-8')
    tools = [R / 'tools/audit' / n for n in ['prepare_contra_force_menu_admission_1031_v1.py',
        'prepare_contra_force_menu_admission_1031_v2.py', 'contra_force_menu_admission_controls_1031_v1.py',
        'contra_force_menu_admission_controls_1031_v2.py', 'contra_force_menu_admission_controls_1031_v3.py',
        'contra_force_menu_admission_controls_1031_v4.py', 'contra_force_menu_cold_parser_1031_v1.py', Path(__file__).name]]
    allowed = {'.s', '.inc', '.cfg', '.dep', '.json', '.diff'}
    files = set(tools + control_paths)
    files.update(p for p in P.iterdir() if p.is_file() and p.suffix in allowed)
    files.update(p for p in (P / 'joint').rglob('*') if p.is_file() and p.suffix in allowed)
    files.add(R / 'build/contra-force-menu-admission-1031-v1/negative.json')
    for i in [1, 2, 3]:
        files.add(R / ('build/contra-force-menu-admission-controls-1031-v%d/controls.json' % i))
    files.update([O / 'scope-and-negatives.json', O / 'README.md', O / 'actual-main-dependency-closure.json'])
    members = {p.relative_to(R).as_posix(): sha(p) for p in sorted(files)}
    put(O / 'source-members.json', members)
    with zipfile.ZipFile(O / 'source-only.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in members:
            archive.write(R / name, name)
    with zipfile.ZipFile(O / 'source-only.zip') as archive:
        for name, digest in members.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest
    external = [P / 'joint/candidate.nes', P / 'joint/candidate.dbg', P / 'joint/candidate.lbl',
                R / 'docs/qa/checkpoints/2026-10-31/bt-lives-body-source-v1/handoff.json']
    handoff = dict(**scope, archive_members=len(members), archive_bytes=(O / 'source-only.zip').stat().st_size,
        actual_main_recipe=str(P / 'main-build.json'), actual_link_recipe=str(P / 'candidate-link.json'),
        actual_config=str(P / 'joint/candidate.cfg'),
        bindings={str(p): sha(p) for p in files | set(external) | {O / 'source-only.zip', O / 'source-members.json'}})
    put(O / 'handoff.json', handoff)
    owned = tools + [O / n for n in ['README.md', 'scope-and-negatives.json', 'actual-main-dependency-closure.json',
                                    'source-only.zip', 'source-members.json', 'handoff.json', 'owned-files.json']]
    put(O / 'owned-files.json', dict(files=[p.relative_to(R).as_posix() for p in owned], agent_stage_or_commit=False))
    print(json.dumps(dict(path=str(O / 'handoff.json'), sha256=sha(O / 'handoff.json'),
                          members=len(members), bytes=(O / 'source-only.zip').stat().st_size,
                          owned=str(O / 'owned-files.json'))), flush=True)


if __name__ == '__main__':
    main()
