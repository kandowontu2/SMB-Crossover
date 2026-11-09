"""Materialize the funded Prince alignment repair and replay exact V8 input."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

from prepare_selected_native_packet_v1 import prepare


R = Path(__file__).resolve().parents[2]
OUT = R / 'build/prince-d6c0-align-native-1110'
PROOF = R / 'build/prince-d6c0-align-1110/funded.json'
BASE = R / 'build/prince-roof-scroll-native-1110/prince-private.nes'
V8 = R / 'build/prince-post-pit-landing-writer-1110/retreat/native'
SYMBOLS = (BASE.with_suffix('.lbl'), BASE.with_suffix('.dbg'))
PARENT = '4699c73befdd331b7e49a8b992a4f15f52d14eed81ac2d76f3b69c63ba3c846e'
CANDIDATE = '529e51490f610f690ad16c84a868615820cf4e438154127925e15feb5fd7bff1'
COOKIE = 535476
OLD_COOKIE = bytes.fromhex('a72602211077666de966b9268ba46b7d')
NEW_COOKIE = bytes.fromhex('a726020ca89fb6312c40ddffdbc0e6a7')
CHR_START = 16 + 128 * 8192
CHR_PAGES = (617, 621, 623, 625, 627, 690, 691, 692, 693, 695, 795, 291, 514)
MAX_BYTES = 2_225_000
MAX_FILES = 5
PINS = {
    PROOF: 'd66ccbcfaa6fd51efffce7705b5d60304be2b3a7aa3c237e26405d01c6355058',
    BASE: PARENT,
    BASE.with_name('candidate.json'): '67ffb0fdb48d24818d7be255cb8c5dc11ab0cd5f84a9565e3d9b78c829cc0a48',
    SYMBOLS[0]: 'f4c7158a7bca4a2b642c785d86207aa8abbf8e6c93307dd7e3e58cdfae563dbf',
    SYMBOLS[1]: 'f36b95f895ef2014f157d11360427b0db4b77840c09bcae51f920c7f758cb4c6',
    V8 / 'ready.json': 'aba44078ca924dffcfc563e39c3d721371860018a2354f1abefb8d954659503a',
    V8 / 'controller.lua': '8a9bd80dac8af977ee6f329ed5b5ff150f7edd53d72bb3b9621391058ee94ec2',
    V8 / 'run.py': '84d2a16b8f0b6aa7c22717f9eefbda494f21fcc0f923907384b74d63991cc49b',
}


def read(path):
    return json.loads(path.read_bytes())


def checked(mapping):
    paths = {(R / path).resolve(): digest for path, digest in mapping.items()}
    for path, digest in paths.items():
        assert sha256(path.read_bytes()).hexdigest() == digest, path
    return paths


def rebuild(proof, base):
    assert len(base) == 2_097_168 and base[COOKIE:COOKIE + 16] == OLD_COOKIE
    assert proof['passed'] and not proof['ROM_written'] and not proof['Mesen_run']
    assert (proof['parent_SHA256'], proof['expected_memory_only_SHA256']) == (PARENT, CANDIDATE)
    assert proof['Prince_cookie'] == NEW_COOKIE.hex()
    assert proof['layout']['worker_half_open'] == [0xD672, 0xD68F]
    assert proof['layout']['decoder_and_existing_code_exact']
    extents = {COOKIE: 16, **{CHR_START + p * 1024: 1024 for p in CHR_PAGES}}
    extents[CHR_START + CHR_PAGES[-1] * 1024] = 921
    assert len(proof['patches']) == len(extents)
    image = bytearray(base)
    spans = []
    for patch in proof['patches']:
        offset = patch['offset']
        before = bytes.fromhex(patch['preimage'])
        after = bytes.fromhex(patch['replacement'])
        length = extents.pop(offset)
        assert len(before) == len(after) == length and before != after, patch['role']
        assert base[offset:offset + length] == before, patch['role']
        image[offset:offset + length] = after
        spans.append(dict(offset=offset, bytes=length, role=patch['role'],
                          changed_bytes=sum(a != b for a, b in zip(before, after, strict=True))))
    assert not extents and image[COOKIE:COOKIE + 16] == NEW_COOKIE
    assert sha256(image).hexdigest() == CANDIDATE
    return image, spans


def controller():
    old = (V8 / 'controller.lua').read_bytes().decode('utf-8')
    # V8 supplies its own local symbols and physical hook signatures. Its
    # wrapper does not need sibling symbol copies to resolve any hook.
    assert old.startswith('local L={')
    edits = [(f'Q.ROM_sha256="{PARENT}"', f'Q.ROM_sha256="{CANDIDATE}"')]
    cookie = lambda raw: 'Q.cookie={' + ','.join(str(byte) for byte in raw) + '}'
    edits.append((cookie(OLD_COOKIE), cookie(NEW_COOKIE)))
    text = old
    for before, after in edits:
        assert text.count(before) == 1 and after not in text
        text = text.replace(before, after)
    restored = text
    for before, after in reversed(edits):
        assert restored.count(after) == 1
        restored = restored.replace(after, before)
    assert restored == old and 'emu.write(' not in text
    sys.path.insert(0, str(R / 'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--verify-only', action='store_true')
    args = cli.parse_args()
    out = args.output.resolve()
    assert out == OUT and not out.exists(), out
    direct = checked(PINS)
    proof, ready, parent = map(read, (PROOF, V8 / 'ready.json', BASE.with_name('candidate.json')))
    assert parent['candidate_SHA256'] == PARENT and parent['Prince_cookie'] == OLD_COOKIE.hex()
    assert Path(ready['ROM']).resolve() == BASE and ready['ROM_sha256'] == PARENT
    assert ready['prepared'] and not ready['native'] and not ready['emulated_writes']
    assert (ready['timeout'], ready['allow_interactive']) == (225, True)
    assert (ready['run_byte_cap'], ready['max_files'], ready['max_PNGs']) == (128_000_000, 64, 4)
    funding = checked(proof['bindings'])
    nested = {}
    for name in ('proof.json', 'lifetime.json'):
        path = PROOF.with_name(name)
        assert path in funding, path
        nested.update(checked(read(path)['bindings']))
    prior = checked(ready['bindings'])
    assert Path(prepare.__code__.co_filename).resolve() in prior
    image, spans = rebuild(proof, BASE.read_bytes())
    text = controller()
    receipt = dict(passed=True, private=True, native_pending=True, Mesen_run=False,
                   parent_SHA256=PARENT, candidate_SHA256=CANDIDATE, Prince_cookie=NEW_COOKIE.hex(),
                   patch_manifest=str(PROOF.relative_to(R)), patch_manifest_SHA256=direct[PROOF],
                   verified_patch_spans=spans, controller_only=True, V8_inputs_unchanged=True,
                   V8_controller_changes=['Q.ROM_sha256', 'Q.cookie'],
                   rebound_controller_SHA256=sha256(text.encode('utf-8')).hexdigest(),
                   read_only_symbols={str(path.relative_to(R)): direct[path] for path in SYMBOLS},
                   native_receipts=['third-pipe.json', 'post-pit-goombas.json', 'full11.json'],
                   ROM_written=not args.verify_only, materialize_max_bytes=MAX_BYTES,
                   materialize_files=MAX_FILES)
    if args.verify_only:
        print(json.dumps(receipt, indent=2))
        return

    out.mkdir()
    rom = out / BASE.name
    rom.write_bytes(image)
    manifest = out / 'candidate.json'
    receipt['bindings'] = {str(path.relative_to(R)): digest for path, digest in (direct | funding | nested).items()}
    receipt['producer_SHA256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    manifest.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    prepare(out / 'native', rom, text, {Path(__file__), manifest, *direct, *funding, *nested, *prior},
            expected=CANDIDATE, timeout=ready['timeout'], allow_interactive=ready['allow_interactive'],
            scope=ready['scope'] + ' Exact funded Prince alignment with unchanged V8 input and observers.',
            rom_symbols=SYMBOLS)
    assert (out / 'native/run.py').read_bytes() == (V8 / 'run.py').read_bytes()
    files = [path for path in out.rglob('*') if path.is_file()]
    size = sum(path.stat().st_size for path in files)
    assert len(files) == MAX_FILES and size <= MAX_BYTES, (len(files), size)
    print(json.dumps(dict(staged_files=len(files), staged_bytes=size, candidate_SHA256=CANDIDATE)))


if __name__ == '__main__':
    main()
