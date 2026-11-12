"""Check Shatterhand's AAB cue and the crossover's compiled pulse1 mixer seam."""

import json

import check_steve_shatterhand_companion_live_1111 as Live


D = Live.DONOR
C, N, W = Live.C, Live.N, Live.W
HOST = 'c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2'
STREAM = bytes.fromhex('fe02e102e330d031d02fd031d033a031702f40311033ff')
VOLUMES = (0x3f, 0x3f, 0x3f, 0x3f, 0x3c, 0x39, 0x36, 0x33)
PITCHES = (0x31, 0x2f, 0x31, 0x33)
RESET = ((0x4000, 0x30), (0x4001, 0x88), (0x4002, 0), (0x4003, 0))


def pulse_row(tick):
    if tick in (0, 17):
        return RESET
    if not tick & 1:
        return ()
    index = tick // 2
    row = ((0x4000, VOLUMES[index]), (0x4002, PITCHES[index % len(PITCHES)]))
    return row + ((0x4003, 0xc0),) if tick == 1 else row


def donor(raw):
    def prg0(start, count):
        offset = 16 + start - 0x8000
        return raw[offset:offset+count]

    assert prg0(0x8e50+2*(0x1a-1), 2) == bytes.fromhex('528f')
    assert prg0(0x8f52, 4) == bytes.fromhex('0940d794')
    assert prg0(0x94d7, len(STREAM)) == STREAM
    assert tuple(0x30 | ((byte >> 4) + 2) for byte in STREAM[6:-1:2]) == VOLUMES
    assert tuple(STREAM[7:-1:2]) == PITCHES * 2
    seed = D.boot(raw)
    ref, cue, natural = (D.fork(seed) for _ in range(3))

    def capture(c):
        row = []
        b = c.memory

        def watch(at, value):
            if at == 0xf1 or 0x4000 <= at <= 0x4013 or at == 0x4015:
                row.append((b.frame, at, value, b.code_key(c.pc)))

        b.watch = watch
        return row

    def channel(rows, frame, lower, upper):
        return tuple((at, value) for f, at, value, _ in rows if f == frame and lower <= at <= upper)

    control, isolated, retrigger = (capture(c) for c in (ref, cue, natural))
    first = seed.memory.frame+1
    cue.memory[0xf1] = 0x1a
    for tick in range(19):
        D.frame(ref, 0)
        D.frame(cue, 0)
        epoch = first+tick
        assert channel(control, epoch, 0x4004, 0x4015) == channel(isolated, epoch, 0x4004, 0x4015), tick
        pulse = channel(isolated, epoch, 0x4000, 0x4003)
        if tick < 18:
            assert pulse == pulse_row(tick), (tick, pulse)
        else:
            restored = tuple((0x4000+i, cue.memory[at]) for i, at in enumerate((0x3d5, 0x3d7, 0x3da, 0x3db)))
            assert pulse == restored
            assert [site for f, at, _, site in isolated if f == epoch and 0x4000 <= at <= 0x4003] == [
                (0, at) for at in (0x825c, 0x8262, 0x8268, 0x826e)]

    natural.memory[0x5c4] = 0x25
    for _ in range(164):
        D.frame(natural, 2)
    hits = [f for f, at, value, site in retrigger if at == 0xf1 and value == 0x1a and site == (13, 0xaa46)]
    assert hits == [2529, 2533, 2537, 2541]
    for f in range(hits[0]+1, hits[-1]+19):
        tick = f-max(hit for hit in hits if hit < f)-1
        assert channel(retrigger, f, 0x4000, 0x4003) == pulse_row(tick), (f, tick)
    return dict(prg0_stream=STREAM.hex(), pitch_and_control_bytes=len(VOLUMES)+len(PITCHES),
                charge_requests=hits, consumed_next_frame=True, isolated_ticks=18,
                native_pulse1_restore_tick=18, other_channel_comparisons=19)


def mixer(raw):
    assert C.digest(raw) == HOST
    bundle = dict(W.Symbols.bundle(), raw=raw)
    assert W.address(bundle, 'X5NativeNoiseSpan') == 0xa586
    assert W.address(bundle, 'X5NativeNoiseMask') == 0xbfbd
    anchor = W.location(bundle, 'X5NativeNoiseSpan')
    assert raw[anchor:anchor+8] == bytes.fromhex('20bdbfd0034c2da9')
    native, last, dirty, effect, fx_dirty = (
        W.address(bundle, name) for name in ('GuestNativeApu', 'GuestApuLast', 'GuestNativeDirty',
                                              'GuestFxApu', 'GuestFxDirty'))

    def run(m, noise_mask):
        m.writes.clear()
        c = N.NesMPU(memory=m, pc=0xa586)
        c.a, c.p, c.sp = noise_mask, 0x25, 0xe0
        c.stPushWord(0x5aff)
        C.Vector.finish(m, c, (0x5b00, 0xe0))
        return tuple((at, value) for at, value in m.writes if 0x4000 <= at <= 0x4015)

    comparisons = 0
    for mask in (0, 8):
        for salt in (11, 62, 149):
            m = C.Common.blank(bundle)
            m.raw_page(1, 0x9d)
            N.put(m, GuestMixMask=mask, GuestMixChanged=mask)
            image = bytes((i*37+salt) & 255 for i in range(16))
            m[native:native+16] = image
            m[last:last+16] = bytes(v ^ 255 for v in image)
            m[dirty:dirty+16] = bytes(16)
            m[effect:effect+16] = bytes(v ^ 128 for v in image)
            m[fx_dirty:fx_dirty+16] = bytes(16)
            baseline = run(C.Vector.clone(m), mask)
            m[last:last+4] = image[:4]
            m[dirty:dirty+4] = bytes(4)
            shadow = run(m, mask)
            assert shadow == tuple((at, value) for at, value in baseline if at >= 0x4004)
            assert bytes(m[native:native+16]) == image
            m[dirty:dirty+4] = bytes((1,))*4
            N.put(m, GuestMixChanged=0)
            release = run(m, mask)
            assert tuple((at, value) for at, value in release if at < 0x4004) == tuple(
                (0x4000+i, image[i]) for i in range(4))
            assert bytes(m[native:native+16]) == image
            comparisons += 1
    return dict(compiled_pulse_lease_cases=comparisons, native_paths=['ordinary', 'active shared noise'])


def main():
    from deliver_steve_laserbot_1111 import PIN, digest, recover_parent

    host = D.HOST.read_bytes()
    if digest(host) == PIN:
        host = recover_parent(host)
    print(json.dumps(dict(donor=D.PIN, host=HOST, **donor(D.DONOR.read_bytes()),
                          **mixer(host)), indent=2), flush=True)


if __name__ == '__main__':
    main()
