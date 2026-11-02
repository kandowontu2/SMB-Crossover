"""Publish the native-tested Arthur wall and natural-pickup repairs."""
from pathlib import Path
import json
import re
from prepare_selected_native_packet_v1 import R, prepare, sha
from nightly_patch_guard_v1 import check
import check_arthur_side_clamp_1101_v8 as C

O = R / 'build/arthur-nightly-1102-v12'
SOURCE = R / 'build/arthur-side-clamp-1101-v8'
PIN = 'b9e685ffd0620a213a2fc05219e2bae415ee81aa07ab0e994db79455792ef6c4'
PARENT = '6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428'


def main():
    O.mkdir(exist_ok=True)
    rom = SOURCE / 'maturity-candidate.nes'
    assert sha(rom) == PIN
    capture = SOURCE / 'flower-maturity/capture'
    result = json.loads((capture / 'result.json').read_text())
    binding = json.loads((capture / 'binding.json').read_text())
    item = json.loads((capture / 'powerup.json').read_text())
    torch = json.loads((capture / 'torch.json').read_text())
    assert result['passed'] and result['lives_start'] == result['lives_end'] == 2
    assert binding['exit_code'] == 0 and binding['ROM_sha256'] == PIN
    assert item['seen_natural_flower'] and item['mature']
    assert item['source_pickup_calls'] == {'6': 1} and item['source_weapon'] == 68
    assert torch['original_torch_handler_calls'] > 0
    for name in ['CPU.json', 'callers-CPU.json', 'maturity-fix-CPU.json']:
        assert json.loads((SOURCE / name).read_text())['passed']
    native_ready = json.loads((SOURCE / 'flower-maturity/ready.json').read_text())
    for path, digest in native_ready['bindings'].items():
        assert sha(path) == digest, path
    ref = SOURCE / 'flower-maturity/controller.lua'
    text = ref.read_text()
    bundle = C.scoped_load(rom)
    names = set(re.findall(r"\br\('([^']+)'", text)) | set(re.findall(r'\bL\.(\w+)', text))
    banks = set(re.findall(r'\bB\.(\w+)', text))
    prefix = [f'L[{json.dumps(n)}]={C.address(bundle,n)}' for n in sorted(names)]
    prefix += [f'B[{json.dumps(n)}]={(C.location(bundle,n)-16)//8192}' for n in sorted(banks)]
    destination = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(destination) == PARENT
    before = check(destination)
    destination.write_bytes(rom.read_bytes())
    after = check(destination)
    assert sha(destination) == PIN
    prepare(O / 'downloads', rom, '\n'.join(prefix) + '\n' + text,
            [Path(__file__), ref, destination], expected=PIN, timeout=150,
            allow_interactive=True,
            scope='Actual Downloads cold Arthur select/Start, natural first '
                  'flower release/maturity/collection and original B-driven '
                  'torch. Explicit candidate symbols; no debug sidecars '
                  'created in Downloads, no emulated writes or backup. '
                  'Full-stage combat qualification remains incomplete.')
    ready_path = O / 'downloads/ready.json'
    ready = json.loads(ready_path.read_text())
    ready['ROM'] = str(destination)
    ready_path.write_text(json.dumps(ready, indent=2) + '\n')
    receipt = dict(installed=True, ROM_sha256=PIN, previous_sha256=PARENT,
                   destination=str(destination), candidate=str(rom.relative_to(R)),
                   backup_created=False, downloads_launch_verified=False,
                   before=before, after=after, natural_flower=result,
                   item=item, torch=torch, helpers_added=False,
                   scope='Arthur wall separation now agrees with original '
                         'side probes. Correct owned policy admits item '
                         'contact; original collector still rejects immature '
                         'items. First natural flower and torch pass; all '
                         'other ROM bytes retain the previous WIP outside '
                         'Arthur wall215B and two owned table operand bytes.',
                   limits=['Fresh full1-1 clear on this hash remains incomplete.',
                           'Every-character, every-powerup and audio reviews remain active.'])
    (O / 'delivery.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(installed=True, ROM_sha256=PIN, backup_created=False,
                          downloads_launch_verified=False)))


if __name__ == '__main__':
    main()
