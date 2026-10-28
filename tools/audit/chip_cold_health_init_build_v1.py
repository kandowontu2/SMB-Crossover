"""Cold-only HP initialization on the frozen queued-HUD candidate; no install."""
from pathlib import Path
import difflib
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
B = R / 'build'
sys.path.insert(0, str(R / 'tools'))
from prepare_cv3_dmc_mirror import prepare
from kirby_icon_palette_build_v1 import command, link
from check_tmnt_audio_fallback_oc import qualified
from current_roster_compact_11_v1 import linked

P = 'chip_cold_health_init'
OLD = '129dabe88489c78e1ead49b17e898979bd01ee0806d44eba2efc1871d4dd227f'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
COLD = '''
; X5InventoryInit already cleared all four profile pages. Initialize the
; selected Chip/Dale constructor before any visible entrance HUD is queued.
; The original variant-restoration loop follows and retains its caller ABI.
.pushseg
.segment "X5_PROFILES"
.proc CdNewGameProfiles
 jsr X5ProfilesNewGame
 lda SelectedCharacter
 cmp #14
 bne Done
 lda #3
 sta CdHealth
 lda #$a5
 sta CdMagic
Done:rts
.endproc
.popseg
'''


def main():
    parent = B / 'chip_hud_queue_complete.nes'
    assert sha(parent) == OLD
    out = B / (P + '.nes')
    assert not out.exists()
    raw, syms, a, loc, _ = linked(parent)
    original = R / 'src/x5_profiles.s'
    before = original.read_bytes()
    eol = b'\r\n' if b'\r\n' in before else b'\n'
    needle = b'  jsr X5ProfilesNewGame' + eol
    assert before.count(needle) == 1
    leaf = B / (P + '_profiles.s')
    leaf.write_bytes(before.replace(needle, b'  jsr CdNewGameProfiles' + eol))
    queue_source = B / 'chip_hud_queue_complete_helper.s'
    helper = B / (P + '_helper.s')
    helper.write_bytes(queue_source.read_bytes() + COLD.replace('\n', '\r\n').encode())
    previous_entry = B / 'chip_hud_queue_complete_entrypoint.s'
    source = previous_entry.read_bytes()
    assert source.count(b'.include "x5_profiles.s"') == 1
    assert source.count(b'.include "chip_hud_queue_complete_helper.s"') == 1
    entry = B / (P + '_entrypoint.s')
    entry.write_bytes(source.replace(b'.include "x5_profiles.s"',
        b'.include "' + leaf.name.encode() + b'"').replace(
        b'.include "chip_hud_queue_complete_helper.s"', b'.include "' + helper.name.encode() + b'"'))
    template = json.loads((B / 'chip_hud_queue_complete_build.json').read_text())['command']
    cmd = command(template, out, entry)
    link(cmd, out)
    prepare(R, out)
    nr, ns, na, nl, _ = linked(out)
    delta = [i for i, (x, y) in enumerate(zip(raw, nr)) if x != y]
    helper_at = nl('CdNewGameProfiles')
    helper_size = int(ns['CdNewGameProfiles']['size'], 0)
    bank = (helper_at - 16) // 8192
    assert bank == (loc('X5InventoryInit') - 16) // 8192
    assert bank != 79
    hook = loc('X5InventoryInit') + raw[loc('X5InventoryInit'):loc('X5InventoryInit') + int(syms['X5InventoryInit']['size'], 0)].index(
        bytes([0x20, a('X5ProfilesNewGame') & 255, a('X5ProfilesNewGame') >> 8]))
    assert nr[hook:hook + 3] == bytes([0x20, na('CdNewGameProfiles') & 255, na('CdNewGameProfiles') >> 8])
    assert raw[helper_at:helper_at + helper_size] == b'\xff' * helper_size
    assert set(delta) <= set(range(hook + 1, hook + 3)) | set(range(helper_at, helper_at + helper_size))
    assert {((i - 16) // 8192) for i in delta} == {bank}
    assert raw[16 + 79 * 8192:16 + 80 * 8192] == nr[16 + 79 * 8192:16 + 80 * 8192]
    old_symbols, new_symbols = qualified(parent), qualified(out)
    assert not {k: (v, new_symbols.get(k)) for k, v in old_symbols.items() if new_symbols.get(k) != v}
    patch = B / (P + '_implementation.patch')
    patch.write_bytes((''.join(difflib.unified_diff(before.decode().splitlines(True), leaf.read_bytes().decode().splitlines(True),
        fromfile='src/x5_profiles.s', tofile='src/x5_profiles.s')) +
        ''.join(difflib.unified_diff(queue_source.read_bytes().decode().splitlines(True), helper.read_bytes().decode().splitlines(True),
        fromfile='src/chip_hud_queue.s', tofile='src/chip_hud_queue.s'))).encode())
    ordinary = []
    for mapper, wanted in [('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                           ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        dest = B / (P + '_' + mapper + '_flagoff.nes')
        c = command(template, dest, entry, mapper)
        link(c, dest)
        assert sha(dest) == wanted
        ordinary.append(dict(mapper=mapper, sha256=wanted, whole_exact=True))
    paths = [Path(__file__), parent, parent.with_suffix('.dbg'), original, queue_source,
             previous_entry, leaf, helper, entry, patch, out, out.with_suffix('.dbg'),
             out.with_suffix('.lbl'), out.with_suffix('.map'), out.with_suffix('.cv3-mirror.json')]
    result = dict(passed=True, source_only=True, native_run=False, parent_sha256=OLD,
                  candidate_sha256=sha(out), changed_bytes=len(delta), changed_banks=[bank],
                  helper=dict(PC=na('CdNewGameProfiles'), bank=bank, size=helper_size),
                  all_existing_qualified_symbols_exact=True, count=len(old_symbols),
                  bank79_complete_queue_candidate_byteexact=True, all_other_ROM_bytes_exact=True,
                  new_RAM=0, new_NMI_or_live_gameplay_code=0,
                  source_overlay={'src/x5_profiles.s': str(leaf), 'src/chip_hud_queue.s': str(helper)},
                  base_queue_source_overlay='Retain129d health leaf and expanded guarded include unchanged.',
                  constructor='Actual new-game profile clear precedes only Chip/Dale HP3/MagicA5; remaining persistent state already cleared.',
                  ordinary=ordinary, command=cmd, bindings={str(p): sha(p) for p in paths})
    receipt = B / (P + '_build.json')
    receipt.write_text(json.dumps(result, indent=2) + '\n', newline='\n')
    print(json.dumps(dict(passed=True, candidate_sha256=sha(out), changed_bytes=len(delta),
                          helper=result['helper'], receipt=str(receipt), sha256=sha(receipt)), indent=2))


if __name__ == '__main__':
    main()
