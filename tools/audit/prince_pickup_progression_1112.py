"""Authenticated Prince mushroom progression; retired native-call tables fund it."""
import prince_cold_packet_1111 as Packet

OLD = bytes.fromhex('adcfc6f030b534c902b030b51f1026b534d00cadcfc6c905b013eecfc6d00e8a48a9018deec6a95b2051aa68aa202f8da90620b5983860a003d002a0024c1bda96f8713aa29aafaf0000000000')


def transform(raw, reverse=False):
    def mutate(runtime, metadata, state):
        # NativeCall now addresses relocated five-entry Landing tables D4C8/CD/D2.
        for address, expected in ((0xda3b, 'b9c8d4'), (0xda41, 'b9cdd4'),
                                  (0xda47, 'b9d2d4')):
            at = address - 0xc800
            assert metadata[at:at+3] == bytes.fromhex(expected)
        replacement = bytearray(OLD)
        # Both full-health and healed mushroom branches enter the helper.
        # Flower, immature, dead, star and 1-UP paths retain their old targets.
        replacement[0xc7cc-0xc7b3] = 0x26
        replacement[0xc7d1-0xc7b3] = 0x21
        replacement[0xc7f3-0xc7b3:0xc7fb-0xc7b3] = bytes.fromhex('a9018d5b074ce0c7')
        before, after = (bytes(replacement), OLD) if reverse else (OLD, bytes(replacement))
        assert state.count(before) == 1
        start = state.index(before)
        state[start:start+len(before)] = after
        return runtime, metadata, state
    return Packet.rebuild(raw, mutate)
