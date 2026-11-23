"""Verify actual cold transport and ready Prince code across all four streams."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import compose_prince_oneup_lift_1123 as Compose

Lift, H = Compose.Lift, Compose.H
P, W, N = Lift.F.Q.P, Lift.W, Lift.N


def verify(parent, image, overlay):
    chunks, rows, cookie, _ = Compose.extract(image)
    assert Compose.inverse(image, overlay) == parent
    assert overlay['decoded'] == chunks and overlay['cookie'] == cookie.hex()
    proof = Lift.B.binding(parent)
    active = owner = None
    completed = []
    imports = 0
    saves = []

    def authenticate(raw):
        assert raw == image
        return proof

    cold = P.clone(P.cold, dict(authenticate=authenticate, COOKIE=cookie.hex()))

    class Bus(W.ControllerBus):
        def __getitem__(self, key):
            if self is owner and active is not None and isinstance(key, int):
                cursor = active['cursor']
                addresses = active['addresses']
                if cursor < len(addresses) and addresses[cursor] == key:
                    active['cursor'] += 1
            return super().__getitem__(key)

        def __setitem__(self, key, value):
            if self is owner and active is not None and isinstance(key, int):
                offset = key - active['destination']
                if 0 <= offset < active['size']:
                    overlap = active['indices'].get(key)
                    if overlap is not None:
                        assert overlap < active['cursor'], ('Overwrote unread input', active['index'], key)
                    assert offset == active['writes'] and value == chunks[active['index']][offset]
                    active['writes'] += 1
            super().__setitem__(key, value)

    class CPU(N.NesMPU):
        def step(self):
            nonlocal active, owner, imports
            mem = self.memory
            if self.pc == 0xC000 and mem.rawtags[2] == 2:
                owner = mem
                assert active is None and len(completed) < len(Compose.STREAM_ORDER)
                index = Compose.STREAM_ORDER[len(completed)]
                start, destination, count, size = rows[index]
                direct = min(count, 0xDC00 - start)
                addresses = list(range(start, start + direct)) + list(
                    range(Compose.WRAP, Compose.WRAP + count - direct))
                assert count == len(addresses) == len(set(addresses))
                ret = (mem[0x100 + ((self.sp + 1) & 255)]
                       + 256 * mem[0x100 + ((self.sp + 2) & 255)] + 1) & 65535
                assert mem.rawtags[1] == (1 if index == 3 else 3)
                assert N.get(mem, 'CurrentBank') == mem.rawtags[1]
                assert self.p & 4 and N.get(mem, 'NmiDisable') & 128
                assert N.get(mem, 'DisableScreenFlag') and N.get(mem, 'Mirror_PPUMASK') & 0x18 == 0
                assert mem.ram[2][0x1FE0] == mem.ram[3][0x1FE0] == 0
                active = dict(index=index, destination=destination, size=size, cursor=0,
                              writes=0, addresses=addresses, indices={v: i for i, v in enumerate(addresses)},
                              ret=(ret, (self.sp + 2) & 255), bank=mem.rawtags[1])
            elif mem is owner and active is not None and (self.pc, self.sp) == active['ret']:
                assert active['writes'] == active['size'] and active['cursor'] == len(active['addresses'])
                completed.append(dict(stream=active['index'], bank=active['bank'],
                                      packed=active['cursor'], bytes=active['writes']))
                active = None
            if mem is owner and self.pc == 0xA000 and mem.rawtags[1] == 1:
                assert len(completed) == 4 and active is None
                assert bytes(mem.ram[1][:len(chunks[3])]) == chunks[3]
                imports += 1
            if mem is owner and self.pc == 0xBBC1 and mem.rawtags[1] == 3 and not saves:
                assert len(completed) == 4 and imports > 0
                assert all(bytes(mem.ram[bank][0x1FE0:0x1FF0]) == cookie for bank in (2, 3))
                saves.append(dict(PC=self.pc, mapped_banks=list(mem.rawtags), both_owner_cookies=True,
                                  pickup_C7B3=bytes(mem[0xC7B3:0xC7BF]).hex()))
            return super().step()

    with patch.object(W, 'ControllerBus', Bus), patch.object(N, 'NesMPU', CPU):
        model = cold(image)
        for _ in range(12):
            model.controller_pad = 0
            P.Engine.Frames.frame(model, cold=True)
    assert len(completed) == 4 and active is None and imports and saves
    assert H(model.bundle['raw']) == H(image)
    return dict(candidate=H(image), parent=H(parent), decoded=completed,
                spare_carrier_bytes=overlay['spare_bytes'],
                cookie=cookie.hex(), warm_imports=imports, first_draw=saves[0],
                no_unread_input_overwritten=True, outputs=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--swept', action='store_true')
    parser.add_argument('--wide-lift', action='store_true')
    parser.add_argument('--hold-plane', action='store_true')
    args = parser.parse_args()
    parent = P.G.ROM.read_bytes()
    if args.swept or args.wide_lift or args.hold_plane:
        import probe_prince_lift_swept_plane_1123 as Sweep

        planner = (Sweep.hold_plane_plan if args.hold_plane else
                   Sweep.wide_plan if args.wide_lift else Sweep.compact_plan)
        image, overlay = Compose.compose(parent, planner)
    else:
        image, overlay = Compose.compose(parent)
    print('PRINCE LIFT COMPOSE ' + json.dumps(dict(candidate=H(image), cookie=overlay['cookie'],
          packed=overlay['packed_bytes'], spare=overlay['spare_bytes']), separators=(',', ':')), flush=True)

    def deny(*args, **kwargs):
        raise AssertionError('Cold verification attempted an artifact write or emulator launch')

    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), patch('subprocess.Popen', deny):
        result = verify(parent, image, overlay)
    digest = H(json.dumps(result, sort_keys=True, separators=(',', ':')).encode())
    print('PRINCE LIFT COLD ' + json.dumps(dict(result, receipt=digest), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
