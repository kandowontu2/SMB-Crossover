"""Strict currentbc5 binding; old67 factories and endpoints remain immutable."""
from hashlib import sha256
from pathlib import Path
import compose_hot_draw_bt_67e_1115 as Hot
import replay_dkjr_public_early_depart_67_1115 as Early
import replay_dkjr_public_early_grounded12_67_1115 as Ground

PIN = 'bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040'
KIND = 'hotdraw-bc5'
HOT_SHA = '60bf0a62b3b81e56331d035aa32e11f580296f39c1f9d8223de55b02fbfff9e7'
EARLY_SHA = '2828bad479ce3d609dbe79adb86a494a39014a7a14690a7fb8930b1b2d50c40e'


def normalize(raw, *, kind):
    if kind != KIND:
        raise ValueError('Explicit hotdraw-bc5 input kind required')
    assert isinstance(raw, bytes) and sha256(raw).hexdigest() == PIN
    assert sha256(Path(Hot.__file__).read_bytes()).hexdigest() == HOT_SHA
    assert sha256(Path(Early.__file__).read_bytes()).hexdigest() == EARLY_SHA
    assert Hot.CANDIDATE == PIN and Hot.PIN == Early.Old.PIN
    reference = Hot.inverse(raw)
    assert sha256(reference).hexdigest() == Early.Old.PIN
    info, _ = Early.Old.identity(reference)
    spans = [(Early.Old.CHR+p*1024, 1024) for p in Early.Old.PAGES]
    spans += [(Early.Old.COOKIE_AT, 16)]
    spans += [(at, len(before)) for at, before in Early.Old.PUBLIC_NATIVE]
    assert sum(size for _, size in spans) == 11433
    for at, size in spans:
        assert raw[at:at+size] == reference[at:at+size]
        assert at+size <= Hot.FILE or at >= Hot.FILE+Hot.SIZE
    return reference, dict(actual_input_SHA256=PIN, explicit_kind=kind,
                          reference67_SHA256=Early.Old.PIN,
                          complete_DK_owner_SHA256=info['complete_DK_owner_SHA256'],
                          complete11433B_DK_owner_exact=True,
                          inverse='compose_hot_draw_bt_67e_1115.inverse',
                          execution_ROM_is_not_normalized_reference=True)


def controller(raw, *, grounded12=True):
    reference, _ = normalize(raw, kind=KIND)
    old = Ground.controller(reference) if grounded12 else Early.controller(reference)
    assert old.count(Early.Old.PIN) == 1
    text = old.replace(Early.Old.PIN, PIN, 1)
    assert text.replace(PIN, Early.Old.PIN, 1) == old
    Ground.LuaRuntime().compile(text)
    return text
