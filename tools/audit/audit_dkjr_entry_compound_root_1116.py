"""Independent public-ancestor ownership review of the entry-only DK Jr image."""
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_forced_entry_current_1116 as C
import replay_dkjr_forced_entry_current_1116 as F

H = lambda value: sha256(value).hexdigest()
COMPOSER_SHA = '67b6ccef60386789854c9f5a9634b92f5178301948b2f0004b0f640f2e9cb7b1'


def main():
    assert H(Path(C.__file__).read_bytes()) == COMPOSER_SHA
    current = C.BT.ROM.read_bytes()
    assert H(current) == C.Parent.PIN
    alpha, first = C.Parent.proposal(current)
    raw, second = C.proposal(alpha)
    assert C.current_proposal(current)[0] == raw
    assert C.inverse(raw) == alpha and C.Parent.inverse(alpha) == current
    owned = set()
    rows = []
    for step, source, spans in (
        ('camera_footer', current, C.Parent.spans(current)),
        ('forced_entry', alpha, C.spans(alpha)),
    ):
        for at, before, after in spans:
            assert len(before) == len(after) and source[at:at+len(before)] == before
            owned.update(range(at, at+len(before)))
            rows.append(dict(step=step, offset=at, bytes=len(before),
                             old_SHA256=H(before), new_SHA256=H(after)))
    changed = {i for i, (a, b) in enumerate(zip(current, raw, strict=True)) if a != b}
    assert changed <= owned
    assert all(raw[i] == current[i] for i in range(len(raw)) if i not in owned)
    for at, size in ((C.BT.CACHE, 8192), (C.BT.HEADER, 487)):
        assert not owned.intersection(range(at, at+size))
        assert raw[at:at+size] == current[at:at+size]
    native = F.controller(raw)
    source = F.controller(raw, source=True)
    report = dict(passed=True, current_SHA256=H(current), alpha_SHA256=H(alpha),
                  candidate_SHA256=H(raw), composer_SHA256=COMPOSER_SHA,
                  factory_SHA256=H(Path(F.__file__).read_bytes()),
                  native_Lua_SHA256=H(native.encode()), source_Lua_SHA256=H(source.encode()),
                  public_union_owned_bytes=len(owned), public_changed_bytes=len(changed),
                  alpha_owned_bytes=first['owned_bytes'], alpha_changed_bytes=first['changed_bytes'],
                  entry_owned_bytes=second['owned_bytes'], entry_changed_bytes=second['changed_bytes'],
                  all_unowned_current_bytes_exact=True, BT8192_and_header487_exact=True,
                  strict_both_inverses=True, spans=rows, outputs=0,
                  scope='Composition and exact controller binding only; no CPU execution, native launch or ROM file write')
    report['receipt_SHA256'] = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
