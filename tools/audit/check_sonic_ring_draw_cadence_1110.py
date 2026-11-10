"""Keep the original thrown-ring pose visible at NES draw cadence."""
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_ring_oam_1110 as Oam
import check_sonic_sms_ring_rebase_1110 as Rebase
from sonic_sms_compact_cold_worker_1110 import assemble


SOURCE = Path(__file__).resolve().parents[1] / 'reference/sonic_drop_projection_1110.s'
RING = Rebase.Feedback


def fix(raw, packet):
    assert sha256(raw).hexdigest() == Oam.PIN
    old = packet['packet']
    code = old['ring_feedback']
    prior = packet['feedback_program']['symbols']
    ring = packet['ring_program']['symbols']
    start, stop = prior['DrawDrop'], prior['EmitPair']
    imports = {name: prior[name] for name in ('DrawFlip', 'DrawAttr', 'EmitPair', 'drops',
                                               'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc')}
    imports.update({name: ring[name] for name in ('DropRecord', 'DropFlags')})
    preamble = ''.join(f'{name} = ${value:04x}\n' for name, value in imports.items())
    new = assemble(preamble + SOURCE.read_text(encoding='ascii'), {'DROP_DRAW': (start, stop-start)})
    replacement = new['images']['DROP_DRAW'].ljust(stop-start, b'\xea')
    assert code[start-0xd800:stop-0xd800] == packet['feedback_program']['images']['RING_FEEDBACK'][start-0xd800:stop-0xd800]
    patched = code[:start-0xd800] + replacement + code[stop-0xd800:]
    assert len(patched) == 1024

    prefix = old['kernel'] + old['metadata'] + old['ring_extension']
    assert old['cookie'][3:] == sha256(prefix + code + old['ring_art']).digest()[:13]
    cookie = old['cookie'][:3] + sha256(prefix + patched + old['ring_art']).digest()[:13]
    at = RING.Live.CHR + old['ring_feedback_page']*1024
    header = RING.Live.COOKIE
    assert raw[at:at+1024] == code and raw[header:header+16] == old['cookie']
    image = bytearray(raw)
    image[at:at+1024] = patched
    image[header:header+16] = cookie
    packet = dict(packet, packet=dict(old, cookie=cookie, ring_feedback=patched))
    details = dict(image_SHA256=sha256(image).hexdigest(), cookie=cookie.hex(),
                   draw_bytes=new['used']['DROP_DRAW'], draw_range=[start, stop],
                   changed_bytes=sum(a != b for a, b in zip(raw, image)))
    return bytes(image), packet, details


def proposal(raw):
    original, common, packet, _ = Rebase.proposal(raw)
    aligned, _ = Oam.fix(original)
    image, packet, details = fix(aligned, packet)
    return image, common, packet, details


def main():
    image, common, packet, details = proposal(Rebase.parent_bytes())
    print(json.dumps(details, sort_keys=True), flush=True)
    print(json.dumps(RING.draw_tests(image, common, packet), sort_keys=True), flush=True)
    print(json.dumps(RING.natural(image, packet), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
