"""Source-fund Thomas/Shinobi and WWF Start masks without admitting them."""
from pathlib import Path
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
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R / 'build/contra-force-world-roles-1031-v2'
M = R / 'build/bt-p2-cf-menu-source-1031-v2'
S = R / 'docs/qa/checkpoints/2026-10-31/contra-force-jump-contact-source-v1/handoff.json'
O = R / 'build/future-start-masks-1031-v1'
J = O / 'joint'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf-8', newline='\n')


def save(path, data):
    write(path, json.dumps(data, indent=2) + '\n')


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def main():
    assert not O.exists()
    O.mkdir()
    try:
        source = json.loads(S.read_text())
        assert sha(S) == '072c8e8855ff60b0524d9f62a2e7e2e3e9c762660f3e9bff0c96031f8ba86359'
        for name, digest in source['bindings'].items():
            assert sha(name) == digest, name
        parent = P / 'joint/candidate.nes'
        assert sha(parent) == 'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
        old = scoped_load(parent)
        helper = R / 'build/bt-ready-menu-1031-v2/joint/src/cf_menu_body.inc'
        select = R / 'build/contra-force-menu-admission-1031-v2/joint/src/character_select.s'
        mc = json.loads((M / 'main-build.json').read_text())['command']
        lc = json.loads((P / 'final-link.json').read_text())['command']
        main_source = next(Path(x) for x in mc if x.endswith('.s'))
        old_main = Path(mc[mc.index('-o') + 1])
        objects = [Path(x) for x in lc if x.endswith('.o')]
        assert old_main in objects and len([p for p in objects if p.name == 'main.o']) == 1
        cfg_text = Path(lc[lc.index('-C') + 1]).read_text()
        inputs = [Path(__file__), S, helper, select, main_source, M / 'main-build.json',
                  P / 'final-link.json', Path(lc[lc.index('-C') + 1]), *objects,
                  parent, P / 'joint/candidate.dbg', P / 'joint/candidate.lbl']
        pinned = {str(p.resolve()): sha(p) for p in inputs}
        write(J / 'entrypoint.s', main_source.read_text())
        write(J / 'src/character_select.s', select.read_text())
        write(J / 'src/cf_menu_body.inc', helper.read_text())

        def run(name, command):
            guard = validate(command, O, cwd=R)
            for item in guard['outputs']:
                Path(item['path']).parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(command, cwd=R, capture_output=True, text=True)
            save(O / (name + '.json'), dict(command=command, output_guard=guard,
                 returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
            assert result.returncode == 0, (name, result.stderr)

        def build(name):
            command = [str(J / 'entrypoint.s') if x.endswith('.s') else x for x in mc]
            command[1:1] = ['-I', str(J), '-I', str(J / 'src')]
            command[command.index('-o') + 1] = str(J / (name + '.o'))
            dep = '--create-full-dep' if '--create-full-dep' in command else '--create-dep'
            command[command.index(dep) + 1] = str(J / (name + '.dep'))
            run(name + '-main-build', command)
            index = 0

            def redirect(match):
                nonlocal index
                if match[1] in ['', '%O']:
                    return match[0]
                path = J / 'sideoutputs' / name / (f'{index:03d}-' + Path(match[1]).name)
                index += 1
                return 'file="' + path.as_posix() + '"'

            config = J / (name + '.cfg')
            write(config, re.sub(r'file\s*=\s*"([^"]*)"', redirect, cfg_text))
            command = [str(J / (name + '.o')) if Path(x) == old_main else x for x in lc]
            for flag, value in [('-C', config), ('-o', J / (name + '.nes')),
                                ('-Ln', J / (name + '.lbl'))]:
                command[command.index(flag) + 1] = str(value)
            if '-m' in command:
                command[command.index('-m') + 1] = str(J / (name + '.map'))
            else:
                command.extend(['-m', str(J / (name + '.map'))])
            command[command.index('--ld-args') + 1] = '--dbgfile,' + str(J / (name + '.dbg'))
            run(name + '-link', command)
            prepare(R, J / (name + '.nes'))

        build('baseline')
        assert (J / 'baseline.nes').read_bytes() == parent.read_bytes()
        text = helper.read_text()
        text = once(text, ' tax\n lda #$80\n cpx #31\n beq BwStartAlts',
                    ' tax\n lda #$44\n cpx #10\n beq BwStartAlts\n lda #$80\n cpx #31\n beq BwStartAlts')
        text = once(text, ' cpx #30\n beq BwStartGroups\n lda #0',
                    ' cpx #30\n beq BwStartGroups\n lda #7\n cpx #28\n beq BwStartGroups\n lda #0')
        text = once(text, '<= 400,lderror,"Menu helper exceeds root400B limit"',
                    '<= 405,lderror,"Menu helper exceeds root405B limit"')
        write(J / 'src/cf_menu_body.inc', text)
        build('candidate')
        new = scoped_load(J / 'candidate.nes')
        before, after = parent.read_bytes(), (J / 'candidate.nes').read_bytes()
        start = location(old, 'FmCfHelperStart')
        assert location(old, 'FmCfHelperEnd') - start == 393
        assert location(new, 'FmCfHelperEnd') - start == 405
        assert before[start + 393:start + 405] == bytes([255]) * 12
        lo, hi = location(old, 'FmStartRetireFlags'), start + 405
        changes = [i for i, pair in enumerate(zip(before, after)) if pair[0] != pair[1]]
        assert changes and all(lo <= i < hi for i in changes)
        assert before[16 + 128 * 8192:] == after[16 + 128 * 8192:]
        for name in ['FmDrawCfPreview', 'FmCfRestoreP1', 'FmStartRetireFlags', 'FmStartFlags',
                     'FmResolve', 'FmPending', 'BtStatusPlayerCount', 'GameLoop', 'CfP1NativeRestore']:
            assert (address(old, name), location(old, name)) == (address(new, name), location(new, name)), name
        for name, digest in pinned.items():
            assert sha(name) == digest, name
        files = [J / ('candidate.' + s) for s in ['nes', 'dbg', 'lbl', 'cfg', 'map']]
        files += [J / 'entrypoint.s', J / 'src/character_select.s', J / 'src/cf_menu_body.inc']
        files += list(O.glob('*-build.json')) + list(O.glob('*-link.json'))
        save(O / 'source-stage.json', dict(passed=True, source=True, native=False, installed=False,
             candidate=sha(J / 'candidate.nes'), parent=sha(parent), parent_source_reproduced=True,
             current_helper_bytes=393, new_helper_bytes=405, prior_reserved_bytes=400,
             newly_granted_preexisting_menu_filler_bytes=5, new_bytes_are_source_owned_FF_preimage=True,
             readiness_unchanged=True, future_masks=dict(FmAlts={'10': 68}, FmGroups={'28': 7}),
             changed_ROM_bytes=len(changes), changed_owner=[lo, hi], all_nonmask_ROM_exact=True,
             bindings={**pinned, **{str(p.resolve()): sha(p) for p in files}}))
        print(json.dumps(dict(source=True, candidate=sha(J / 'candidate.nes'), helper_bytes=405,
                              changed=len(changes), native=False, installed=False)))
    except Exception as error:
        save(O / 'negative.json', dict(passed=False, error=repr(error), traceback=traceback.format_exc()))
        raise


if __name__ == '__main__':
    main()
