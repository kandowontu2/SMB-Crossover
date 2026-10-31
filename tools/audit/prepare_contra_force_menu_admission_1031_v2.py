"""Genuine CF menu admission source child; no native/install certification.

Build only after the root-approved BT source-control handoff is available.
One genuine current main is reassembled with three local menu source overrides;
BT/CF kernels, palettes, cookies, carrier and all other objects remain exact.
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
from prepare_cv3_dmc_mirror import prepare
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address, location

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


def bound(path):
    doc = json.loads(path.read_text())
    for name, digest in doc.get('bindings', {}).items():
        assert sha(name) == digest, name
    return doc


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-joint', type=Path, required=True)
    ap.add_argument('--parent-handoff', type=Path, required=True)
    ap.add_argument('--link-recipe', type=Path, required=True)
    ap.add_argument('--main-recipe', type=Path, required=True)
    ap.add_argument('--expected-parent-sha256', required=True)
    ap.add_argument('--output-root', type=Path, required=True)
    args = ap.parse_args()
    parent = args.parent_joint.resolve()
    out = args.output_root.resolve()
    assert out.is_relative_to(R / 'build') and not out.exists()
    joint = out / 'joint'
    (joint / 'src').mkdir(parents=True)
    try:
        handoff = bound(args.parent_handoff)
        assert sha(parent / 'candidate.nes') == args.expected_parent_sha256
        link = json.loads(args.link_recipe.read_text())['command']
        objects = [Path(v).resolve() for v in link if Path(v).suffix == '.o']
        mains = [p for p in objects if p.name == 'main.o']
        assert len(mains) == 1
        oldmain = mains[0]
        compile_cmd = json.loads(args.main_recipe.read_text())['command']
        assert Path(compile_cmd[compile_cmd.index('-o') + 1]).resolve() == oldmain
        entries = [Path(v).resolve() for v in compile_cmd if Path(v).suffix == '.s']
        assert len(entries) == 1 and entries[0].parent == oldmain.parent
        source_root = oldmain.parent
        originals = {name: source_root / 'src' / name for name in
                     ['character_select.s', 'full_roster_menu.s', 'full_roster_menu_art.inc']}
        pinned = {str(p): sha(p) for p in [parent / 'candidate.nes', parent / 'candidate.dbg',
                  parent / 'candidate.lbl', args.parent_handoff, args.link_recipe, args.main_recipe,
                  entries[0], *originals.values(), *objects]}
        old = qualified(parent / 'candidate.nes')
        # The actual root BT child must retain the placed and qualified CF67.
        assert address(old, 'CfP1NativeRestore') == 0xae97
        assert location(old, 'CfP1NativeRestore') == 16 + 91 * 8192 + 0xe97
        cfgarg = Path(link[link.index('-C') + 1])
        config = cfgarg.read_text()
        pinned[str(cfgarg.resolve())] = sha(cfgarg)
        logs = []

        def run(name, command):
            guard = validate(command, out, cwd=R)
            done = subprocess.run(command, cwd=R, capture_output=True, text=True)
            record = dict(command=command, output_guard=guard, returncode=done.returncode,
                          stdout=done.stdout, stderr=done.stderr)
            save(out / (name + '.json'), record)
            logs.append(out / (name + '.json'))
            assert done.returncode == 0, (name, done.stderr)

        def cfg(name):
            number = 0

            def redir(match):
                nonlocal number
                if match[1] in ['', '%O']:
                    return match[0]
                p = joint / 'sideoutputs' / name / ('%03d-' % number + Path(match[1]).name)
                number += 1
                p.parent.mkdir(parents=True, exist_ok=True)
                return 'file="' + p.as_posix() + '"'

            text = re.sub(r'file\s*=\s*"([^"]*)"', redir, config)
            path = joint / (name + '.cfg')
            write(path, text)
            return path

        def link_one(name, main_obj):
            command = [str(joint / main_obj) if Path(v).suffix == '.o' and Path(v).resolve() == oldmain else v for v in link]
            for flag, value in [('-C', cfg(name)), ('-o', joint / (name + '.nes')),
                                ('-Ln', joint / (name + '.lbl'))]:
                command[command.index(flag) + 1] = str(value)
            if '-m' in command:
                command[command.index('-m') + 1] = str(joint / (name + '.map'))
            else:
                command.extend(['-m', str(joint / (name + '.map'))])
            command[command.index('--ld-args') + 1] = '--dbgfile,' + str(joint / (name + '.dbg'))
            run(name + '-link', command)
            prepare(R, joint / (name + '.nes'))

        # First source-reproduce the real parent without any local menu override.
        write(joint / 'entrypoint.s', entries[0].read_text())

        def main_command(output, local):
            command = compile_cmd[:]
            command[command.index('-o') + 1] = str(joint / (output + '.o'))
            depflag = '--create-full-dep' if '--create-full-dep' in command else '--create-dep'
            command[command.index(depflag) + 1] = str(joint / (output + '.dep'))
            command = [str(joint / 'entrypoint.s') if Path(v).suffix == '.s' else v for v in command]
            if local:
                command[1:1] = ['-I', str(joint), '-I', str(joint / 'src')]
            return command

        run('baseline-main-build', main_command('baseline-main', False))
        link_one('baseline', 'baseline-main.o')
        assert (joint / 'baseline.nes').read_bytes() == (parent / 'candidate.nes').read_bytes(), 'Current main source reproduction failed'

        roster = originals['full_roster_menu.s'].read_text()
        roster = once(roster, ' adc #26\nPending:sec\n rts', ' adc #26\n clc\n rts\nPending:sec\n rts')
        roster = once(roster, '.assert *-FmPending<=241,lderror,"Existing pending span"\n.res 7,$ea',
                      '.assert *-FmPending<=243,lderror,"Existing248B pending envelope"\n.res 5,$ea')
        menu = originals['character_select.s'].read_text()
        menu = once(menu, '.proc DrawSelectionPreview\n  farcall FmPending\n  bcc FmNativePreview\n  cmp #26',
                    '.proc DrawSelectionPreview\n  farcall FmPending\n  bcs FmPendingPreview\n  cpx #30\n  bne FmNativePreview\nFmPendingPreview:\n  cmp #26')
        old_hints = ''.join(name + ': .byte "SELECT  CHANGE HERO "\n' for name in
                            ['DwHint', 'Z2Hint', 'TnHint', 'CdHint', 'Cv3Hint', 'M3Hint', 'ProtoHint'])
        aliases = ''.join(name + ':\n' for name in ['DwHint', 'Z2Hint', 'TnHint', 'CdHint', 'Cv3Hint', 'M3Hint'])
        menu = once(menu, old_hints, aliases + 'ProtoHint: .byte "SELECT  CHANGE HERO "\n')
        assert '.res $c8c-(*-CrossoverMenuInput),$ff' in menu
        art = originals['full_roster_menu_art.inc'].read_text()
        name_rows = {}
        for name in ['BURNS', 'SMITH', 'IRON', 'BEANS']:
            match = re.search(r'^ \.byte "([^"\n]*\*' + name + r'[^"\n]*)"$', art, re.M)
            assert match and len(match[1]) == 16, (name, match[1] if match else None)
            new = match[1].replace('*', ' ')
            assert len(new) == 16
            art = once(art, match[0], ' .byte "' + new + '"')
            name_rows[name] = new
        texts = {'character_select.s': menu, 'full_roster_menu.s': roster, 'full_roster_menu_art.inc': art}
        diff = []
        for name, text in texts.items():
            dest = joint / 'src' / name
            write(dest, text)
            diff.extend(difflib.unified_diff(originals[name].read_text().splitlines(True), text.splitlines(True),
                                            fromfile=str(originals[name]), tofile=str(dest)))
        write(out / 'menu-source.diff', ''.join(diff))
        run('main-build', main_command('main', True))
        link_one('candidate', 'main.o')
        new = qualified(joint / 'candidate.nes')
        menu_seg = next(v for v in new['segs'].values() if v['name'] == '"PROTO_MENU"')
        assert int(menu_seg['size'], 0) == 0xc8c
        assert address(new, 'FmResolve') == address(old, 'FmResolve')
        assert address(new, 'FmPending') == address(old, 'FmPending')
        assert address(new, 'CrossoverMenuInput') == address(old, 'CrossoverMenuInput')
        assert new['raw'][:16] == old['raw'][:16]
        changed = [i for i, pair in enumerate(zip(old['raw'], new['raw'])) if pair[0] != pair[1]]
        fm_seg = new['segs'][new['syms']['FmPending']['seg']]
        names_seg = new['segs'][new['syms']['FmNames']['seg']]
        envelopes = [(int(menu_seg['ooffs'], 0), int(menu_seg['size'], 0)),
                     (int(fm_seg['ooffs'], 0), int(fm_seg['size'], 0)),
                     (int(names_seg['ooffs'], 0), int(names_seg['size'], 0))]
        # Same genuine character_select.s producer has one cross-segment
        # consumer: its PN fallback JMP QueueVariantHint+3 must follow the
        # linked menu label. Only this operand is an additional envelope.
        consumer = []
        for bundle in [old, new]:
            at = location(bundle, 'PnMenuVariantHintGate::Original') + 3
            assert bundle['raw'][at] == 0x4c
            target = bundle['raw'][at + 1] + 256 * bundle['raw'][at + 2]
            assert target == address(bundle, 'QueueVariantHint') + 3
            consumer.append(dict(JMP_file_offset=at, actual_target=target,
                                 genuine_target=address(bundle, 'QueueVariantHint') + 3))
        assert consumer[0]['JMP_file_offset'] == consumer[1]['JMP_file_offset']
        envelopes.append((consumer[1]['JMP_file_offset'] + 1, 2))
        save(out / 'hint-consumer-closure.json', dict(passed=True, same_source_producer=True,
             source=str(originals['character_select.s']), reference='jmp QueueVariantHint+3',
             old_new=consumer, allowed_only_actual_operand_bytes=2,
             retained_v1_negative=str(R / 'build/contra-force-menu-admission-1031-v1/negative.json')))
        assert all(any(lo <= at < lo + size for lo, size in envelopes) for at in changed), 'Change outside actual menu/roster/name source owners'
        assert old['raw'][16 + 128 * 8192:] == new['raw'][16 + 128 * 8192:], 'CHR/carriers changed'
        for name in ['CfP1NativeRestore', 'FwNativeDrawAll', 'BtServiceVeneers', 'BtLoad', 'BtCheck',
                     'CfLoaderProposal', 'CfRetire', 'CfLoadIfCold', 'GameLoop', 'BwScene']:
            assert address(old, name) == address(new, name) and location(old, name) == location(new, name), name
        # Actual diff-envelope validation above also protects every BT/CF/FF
        # loader/kernel/cookie and the existing shared59+67 instruction bytes.
        for name, digest in pinned.items():
            assert sha(name) == digest, ('Parent input changed', name)
        bound(args.parent_handoff)
        result = dict(source=True, native=False, installed=False, admitted=False,
                      candidate=sha(joint / 'candidate.nes'), parent=args.expected_parent_sha256,
                      status='CF_MENU_GATE_SOURCE_ENABLED_FUNCTIONAL_NATIVE_ADMISSION_PENDING',
                      CF_menu_gate_enabled=True, actual_gameplay_admitted=False,
                      source_controls_pending=True, name_rows=name_rows,
                      pending_envelope_bytes=248, PROTO_MENU_bytes=0xc8c, hint_saved_bytes=120,
                      shared59_restore67_BT_CF_payloads_cookies_CHR_exact=True,
                      changed_ROM_bytes=len(changed), allowed_menu_envelopes=envelopes,
                      genuine_crosssegment_hint_consumer=consumer,
                      source_producers={str(k): sha(k) for k in originals.values()},
                      bindings={**pinned, str(Path(__file__).resolve()): sha(__file__),
                                **{str(p): sha(p) for p in out.rglob('*') if p.is_file()}})
        save(out / 'source-stage.json', result)
        print(json.dumps(dict(source_stage=str(out / 'source-stage.json'), sha256=sha(out / 'source-stage.json'),
                              candidate=result['candidate'], changed=len(changed))), flush=True)
    except Exception as error:
        save(out / 'negative.json', dict(passed=False, error=repr(error), traceback=traceback.format_exc(), native=False))
        raise


if __name__ == '__main__':
    main()
