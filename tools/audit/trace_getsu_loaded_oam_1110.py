"""Trace actual c8 Getsu OAM shadow and DMA ownership after loaded drawing."""

import argparse
from pathlib import Path
import json

import check_getsu_native_stage_1110 as S


R, O, N, SHA = S.R, S.O, S.N, S.SHA
LOAD = R / 'build/getsu-loaded-stage-1110'


def image():
    p = O.Page.load_json(LOAD / 'proof.json')
    base, old, _, prior = S.reconstruct(S.OWNER)
    raw = bytearray(base['raw'])
    for row in p['patch_PRG']:
        at, a, z = row['file_offset'], bytes.fromhex(row['old_hex']), bytes.fromhex(row['new_hex'])
        assert raw[at:at + len(a)] == a
        raw[at:at + len(z)] = z
    body = (LOAD / 'kernel.bin').read_bytes()
    assert SHA(body) == p['kernel_SHA256']
    for i, page in enumerate(old['code_pages']):
        at = page['file_offset']
        assert raw[at:at + 1024] == prior[i * 1024:(i + 1) * 1024]
        raw[at:at + 1024] = body[i * 1024:(i + 1) * 1024]
    art = (S.ART.parent / 'atlas.chr').read_bytes()
    at = O.Page.CHR + 990 * 1024
    raw[at:at + 1024] = art
    assert SHA(raw) == p['expected_memory_only_SHA256']
    return dict(base, raw=bytes(raw)), p


class TraceBus(S.ColdBus):
    events = None
    point = None

    def __setitem__(self, address, value):
        if self.events is not None and isinstance(address, int):
            if 0x200 <= address < 0x300 or address in (0x06de, 0x6b06, 0x6b07, 0x6e1):
                self.events.append(dict(pc=self.point, address=address, value=value))
            if address == 0x4014:
                oam = bytes(self[value << 8:(value + 1) << 8])
                self.events.append(dict(pc=self.point, address=address, first=oam[:32].hex(),
                                        visible=[list(oam[i:i + 4]) for i in range(0, 256, 4) if oam[i] < 240]))
        return super().__setitem__(address, value)


def trace(b):
    m = TraceBus(b)
    cpu = O.NesMPU(memory=m, pc=None)
    cpu.reset()
    for _ in range(300000):
        if cpu.pc == S.address(b, 'IdleLoop'):
            break
        assert m[cpu.pc]
        cpu.step()
    else:
        raise AssertionError('No native IdleLoop')
    m.vblank_at_boot = False
    for i in range(120):
        if m[0x7307] == 2:
            break
        S.frame(m, 16 if i == 40 else 0, None)
    else:
        raise AssertionError('No native menu')
    for pad, count in ((1, 5), (32, 4), (16, 1)):
        for _ in range(count):
            S.frame(m, 0, None)
            S.frame(m, pad, None)
    assert m[0x6002] == 42
    for _ in range(600):
        if tuple(N.get(m, k) for k in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
            break
        S.frame(m, 0, None)
    else:
        raise AssertionError('No active stage')
    N.put(m, NmiDisable=255, SavedJoypadBits=0, SavedJoypad1Bits=0, SavedJoypad2Bits=0)
    m.events = []
    track = {(3, 0xa4be): 'GfDraw'}
    for name in ('PlayerOAMReservation', 'MetaspriteRenderLoop', 'PlayerGfxHandler', 'DrawAll',
                 'X5PublishChr', 'MoveAllSpritesOffscreen'):
        if name not in b['syms']:
            continue
        at = O.location(b, name)
        track[((at - 16) // 8192 | 128, S.address(b, name))] = name

    def watch(c):
        if c.pc < 0x8000:
            m.point = ('RAM', c.pc)
        else:
            bank = m.rawtags[(c.pc - 0x8000) // 8192]
            m.point = (bank, c.pc)
            name = track.get(m.point)
            if name:
                m.events.append(dict(pc=m.point, call=name, current_oam=m[0x06de],
                                     pose=bytes(m[0x6b06:0x6b08]).hex(), oam0=bytes(m[0x200:0x214]).hex()))
    S.FRONT.F.invoke(m, 'GameLoop', watch=watch)
    before_dma = bytes(m[0x200:0x300])
    m.point = 'NMI'
    N.consume(m)
    return dict(events=m.events, pre_DMA_visible=[list(before_dma[i:i + 4]) for i in range(0, 256, 4) if before_dma[i] < 240],
                chr=m.chr_latches, final_pose=bytes(m[0x6b06:0x6b08]).hex(), final_cursor=m[0x06de])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build')
    b, p = image()
    result = trace(b)
    out.mkdir(exist_ok=True)
    (out / 'oam-trace.json').write_text(json.dumps(dict(memory_only_SHA256=p['expected_memory_only_SHA256'], **result), indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'events'}))


if __name__ == '__main__':
    main()
