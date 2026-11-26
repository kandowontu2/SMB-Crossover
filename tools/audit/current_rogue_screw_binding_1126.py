"""Bind the retained earned-Screw combat controller to the exact 1126 nightly.

The old ROM is recovered only in memory for frozen controller metadata.  Every
executed hook is checked against the supplied current image.  This module never
launches Mesen or writes a ROM/controller.  Its one compiler scratch directory
stays inside the caller's bounded output root and is removed before returning.
"""

import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile
from unittest.mock import patch

from check_ff_stdout_controller_source_1110 import LuaRuntime
import build_storage_guard_v1 as Storage
import compose_prince_active_pipe_fall_1126 as Active
import compose_prince_ledge_landing_1124 as Ledge
import compose_prince_pipe_play_1124 as PipePlay
import compose_prince_used_ledge_grab_1126 as Grab
import compose_sonic_current_auth_epoch_1122 as Sonic
import run_roster_empty_cadence_current_1123 as Current
import run_rogue_screw_combat_native_1123 as Combat


R, ROM = Combat.Stdout.R, Combat.ROM
PIN = '83b387931d2cf22981b6267fe062d246ba684d1bcb62e066d932dc9ae82aee40'
REFERENCE = '28708fa9a4e7dd88f1aaa72653b7d5a6ba0fb3c6d5abf544a526b09d333a884c'
OUT = R / 'build/rogue-current-binding-1126'


def H(data):
    return sha256(data).hexdigest()


def output_root(output):
    output = Path(output or OUT).resolve()
    assert output.is_relative_to((R / 'build').resolve()) and output != (R / 'build').resolve()
    Storage.preflight(private_root=output, reserved_bytes=1_000_000, reserved_files=10, fresh=True)
    output.mkdir(parents=True, exist_ok=True)
    return output


@lru_cache(maxsize=2)
def reference(raw, output=None):
    """Recover exact287 metadata from exact83 without touching the shared slot."""
    assert isinstance(raw, bytes) and len(raw) == 2097168 and H(raw) == PIN
    output = output_root(output)
    before = {p.resolve() for p in output.rglob('*') if p.is_file()}
    # First unwind the four later Prince-only changes to the typed50ddd input
    # already supported by the retained current-image metadata resolver.
    parent = Active.inverse(raw)
    parent = Grab.inverse(parent)
    parent = Ledge.inverse(parent)
    parent = PipePlay.inverse(parent)
    assert H(parent) == PipePlay.PARENT
    original_temporary = tempfile.TemporaryDirectory
    with original_temporary(dir=output, prefix='.rogue-binding-') as temporary:
        scratch = Path(temporary)

        def bounded_temporary(*args, **kwargs):
            kwargs['dir'] = scratch
            return original_temporary(*args, **kwargs)

        # Arthur's typed inverse recompiles one small loader.  Redirect its
        # existing output argument and every nested compiler temp into scratch.
        with patch.object(Current.Previous.Timing, 'SHARED', scratch), \
             patch.object(tempfile, 'TemporaryDirectory', bounded_temporary):
            original59 = Current.reference(parent)
            assert H(original59) == Sonic.PIN
            authenticated, _ = Sonic.proposal(original59)
            owner, recovered = Combat.Block.Trees.Nightly.images(authenticated)
            assert owner == original59 and H(recovered) == REFERENCE == Combat.PIN
    assert {p.resolve() for p in output.rglob('*') if p.is_file()} == before
    return recovered


def config(text):
    """Evaluate only declarative binding statements, never the controller."""
    boundary = text.index('local frame,polls,entries,updates=')
    return LuaRuntime().execute(text[:boundary] + '\nreturn C')


@lru_cache(maxsize=2)
def packet(raw, output=None):
    old = reference(raw, output)
    original = Combat.controller(old)
    assert H(original.encode()) == Combat.CONTROLLER
    bindings = config(original)
    assert bindings.sha == REFERENCE and original.count(REFERENCE) == 1
    updates = []
    hooks = []
    lua = Combat.Block.Trees.Base.Base.J.Previous.Previous.Frozen.lua
    for name, hook in sorted(bindings.hooks.items()):
        expected = bytes(v for _, v in sorted(hook.bytes.items()))
        at, pc = 16 + int(hook.offset), int(hook.PC)
        assert old[at:at + len(expected)] == expected, ('Stale frozen hook', name)
        assert (at - 16) % 8192 == pc % 8192, ('Hook mapping', name)
        actual = raw[at:at + len(expected)]
        if actual != expected:
            assert name == 'GameLoop', ('Changed Rogue/native hook needs review', name)
            updates.append('C.hooks.' + name + '.bytes=' + lua(list(actual)))
        hooks.append(dict(name=name, PC=pc, offset=at - 16, bytes=len(actual),
                          current_SHA256=H(actual), changed=actual != expected))
    text = original.replace(REFERENCE, PIN, 1)
    if updates:
        boundary = text.index('local frame,polls,entries,updates=')
        text = text[:boundary] + '\n'.join(updates) + '\n' + text[boundary:]
    # The entire gameplay policy and all acceptance gates remain byte-exact.
    boundary = original.index('local frame,polls,entries,updates=')
    assert text[text.index('local frame,polls,entries,updates='):] == original[boundary:]
    for name, hook in config(text).hooks.items():
        expected = bytes(v for _, v in sorted(hook.bytes.items()))
        at = 16 + int(hook.offset)
        assert raw[at:at + len(expected)] == expected, ('Actual current hook', name)
    executable = '\n'.join(line.split('--', 1)[0] for line in text.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)', executable)
    LuaRuntime().compile(text)
    proof = dict(passed=True, ROM_SHA256=PIN, metadata_reference_SHA256=REFERENCE,
                 reference_controller_SHA256=Combat.CONTROLLER,
                 controller_SHA256=H(text.encode()), controller_bytes=len(text.encode()),
                 hooks=hooks, actual_hook_preimages=True, exact_functional_body=True,
                 compiler_scratch_removed=True, ROM_outputs=0, controller_outputs=0,
                 route_executed=False, native_Mesen=False)
    return text, proof


def controller(raw, output=None):
    """Return current input-only combat Lua; suitable for a Spring extension."""
    return packet(raw, output)[0]


def validate(raw, output=None):
    return packet(raw, output)[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    raw = ROM.read_bytes()
    result = validate(raw, args.output)
    assert ROM.read_bytes() == raw
    result['source_SHA256'] = H(Path(__file__).read_bytes())
    print('ROGUE_CURRENT_BINDING ' + json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
