"""Compose Jay's native head effect into authenticated existing carriers."""

from hashlib import sha256
import json

import check_jay_head_bridge_1113 as B

PARENT_PIN = 'a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
CANDIDATE_PIN = '9349a0f5a66673b3a6e0bc00fcd351b2f3b3ab7a1858b4b5fdbc4f3f9864311d'
NEW_COOKIE = bytes.fromhex('a810200bd95329ce2991ea9772f5eaf4')


def digest(raw):
    return sha256(raw).hexdigest()


def cold(raw, cookie, pin):
    return B.Current.cold(raw, pin=pin, cookie=cookie)


def proposal(raw):
    assert digest(raw) == PARENT_PIN
    # The independent Karnov scene successor has no Jay/shared cache edits.
    import compose_karnov_scene_motor_1113 as Karnov
    parent = Karnov.inverse(raw)
    assert digest(parent) == B.Current.PIN
    _, model = cold(raw, B.Current.COOKIE, PARENT_PIN)
    fields = B.bindings(model)
    code, runtime, sizes = B.assemble(model, fields)
    assert sizes['proposed_total'] <= sizes['capacity']
    stage, transport = B.Gun.staged(runtime)
    assert len(stage) == 2048 and transport['used'] == sizes['proposed_total']
    out, edits = bytearray(raw), []

    def replace(at, old, new, label):
        assert len(old) == len(new) and raw[at:at+len(old)] == old, label
        assert parent[at:at+len(old)] == old, label
        out[at:at+len(old)] = new
        edits.append(dict(file=at, size=len(new), label=label))

    start = B.Gun.C.CHR+331*1024
    replace(start, B.Gun.T.page(raw, 331)+B.Gun.T.page(raw, 332), stage, 'existing compressed primary')
    for name in ('FILTER', 'HEAD_CALL', 'CANCEL_RETURN'):
        pc, _ = code['layout'][name]
        body = code['images'][name]
        at = B.Gun.C.CHR+B.Gun.T.EXTRA_PAGE*1024+pc-0xbc00
        replace(at, bytes([0xea])*len(body), body, name)
    cookie = bytes.fromhex('a810200b')+sha256(b'Jay native head bridge 1113\0'+stage+b''.join(
        code['images'][name] for name in ('FILTER', 'HEAD_CALL', 'CANCEL_RETURN'))).digest()[:12]
    assert raw.count(B.Current.COOKIE) == 2
    hot = B.Gun.C.offset(94, 0xb2ef)
    loader = B.Gun.C.offset(65, B.Gun.T.COLD)
    cookie_at = raw.index(B.Current.COOKIE, loader, loader+B.Gun.T.COLD_SIZE)
    for at in (hot, cookie_at):
        replace(at, B.Current.COOKIE, cookie, 'joint cache identity')
    result = bytes(out)
    allowed = set().union(*(set(range(e['file'],e['file']+e['size'])) for e in edits))
    assert all(a == b or i in allowed for i,(a,b) in enumerate(zip(raw,result)))
    if CANDIDATE_PIN is not None:
        assert digest(result) == CANDIDATE_PIN and cookie == NEW_COOKIE
    return result, dict(parent_SHA256=PARENT_PIN, candidate_SHA256=digest(result), cookie=cookie,
        source_SHA256=digest(B.SOURCE.read_bytes()), compressed=sizes, transport=transport,
        code=code, fields=fields, edits=edits, allocation_growth=0)


def inverse(raw):
    assert CANDIDATE_PIN is not None and digest(raw) == CANDIDATE_PIN
    _, model = cold(raw, NEW_COOKIE, CANDIDATE_PIN)
    original = B.Gun.C.Jay.build()
    # Recreate the authenticated old primary from its retained runtime.
    runtime = bytearray(model.ram[3][:0x8c0])
    cancel = original['symbols']['CancelUpwardVelocity']-0xa000
    runtime[cancel:cancel+6] = original['images']['PRIVATE'][cancel:cancel+6]
    first = 0xa83d-0xa000
    runtime[first:first+44] = bytes([0xea])*44
    stage, _ = B.Gun.staged(bytes(runtime))
    restored = bytearray(raw)
    at = B.Gun.C.CHR+331*1024
    restored[at:at+2048] = stage
    for pc, size in ((0xbc98,8), (0xbd1c,4), (0xbe17,25)):
        at = B.Gun.C.CHR+B.Gun.T.EXTRA_PAGE*1024+pc-0xbc00
        restored[at:at+size] = bytes([0xea])*size
    loader = B.Gun.C.offset(65, B.Gun.T.COLD)
    at = raw.index(NEW_COOKIE, loader, loader+B.Gun.T.COLD_SIZE)
    for at in (at, B.Gun.C.offset(94,0xb2ef)):
        restored[at:at+16] = B.Current.COOKIE
    result = bytes(restored)
    assert digest(result) == PARENT_PIN and proposal(result)[0] == raw
    return result


if __name__ == '__main__':
    installed = B.Current.ROM.read_bytes()
    parent = inverse(installed) if digest(installed) == CANDIDATE_PIN else installed
    image, info = proposal(parent)
    _, model = cold(image, info['cookie'], info['candidate_SHA256'])
    for name,(pc,_) in info['code']['layout'].items():
        body = info['code']['images'][name]
        assert bytes(model.ram[3][pc-0xa000:pc-0xa000+len(body)]) == body, name
    print(json.dumps({k:v.hex() if isinstance(v,bytes) else v for k,v in info.items()
                      if k not in ('code','fields')}))
