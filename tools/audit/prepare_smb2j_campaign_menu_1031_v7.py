"""Build an uninstalled two-campaign frontend on exact a441 source."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R / 'build/contra-force-world-chr-publisher-1031-v1'
M = R / 'build/bt-p2-cf-menu-source-1031-v2'
H = R / 'docs/qa/checkpoints/2026-10-31/contra-force-world-chr-source-v1/handoff.json'
O = R / 'build/smb2j-campaign-menu-source-1031-v7'
J = O / 'joint'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def save(path, data):
    write(path, json.dumps(data, indent=2) + '\n')


def once(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after)


def main():
    assert not O.exists()
    O.mkdir()
    parent = P / 'joint/candidate.nes'
    assert sha(parent) == 'a4410264ffccc7ce44e3b5ead1da639428cfa0594c94b2f63fa99fb4feab5b38'
    source = json.loads(H.read_text())
    for path, digest in source['bindings'].items():
        assert sha(path) == digest, path
    old = scoped_load(parent)
    mc = json.loads((M / 'main-build.json').read_text())['command']
    lc = json.loads((P / 'final-link.json').read_text())['command']
    main_source = next(Path(x) for x in mc if x.endswith('.s'))
    old_main = Path(mc[mc.index('-o') + 1])
    helper = R / 'build/bt-ready-menu-1031-v2/joint/src/cf_menu_body.inc'
    select = R / 'build/contra-force-menu-admission-1031-v2/joint/src/character_select.s'
    fragment = R / 'tools/reference/smb2j_campaign_menu_1031_v5.inc'
    dispatch = R / 'tools/reference/smb2j_campaign_dispatch_1031_v1.inc'
    inputs = [dispatch, Path(__file__), H, parent, P / 'joint/candidate.dbg', P / 'joint/candidate.lbl',
              main_source, helper, select, fragment, M / 'main-build.json', P / 'final-link.json',
              Path(lc[lc.index('-C') + 1]), *[Path(p) for p in lc if p.endswith('.o')]]
    # Bind the complete real main dependency closure, including raw audio that
    # uses unallocated-looking ZP EC/ED outside the linker-owned ZP segment.
    dep = Path(mc[mc.index('--create-full-dep') + 1]).read_text().split(':\t', 1)[1]
    dep = dep.split('\n', 1)[0]
    inputs += [Path(p.replace('\\ ', ' ')) for p in re.split(r'(?<!\\)\s+', dep) if p]
    pinned = {str(p.resolve()): sha(p) for p in inputs}
    write(J / 'entrypoint.s', main_source.read_text())
    write(J / 'src/character_select.s', select.read_text())
    write(J / 'src/cf_menu_body.inc', helper.read_text())
    cfg = Path(lc[lc.index('-C') + 1]).read_text()

    def run(name, command):
        guard = validate(command, O, cwd=R)
        for output in guard['outputs']:
            Path(output['path']).parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(command, cwd=R, capture_output=True, text=True)
        save(O / (name + '.json'), dict(command=command, output_guard=guard,
             returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        assert result.returncode == 0, (name, result.stderr)

    def build(name):
        command = [str(J / 'entrypoint.s') if x.endswith('.s') else x for x in mc]
        command[1:1] = ['-I', str(J), '-I', str(J / 'src')]
        command[command.index('-o') + 1] = str(J / (name + '.o'))
        command[command.index('--create-full-dep') + 1] = str(J / (name + '.dep'))
        run(name + '-main-build', command)
        counter = 0

        def redirect(match):
            nonlocal counter
            if match[1] in ['', '%O']:
                return match[0]
            path = J / 'sideoutputs' / name / (f'{counter:03d}-' + Path(match[1]).name)
            counter += 1
            return 'file="' + path.as_posix() + '"'

        config = J / (name + '.cfg')
        write(config, re.sub(r'file\s*=\s*"([^"]*)"', redirect, cfg))
        command = [str(J / (name + '.o')) if Path(x) == old_main else x for x in lc]
        for flag, path in [('-C', config), ('-o', J / (name + '.nes')),
                           ('-Ln', J / (name + '.lbl')), ('-m', J / (name + '.map'))]:
            command[command.index(flag) + 1] = str(path)
        command[command.index('--ld-args') + 1] = '--dbgfile,' + str(J / (name + '.dbg'))
        run(name + '-link', command)
        prepare(R, J / (name + '.nes'))

    build('baseline')
    assert (J / 'baseline.nes').read_bytes() == parent.read_bytes()
    select_text, helper_text = select.read_text(), helper.read_text()
    # Genuine original dispatcher has eight7B CMP/long-BEQ rows. No labels
    # inside this replaced span are externally entered; all old PCs remain.
    start = select_text.index('  cmp #1\n  jeq BuildScreen')
    stop = select_text.index('  lda CrossoverTitleDrawn', start)
    original_dispatch = select_text[start:stop]
    select_text = once(select_text, original_dispatch,
                       '  jmp J2MenuDispatch\n  .res 53,$ff ; Old56B dispatcher span.\nJ2LegacyTitleCheck:\n')
    select_text = once(select_text, '  lda #0\n  sta FmAlts\n  sta FmGroups\n  farcall InitializeNameTables',
                       '  jsr J2SelectionReset\n  .res 5,$ea ; Old8B flag reset span.\n  farcall InitializeNameTables')
    select_text = once(select_text, '  farcall FmStartFlags\n  farcall CheatsApplyStartingLevel',
                       '  farcall J2OpenCampaign,jmp\n  farcall CheatsApplyStartingLevel')
    select_text = once(select_text, '  lda CrossoverContinue\n  bne :+',
                       '  jsr J2ContinueValue\n  bne :+')
    select_text = once(select_text, '  lda CrossoverContinue\n  ora #Start_Button',
                       '  jsr J2ContinueValue\n  ora #Start_Button')
    select_text = once(select_text, '.assert *-CrossoverMenuInput<=$c8c,', '.include \"smb2j_campaign_dispatch_1031_v1.inc\"\n.assert *-CrossoverMenuInput<=$c8c,')
    # Adopt only the previously verified SOURCE mask funding, not its old Main.
    helper_text = once(helper_text, ' tax\n lda #$80\n cpx #31\n beq BwStartAlts',
                       ' tax\n lda #$44\n cpx #10\n beq BwStartAlts\n lda #$80\n cpx #31\n beq BwStartAlts')
    helper_text = once(helper_text, ' cpx #30\n beq BwStartGroups\n lda #0',
                       ' cpx #30\n beq BwStartGroups\n lda #7\n cpx #28\n beq BwStartGroups\n lda #0')
    helper_text = once(helper_text, '<= 400,lderror,"Menu helper exceeds root400B limit"',
                       '<= 405,lderror,"Menu helper exceeds root405B limit"')
    helper_text = once(helper_text, '.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart),$ff',
                       '.include "smb2j_campaign_menu_1031_v5.inc"\n.res $bfb0-$b49b-(*-FmCfHelperStart),$ff')
    write(J / 'src/character_select.s', select_text)
    write(J / 'src/cf_menu_body.inc', helper_text)
    write(J / 'src/smb2j_campaign_menu_1031_v5.inc', fragment.read_text())
    write(J / 'src/smb2j_campaign_dispatch_1031_v1.inc', dispatch.read_text())
    build('candidate')
    new = scoped_load(J / 'candidate.nes')
    before, after = parent.read_bytes(), (J / 'candidate.nes').read_bytes()
    a, z = 16 + 29 * 8192 + 0x1640, 16 + 29 * 8192 + 0x1ef0
    assert before[a:z] == bytes([255]) * (z - a)
    assert address(new, 'J2MenuStart') == 0xb640 and address(new, 'J2MenuEnd') <= 0xbef0
    assert address(new, 'FmCfHelperEnd') == 0xb630
    future = R / 'build/future-start-masks-1031-v1/joint/candidate.nes'
    first = location(old, 'FmCfHelperStart')
    assert after[first:first+405] == future.read_bytes()[first:first+405], 'Exact previously funded405B mask body'
    pinned[str(future.resolve())] = sha(future)
    old_labels = 0
    for name, sym in old['syms'].items():
        if name.split('::')[-1].startswith('LOCAL-MACRO_SYMBOL-'):
            continue
        if sym.get('type') != 'lab' or 'seg' not in sym or name not in new['syms'] or name.split('::')[-1] in ['FmCfHelperEnd', 'BwStartAlts', 'BwStartGroups']:
            continue
        assert address(old, name) == address(new, name), name
        if 'ooffs' in old['segs'][sym['seg']]:
            assert location(old, name) == location(new, name), name
        old_labels += 1
    changes = [i for i, (x, y) in enumerate(zip(before, after)) if x != y]
    assert changes
    # Both physical banks are explicit. All near edges stay in bank66;
    # root body29 is reached only by real18B farcall transports.
    ranges = [(location(old,'CrossoverMenuInput')+0x24,56),
              (location(old,'CrossoverMenuInput::BuildScreen')+7,8),
              (location(old,'CrossoverMenuInput::FmStartReady'),18),
              (location(old,'CrossoverMenuInput::FmStartReady')+36,3),
              (location(old,'CrossoverMenuInput::FmStartReady')+80,3),
              (first,405), (a,address(new,'J2MenuEnd')-0xb640),
              (16+66*8192+0x10c0,address(new,'J2ProtoEnd')-0xb0c0)]
    assert all(any(start <= i < start+size for start,size in ranges) for i in changes), [hex(i) for i in changes if not any(start<=i<start+size for start,size in ranges)][:12]
    assert address(new,'J2ProtoStart')==0xb0c0 and address(new,'J2ProtoEnd')<=0xb134
    assert (location(new,'J2MenuDispatch')-16)//8192 == (location(old,'CrossoverMenuInput')-16)//8192 ==66
    assert (location(new,'J2SelectionReset')-16)//8192==66
    assert (location(new,'J2ContinueValue')-16)//8192==66
    assert (location(new,'J2GameMenu')-16)//8192==29
    palette=location(old,'SelectPalette'); cp=location(new,'J2MenuPalette')
    assert after[cp:cp+16]==before[palette:palette+16]
    assert before[:16] == after[:16] and before[16 + 1048576:] == after[16 + 1048576:]
    for path, digest in pinned.items():
        assert sha(path) == digest, path
    refs = list(J.glob('*')) + list((J / 'src').glob('*')) + list(O.glob('*-build.json')) + list(O.glob('*-link.json'))
    refs = [p for p in refs if p.is_file()]
    save(O / 'source-stage.json', dict(passed=True, source=True, native=False, installed=False,
         source_component_only=True, SMB2J_campaign_still_declined=True,
         candidate=sha(J / 'candidate.nes'), parent=sha(parent), parent_source_reproduced=True,
         matched_old_label_PCs=old_labels, all_nonmenu_ROM_CHR_and_header_exact=True,
         exact_hook_ranges=ranges, cross_bank_edges_use_real_transport=True,
         new_global_and_ZP_bytes=0, campaign_state='CrossoverContinue lowbit; existing A-bit continue preserved through same-size near helpers. Bit1 is a one-shot roster-resume flag.',
         root_frontend_grant=dict(bank=29, start=0xb640, maximum=0xbef0, actual_end=address(new, 'J2MenuEnd')),
         future_Start_masks_source_funding_included=True, ready_identities_unchanged=74,
         changed_ROM_bytes=len(changes),
         bindings={**pinned, **{str(p.resolve()): sha(p) for p in refs}}))
    print(json.dumps(dict(source=True, native=False, installed=False,
                          candidate=sha(J / 'candidate.nes'), menu_bytes=address(new, 'J2MenuEnd') - 0xb640)))


if __name__ == '__main__':
    main()
