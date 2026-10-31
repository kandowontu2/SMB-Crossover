"""Recheck owner closure on Ready74 and grant an isolated first-wrestler port."""
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
from wwf_resource_inventory_1031_v1 import fields
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location

P = R / 'build/bt-ready-menu-1031-v2/joint'
J = R / 'build/contra-force-world-roles-1031-v2/joint'
O = R / 'build/wwf-ready74-first-host-resource-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    assert not O.exists()
    original = P / 'candidate.nes'
    current = J / 'candidate.nes'
    assert sha(original) == 'f0b7b9b80ac59b546cee599b9efcb5337b970b11638a669ace78a67dd024724d'
    assert sha(current) == 'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
    before, now = original.read_bytes(), current.read_bytes()
    old, new = scoped_load(original), scoped_load(current)
    closure_path = R / 'build/wwf-resource-consumers-1031-v1/consumers.json'
    closure = json.loads(closure_path.read_text())
    for path, digest in closure['bindings'].items():
        assert sha(path) == digest, path
    segments = [fields(line) for line in (J / 'candidate.dbg').read_text().splitlines()
                if line.startswith('seg\t')]
    checked = []
    for lo, hi in [(426, 460), (546, 604), (629, 668)]:
        a, z = 16 + 1048576 + lo * 1024, 16 + 1048576 + hi * 1024
        assert before[a:z] == now[a:z] == bytes(z - a)
        assert not [s for s in segments if s.get('size') and 'ooffs' in s
                    and s['ooffs'] < z and a < s['ooffs'] + s['size']]
        checked.append(dict(pages=[lo, hi], source_unemitted=True, bytes=z-a,
                            sha256=hashlib.sha256(now[a:z]).hexdigest()))
    for name, size in [('CdPoseChrLo', 60), ('CdPoseChrHi', 60),
                       ('TnBodyChr', 99), ('M3Form0ChrLo', 81), ('MbChrOffsets', 7)]:
        a, b = location(old, name), location(new, name)
        assert a == b and before[a:a+size] == now[b:b+size], name
    a, z = 16 + 96 * 8192, 16 + 97 * 8192
    assert before[a:z] == now[a:z], 'All current Mike code/data/padding must be exact'
    mike = next(s for s in segments if s['name'] == 'MIKE_CORE')
    assert (mike['start'], mike['size'], mike['ooffs']) == (0xa000, 0x936, a)
    assert now[a+0x936:z] == bytes([255]) * (0x2000-0x936)
    O.mkdir()
    cfg = (J / 'candidate.cfg').read_text()
    for name, start, size, keep in [('CD_CHR_MEM', 0x67000, 0xc000, 0x3800),
                                  ('M3_CHR_MEM', 0x83000, 0x14000, 0x5800),
                                  ('TMNT_CHR_MEM', 0x97000, 0x10000, 0x6400)]:
        pattern = rf'(?m)^\s*{name}:\s*start\s*=\s*\${start:x},\s*size\s*=\s*\${size:x},([^\n]*);'
        hits = list(re.finditer(pattern, cfg, re.I))
        assert len(hits) == 1, (name, len(hits))
        suffix = hits[0][1]
        replacement = (f'    {name}: start=${start:x},size=${keep:x},{suffix};\n'
                       f'    {name}_RETAINED_UNUSED_TAIL: start=${start+keep:x},size=${size-keep:x},{suffix};')
        cfg = re.sub(pattern, lambda _: replacement, cfg, count=1, flags=re.I)
    counter = 0

    def side(match):
        nonlocal counter
        if match[1] in ['', '%O']:
            return match[0]
        counter += 1
        path = O / 'sideoutputs' / (f'{counter:03d}-' + Path(match[1]).name)
        return 'file="' + path.as_posix() + '"'

    cfg = re.sub(r'file\s*=\s*"([^"\r\n]*)"', side, cfg)
    (O / 'candidate.cfg').write_text(cfg, encoding='utf-8', newline='\n')
    recipe = J.parent / 'final-link.json'
    command = json.loads(recipe.read_text())['command'][:]
    for flag, target in [('-C', 'candidate.cfg'), ('-o', 'candidate.nes'),
                         ('-Ln', 'candidate.lbl')]:
        command[command.index(flag)+1] = str(O / target)
    if '-m' in command:
        command[command.index('-m')+1] = str(O / 'candidate.map')
    else:
        command += ['-m', str(O / 'candidate.map')]
    command[command.index('--ld-args')+1] = '--dbgfile,' + str(O / 'candidate.dbg')
    objects = [Path(arg) for arg in command if arg.endswith('.o')]
    bound = {str(path.resolve()): sha(path) for path in [Path(__file__), closure_path,
             recipe, J / 'candidate.cfg', current, J / 'candidate.dbg',
             J / 'candidate.lbl', *objects]}
    guard = validate(command, O, cwd=R)
    for output in guard['outputs']:
        Path(output['path']).parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, cwd=R, capture_output=True, text=True)
    dump(O / 'link.json', dict(command=command, output_guard=guard,
         returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    assert result.returncode == 0, result.stderr
    prepare(R, O / 'candidate.nes')
    assert (O / 'candidate.nes').read_bytes() == now
    symbols = lambda p: sorted(re.findall(r'al ([A-Fa-f0-9]+) \.(\w+)', Path(p).read_text()))
    assert symbols(O / 'candidate.lbl') == symbols(J / 'candidate.lbl')
    for path, digest in bound.items():
        assert sha(path) == digest, path
    proof = dict(passed=True, source=True, native=False, installed=False,
         current_sha256=sha(current), exact_current_layout_reproduced=True,
         all_labels_exact=True, checked_retained_owner_tails=checked,
         root_first_host_grant=dict(scope='Private first-Hogan source integration only; root reviews before any native launch/admission.',
              body_pages=[546, 563], selected_template_pages=[629, 653],
              selected_metadata_pages=[653, 655], CHR_pages=43,
              resident=dict(physical_bank=96, A_view=[0xa936, 0xc000], bytes=5834,
                            C_alias=[0xc936, 0xe000], preimage_sha256=hashlib.sha256(now[a+0x936:z]).hexdigest()),
              conditional_RAM_banks=[1, 2, 3], owner='Authenticated selected WWF epoch only',
              global_or_ZP_growth=0, physical_scratch='Only R0..7, scoped and restored',
              menu_mask_handoff='docs/qa/checkpoints/2026-10-31/future-start-masks-source-v1/handoff.json'),
         preconditions=['Source-only conditional lease, not an installed character or automatic host-hook grant.',
              'Keep existing Mike code/data and every foreign endpoint fixed; execute copier from stable C alias while replacing A.',
              'Only forced-blank cold load after retiring previous owner via current5FFF protocol; publish complete cookie last.',
              'No RAM opcode before selected-identity/full-cookie/epoch checks. Return original AXYP/SP/map shadows/SMC state.',
              'No old whole-main/object overlays. Rebuild from actual current source; current roster and native interrupts must remain valid.',
              'The other88 unused owner-tail pages remain unallocated; optional portrait pages are not granted.',
              'Full WWF roster plus Thomas needs a later measured sparse-template/storage contract.'],
         bindings={**bound, **{str(path): sha(path) for path in [O / 'candidate.cfg',
             O / 'link.json', O / 'candidate.nes', O / 'candidate.lbl', O / 'candidate.dbg']}})
    dump(O / 'resource-contract.json', proof)
    print(json.dumps({key: proof[key] for key in ['passed', 'current_sha256',
                     'exact_current_layout_reproduced', 'all_labels_exact', 'root_first_host_grant']}))


if __name__ == '__main__':
    main()
