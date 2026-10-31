"""Prepare the granted CF P1 graft on a frozen current M3/BT source cart.

Preparation is the default: it writes sources, isolated commands and a recipe,
but invokes no compiler/linker. --execute is for the root-approved successor.
The actual parent's main/menu/M3 objects are never rebuilt or overwritten.
"""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address, location
from prepare_cv3_dmc_mirror import prepare as cv3_mirror

K = R / 'build/contra-force-p1-kernel-v1'
OLD = R / 'build/contra-force-p1-cart-v2'
GRANTS = R / 'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources'
PINS = {
    K / 'build-proof.json': '8b927877185cf50770593ce5f50c2f2823bd290d9eced40dc4fdf6fc1ff37bb6',
    OLD / 'source-stage.json': 'aab3adc044e80ae2f043a6f2cfce98ec5ac1ae860331d5f698e47ed810c2a629',
    GRANTS / 'root-review-and-reservations.json': '4dc474df018af488a3464e31a2ab1261c99ba3b07870fc402b0e40957a9dba90',
    GRANTS / 'native-first-amendment-v2.json': '5e706c5a0be059aa6769ebdf9f5345f66a73f8a9018912c91d0cc0c0fca875af',
    GRANTS / 'native-restore-factor-grant-v1.json': '4a6bf61cd52a84a40bd59ee383449a7ae2d4809268fb5e90464246185ec18809',
    GRANTS / 'native-restore-source-amendment-v2.json': '5ea941acc823c1a90e1b9d172494f95fdf0107f3aa025d2b8ee7e9f7da586fec',
    R / 'docs/qa/checkpoints/2026-10-31/m3-current-cfbt-source-v1/handoff.json': 'd81119a76567e7d150bd3ff4d3d79c73b7abfa7feefeb58730c4aaf7cb9df9d4',
    R / 'tools/reference/contra_force_p1_native_restore_proposal_v2.s': 'a75ec54c06142d0619af5dced2e0b6351375f65c0566d3feb24613725d8e5a25',
    R / 'tools/reference/contra_force_p1_shared_factor_proposal_v3.s': '47a4f10e07b6bec51687e788880933586666170956f7ea7f3e5c25c0e9e32b7f',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def write(path, value):
    Path(path).write_text(value, encoding='utf-8', newline='\n')


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


def bound(path):
    doc = json.loads(Path(path).read_text())
    for name, digest in doc.get('bindings', {}).items():
        assert sha(name) == digest, ('Frozen binding mismatch', name, digest, sha(name))
    return doc


def native_abi(bundle):
    """Validate every absolute original native import before payload reuse."""
    rows = []
    source = (K / 'native-imports.s').read_text()
    for name, value in re.findall(r'^([A-Za-z0-9_]+)=\$([0-9a-fA-F]+)$', source, re.M):
        expected = int(value, 16)
        if name == 'CfNativeResetBank':
            sym = bundle['syms']['JnResetDispatch']
            seg = bundle['segs'][sym['seg']]
            actual = (int(seg['ooffs'], 0) - 16) // 8192 | 128
        else:
            actual = address(bundle, name)
        assert actual == expected, ('Source kernel native ABI changed', name, expected, actual)
        rows.append(dict(name=name, expected=expected, actual=actual))
    assert len(rows) == 108
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-joint', type=Path, required=True)
    ap.add_argument('--parent-handoff', type=Path, required=True)
    ap.add_argument('--link-recipe', type=Path, required=True)
    ap.add_argument('--expected-parent-sha256', required=True)
    ap.add_argument('--output-root', type=Path, required=True)
    ap.add_argument('--execute', action='store_true')
    args = ap.parse_args()
    parent = args.parent_joint.resolve()
    out = args.output_root.resolve()
    assert out.is_relative_to(R / 'build') and not out.exists(), out
    joint = out / 'joint'
    joint.mkdir(parents=True)
    try:
        for path, digest in PINS.items():
            assert sha(path) == digest, ('Pinned prerequisite changed', str(path), digest, sha(path))
        bound(args.parent_handoff)
        bound(K / 'build-proof.json')
        bound(OLD / 'source-stage.json')
        for name in ['root-review-and-reservations.json', 'native-first-amendment-v2.json',
                     'native-restore-factor-grant-v1.json', 'native-restore-source-amendment-v2.json']:
            bound(GRANTS / name)
        assert sha(parent / 'candidate.nes') == args.expected_parent_sha256
        old = qualified(parent / 'candidate.nes')
        imports = native_abi(old)
        gap = 16 + 91 * 8192 + 0xe97
        assert old['raw'][gap:gap + 67] == bytes([234]) * 67, 'M3 source factor/split prerequisite absent'
        assert [address(old, name) for name in ['__M3_GFX_LOAD__', '__M3_GFX_RUN__', '__M3_GFX_SIZE__']] == [0xc000, 0xc000, 0x13fd]

        recipe = json.loads(args.link_recipe.read_text())['command']
        objects = [Path(v).resolve() for v in recipe if Path(v).suffix.lower() == '.o']
        assert len(objects) == len(set(objects)) and len(objects) >= 80
        by_name = {}
        for obj in objects:
            by_name.setdefault(obj.name, []).append(obj)

        def one(name):
            values = by_name.get(name, [])
            assert len(values) == 1, (name, values)
            return values[0]

        chosen = {name: one(name + '.o') for name in ['cf-loader', 'cf-guard', 'cf-carrier', 'cf-retire',
                                                        'ff-palette', 'ff-palette-lifecycle']}
        loaders = [obj for obj in by_name.get('loader.o', [])
                   if '.import FwPaletteMapC' in obj.with_suffix('.s').read_text()]
        assert len(loaders) == 1, loaders
        chosen['loader'] = loaders[0]
        source_inputs = {str(obj.with_suffix('.s')): sha(obj.with_suffix('.s')) for obj in chosen.values()}
        frozen_inputs = {str(p): sha(p) for p in [parent / 'candidate.nes', parent / 'candidate.dbg',
                         parent / 'candidate.lbl', parent / 'private.cfg', args.parent_handoff,
                         args.link_recipe, *objects]}

        # Do not guess what the current recipe consumes from copied source trees.
        save(out / 'parent-object-inputs.json', dict(objects=frozen_inputs, actual_sources=source_inputs,
                                                     no_main_or_menu_recompile=True))
        save(out / 'native-abi.json', dict(passed=True, count=len(imports), imports=imports))
        cfg_text = (parent / 'private.cfg').read_text()
        assert re.search(r'CF_P1_RESTORE_ROM_MEM\s*:\s*start=\$ae97,\s*size=\$43', cfg_text, re.I)
        assert 'CF_P1_ROM_RESTORE_PROPOSAL:' not in cfg_text
        assert 'M3_GFX_PREFIX:load=X5_NEW_5B' in cfg_text
        assert 'RODATA:load=X5_NEW_5B_AFTER_CF' in cfg_text

        def config(name, worker):
            text = cfg_text
            serial = 0

            def redirect(match):
                nonlocal serial
                if match[1] in ['', '%O']:
                    return match[0]
                dest = joint / 'sideoutputs' / name / ('%03d-' % serial + Path(match[1]).name)
                serial += 1
                dest.parent.mkdir(parents=True, exist_ok=True)
                return 'file="' + dest.as_posix() + '"'

            text = re.sub(r'file\s*=\s*"([^"]*)"', redirect, text)
            if worker:
                text = once(text, 'SEGMENTS {', 'SEGMENTS {\n    CF_P1_ROM_RESTORE_PROPOSAL:load=CF_P1_RESTORE_ROM_MEM,type=ro;')
            dest = joint / (name + '.cfg')
            write(dest, text)
            return dest

        # Produce the exact frozen source-built kernel; no cartridge byte patch.
        images = []
        for bank in [1, 2, 3]:
            image = bytearray((K / ('ram%d.bin' % bank)).read_bytes())
            image.extend([0] * (8192 - len(image)))
            assert len(image) == 8192
            if bank in [2, 3]:
                image[0x1fe0:] = bytes(32)
            (joint / ('cf-ram%d.bin' % bank)).write_bytes(image)
            images.append(image)
        payload = b''.join(images)
        cookie = bytes([167, 31, 0, 2]) + hashlib.sha256(payload).digest()[:12]
        assert payload == (OLD / 'joint/cf-stream.bin').read_bytes()
        assert cookie == (OLD / 'joint/cf-cookie.bin').read_bytes()
        (joint / 'cf-stream.bin').write_bytes(payload)
        (joint / 'cf-cookie.bin').write_bytes(cookie)

        diffs = []

        def changed(name, text):
            src = chosen[name].with_suffix('.s')
            write(joint / (name + '.s'), text)
            diffs.extend(difflib.unified_diff(src.read_text().splitlines(True), text.splitlines(True),
                                            fromfile=str(src), tofile=str(joint / (name + '.s'))))

        for name in ['cf-loader', 'cf-guard', 'cf-retire']:
            text = chosen[name].with_suffix('.s').read_text()
            text = re.sub(r'\.incbin\s+"[^"]*cf-cookie\.bin"',
                          lambda m: '.incbin "' + (joint / 'cf-cookie.bin').as_posix() + '"', text)
            changed(name, text)
        text = chosen['cf-carrier'].with_suffix('.s').read_text()
        text, count = re.subn(r'\.incbin\s+"[^"]*cf-stream\.bin"',
                             lambda m: '.incbin "' + (joint / 'cf-stream.bin').as_posix() + '"', text)
        assert count == 1
        changed('cf-carrier', text)

        loader_dir = chosen['loader'].parent
        changed('loader', chosen['loader'].with_suffix('.s').read_text())
        (joint / 'ff-cookie.bin').write_bytes((loader_dir / 'ff-cookie.bin').read_bytes())
        epoch = (loader_dir / 'ff-epoch-rom.inc').read_text()
        epoch = once(epoch, 'FfMuxRomNative:\n pla\n plp\n sta SafecallA_SMC+1',
                     'FfMuxRomNative:\n pla\n plp\n.export FfMuxNativeTail\nFfMuxNativeTail:\n sta SafecallA_SMC+1')
        write(joint / 'ff-epoch-rom.inc', epoch)
        source_inputs[str(loader_dir / 'ff-epoch-rom.inc')] = sha(loader_dir / 'ff-epoch-rom.inc')
        source_inputs[str(loader_dir / 'ff-cookie.bin')] = sha(loader_dir / 'ff-cookie.bin')

        shared = (R / 'tools/reference/contra_force_p1_shared_factor_proposal_v3.s').read_text()
        shared_body = shared.split('CfSharedDrawSelect:\n', 1)[1].split('CfSharedDrawSelectEnd:', 1)[0]
        shared_body = once(shared_body, 'lda #<(BtServiceVeneers+18)', 'lda #<CfP1NativeRestore')
        shared_body = once(shared_body, 'lda #>(BtServiceVeneers+18)', 'lda #>CfP1NativeRestore')
        shared_body = once(shared_body, '.bank(BtServiceVeneers)', '.bank(CfP1NativeRestore)')
        palette = chosen['ff-palette'].with_suffix('.s').read_text()
        palette = once(palette, '.import FfMuxNativeROM', '.import FfMuxNativeROM,FfMuxNativeTail,CfP1NativeRestore')
        palette, count = re.subn(r'\.proc FwNativeDrawAll\n[\s\S]*?\.endproc',
                                lambda m: '.proc FwNativeDrawAll\n' + shared_body +
                                '.assert *-FwNativeDrawAll=59,error,"Approved native-first CF late59"\n.endproc',
                                palette, count=1)
        assert count == 1
        changed('ff-palette', palette)

        life = chosen['ff-palette-lifecycle'].with_suffix('.s').read_text()
        life = once(life, ' MP_FAR MoveAllSpritesOffscreen,jsr\n ldx SmFreezePaletteControl',
                    ' MP_FAR MoveAllSpritesOffscreen,jsr\n.export FwMuxNativeSelect\nFwMuxNativeSelect:\n ldx SmFreezePaletteControl')
        changed('ff-palette-lifecycle', life)
        restore = (R / 'tools/reference/contra_force_p1_native_restore_proposal_v2.s').read_text()
        restore += '\n.assert CfP1NativeRestore=$ae97,lderror,"Exact granted A91 restore start"\n'
        restore += '.assert CfP1NativeRestoreEnd=$aeda,lderror,"Exact granted67B restore end"\n'
        restore += '.assert .bank(CfP1NativeRestore)=$5b,lderror,"Genuine physical91 A-view worker"\n'
        write(joint / 'cf-p1-native-restore.s', restore)
        write(out / 'source.diff', ''.join(diffs))

        commands = []
        baseline_cfg = config('baseline', False)
        final_cfg = config('candidate', True)

        def link_command(name, cfg, remap, extra):
            command = [str(v) for v in recipe]
            for flag, value in [('-C', cfg), ('-Ln', joint / (name + '.lbl')),
                                ('-o', joint / (name + '.nes'))]:
                assert command.count(flag) == 1, flag
                command[command.index(flag) + 1] = str(value)
            if '-m' in command:
                command[command.index('-m') + 1] = str(joint / (name + '.map'))
            else:
                command.extend(['-m', str(joint / (name + '.map'))])
            assert command.count('--ld-args') == 1
            assert command[command.index('--ld-args') + 1].startswith('--dbgfile,')
            command[command.index('--ld-args') + 1] = '--dbgfile,' + str(joint / (name + '.dbg'))
            command = [remap.get(str(Path(v).resolve()), v) if Path(v).suffix == '.o' else v for v in command]
            command.extend(extra)
            return command

        commands.append(dict(name='baseline-link', command=link_command('baseline', baseline_cfg, {}, [])))
        remap = {}
        for name in [*chosen, 'cf-p1-native-restore']:
            command = [str(R / 'tools/Windows/cc65/bin/ca65.exe'), '--cpu', '6502x', '-g',
                       '-I', str(joint), '-I', str(loader_dir), '-I', str(R),
                       '--create-full-dep', str(joint / (name + '.dep')),
                       '-o', str(joint / (name + '.o')), str(joint / (name + '.s'))]
            commands.append(dict(name=name + '-build', command=command))
            if name in chosen:
                remap[str(chosen[name])] = str(joint / (name + '.o'))
        commands.append(dict(name='candidate-link', command=link_command('candidate', final_cfg, remap,
                                                                         [str(joint / 'cf-p1-native-restore.o')])))
        for row in commands:
            row['output_guard'] = validate(row['command'], out, cwd=R)
        save(out / 'prepared-commands.json', commands)
        plan = dict(status='PREPARED_ONLY_NO_COMPILER_OR_LINKER_INVOKED', source=True,
                    native=False, ready=False, admitted=False, installed=False,
                    parent=args.expected_parent_sha256, actual_parent_joint=str(parent),
                    required_root_BT_child_before_execute=True, main_menu_M3_objects_unchanged=True,
                    worker_placement=dict(physical=91, run=0xae97, end=0xaeda, bytes=67),
                    shared_span=[0xb3c5, 0xb400], cookie=cookie.hex(),
                    source_input_inventory=source_inputs, actual_objects={str(p): sha(p) for p in objects},
                    qualified_kernel=str(K / 'build-proof.json'), native_imports_checked=len(imports),
                    no_new_PRG_RAM_CHR_OAM=True,
                    allowed_ROM_changes=['existing shared59', 'granted physical91 worker67',
                                         'two existing16B CF cookies', 'existing24KB carrier935..<959'],
                    still_required=['Actual linked finite paired OAM/pixels/normalPPU/queue/lifecycle and real ISR controls',
                                    'Current68/BT/Samus/FF actual source regressions',
                                    'Root-reviewed native/controller/menu readiness, no native grant here'],
                    bindings={str(p): h for p, h in PINS.items()})
        plan['bindings'].update({str(Path(__file__).resolve()): sha(__file__),
                                 str(args.parent_handoff.resolve()): sha(args.parent_handoff),
                                 str(args.link_recipe.resolve()): sha(args.link_recipe),
                                 **frozen_inputs, **source_inputs})
        plan['bindings'].update({str(p): sha(p) for p in out.rglob('*') if p.is_file()})
        save(out / 'prepared.json', plan)
        if not args.execute:
            print(json.dumps(dict(prepared=str(out / 'prepared.json'), sha256=sha(out / 'prepared.json'),
                                  compiler_invocations=0, linker_invocations=0)))
            return

        # Every command is guarded again immediately before execution.
        logs = []
        for row in commands:
            guard = validate(row['command'], out, cwd=R)
            run = subprocess.run(row['command'], cwd=R, capture_output=True, text=True)
            log = dict(**row, immediate_output_guard=guard, returncode=run.returncode,
                       stdout=run.stdout, stderr=run.stderr)
            save(out / (row['name'] + '.json'), log)
            logs.append(log)
            assert run.returncode == 0, (row['name'], run.stderr)
            if row['name'].endswith('-link'):
                target = joint / (row['name'].replace('-link', '') + '.nes')
                cv3_mirror(R, target)
                if row['name'] == 'baseline-link':
                    assert target.read_bytes() == (parent / 'candidate.nes').read_bytes(), 'Actual parent reproduction failed'
        new = qualified(joint / 'candidate.nes')
        assert len(old['raw']) == len(new['raw'])
        assert address(new, 'FwNativeDrawAll') == 0xb3c5 and address(new, 'FwNativeDrawAllEnd') == 0xb400
        assert address(new, 'CfP1NativeRestore') == 0xae97 and address(new, 'CfP1NativeRestoreEnd') == 0xaeda
        assert location(new, 'CfP1NativeRestore') == gap
        assert address(new, 'FfMuxNativeTail') == address(old, 'FfMuxRomNative') + 2
        assert address(new, 'FwMuxNativeSelect') == 0xbeb6
        assert native_abi(new) == imports
        envelopes = [(location(new, 'FwNativeDrawAll'), 59), (gap, 67),
                     (location(new, 'CfExternalCookie'), 16), (location(new, 'CfLoaderExpectedCookie'), 16),
                     (16 + 128 * 8192 + 935 * 1024, 24 * 1024)]
        changes = [i for i, pair in enumerate(zip(old['raw'], new['raw'])) if pair[0] != pair[1]]
        assert all(any(lo <= at < lo + count for lo, count in envelopes) for at in changes)
        assert old['raw'][:16] == new['raw'][:16]
        preserved = 0
        for name, sym in old['syms'].items():
            if name.startswith('FwNativeDrawAll::'):
                continue  # Private labels inside the explicitly replaced59B routine.
            assert name in new['syms'] and int(sym['val'], 0) == address(new, name), ('Old symbol moved', name)
            preserved += 1
        for name, digest in {**frozen_inputs, **source_inputs}.items():
            assert sha(name) == digest, ('Input changed during private build', name)
        bound(args.parent_handoff)
        result = dict(passed=True, status='SOURCE_LINKED_RESTORE67_P1_SUCCESSOR_NOT_ADMITTED',
                      parent=args.expected_parent_sha256, candidate=sha(joint / 'candidate.nes'),
                      source=True, native=False, ready=False, admitted=False, installed=False,
                      binary_patch=False, changed_ROM_bytes=len(changes), allowed_envelopes=envelopes,
                      all_old_resolved_symbols_exact_except_private_replaced_draw_labels=preserved,
                      native_imports_checked=108, main_menu_M3_objects_unchanged=True,
                      still_required=plan['still_required'],
                      bindings={**plan['bindings'], str(out / 'prepared.json'): sha(out / 'prepared.json'),
                                **{str(p): sha(p) for p in out.rglob('*') if p.is_file()}})
        save(out / 'source-stage.json', result)
        print(json.dumps(dict(source_stage=str(out / 'source-stage.json'), sha256=sha(out / 'source-stage.json'),
                              candidate=result['candidate'], changed=len(changes))))
    except Exception as error:
        save(out / 'negative.json', dict(passed=False, error=repr(error), traceback=traceback.format_exc(),
                                        native=False, admitted=False))
        raise


if __name__ == '__main__':
    main()
