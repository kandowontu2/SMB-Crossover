"""Repeat public getter, header and scene checks on the exact scene derivative."""
from collections import Counter
from hashlib import sha256
import json

import check_sonic_native_scene_1110 as Scene
import check_sonic_public_admission_1110 as Public

PIN = '9e4d1bb5bc50fd019ac95dd6435b698f556f530bf7418a88fd216ae5c1cda14e'
T, S, W = Scene.T, Scene.T.S, Public.W


def scripted(seed, packet):
    counters = Counter()
    native = (
        (10, 'BlockBufferColli_Head', 0, 4),
        (14, 'BlockBufferColli_Side', 3, 8),
        (35, 'BlockBufferColli_Feet', 0, 32),
        (35, 'BlockBufferColli_Feet', 1, 32),
    )
    for engine in (3, 5, 6, 7, 9, 10, 11, 12):
        for grounded in (False, True):
            for row, name, y, dy in native:
                for tile in (0, 0x54, 0xc2):
                    arena = T.clone(seed, packet)
                    S.scene(arena, 64, 176)
                    S.set_native(arena, GameEngineSubroutine=engine, PlayerSize=0)
                    arena[0xc030] = 128 if grounded else 0
                    for x in (64, 72, 80):
                        arena[T.pointer(x, 176 + dy)] = tile
                    expected = T.clone(arena, packet)
                    direct, _ = T.invoke(expected, W.address(arena.bundle, name), y=y, watch=False)
                    actual = Public.public(arena, row, y, a=85, x=73)
                    assert (actual.a, actual.x, actual.y, actual.p & 0xcf) == (
                        direct.a, direct.x, direct.y, direct.p & 0xcf), (engine, row, grounded, tile)
                    assert bytes(arena[3:11]) == bytes(expected[3:11]), (engine, row, grounded, tile)
                    assert arena.ram == expected.ram and arena.rawtags == expected.rawtags
                    counters['scripted_public_matches_native_getter'] += 1
            arena = T.clone(seed, packet)
            S.set_native(arena, GameEngineSubroutine=engine)
            before = bytes(arena[S.host(arena, 'BoundingBox_UL_Corner'):S.host(arena, 'BoundingBox_UL_Corner') + 4])
            result = Public.public(arena, 16, 0)
            after = bytes(arena[S.host(arena, 'BoundingBox_UL_Corner'):S.host(arena, 'BoundingBox_UL_Corner') + 4])
            assert not result.p & 1 and before == after, engine
            counters['scripted_bounds_requests_native_fallback'] += 1
    return dict(counters)


def main():
    image, program, packet, record = Scene.combined()
    assert sha256(image).hexdigest() == PIN == record['image_SHA256']
    public = Public.getters(image, program, packet)
    seed = public.pop('ready_seed')
    public.pop('samples')
    scenarios = scripted(seed, packet)
    lifetime = Public.lifecycle(image, program, packet)
    print(json.dumps(dict(passed=True, source_CPU_only=True, output_files=0, image_SHA256=PIN,
        scene=record, ordinary=public, scripted=scenarios, lifetime=lifetime)), flush=True)


if __name__ == '__main__':
    main()
