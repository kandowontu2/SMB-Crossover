"""Add each actor's native direction to the bounded single-update profile."""
from pathlib import Path
import prepare_mini_enemy_cost_profile_1110_v5 as enemy

actors = enemy.calls.actors
original_prepare = actors.original_prepare


def with_direction(output, rom, source, refs, **kwargs):
    anchor = 'box_control=read(0x0646+i),contact=read(0x0566+i)'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor+',direction=read(0x053f+i)')
    original_prepare(output, rom, source, {*refs, Path(__file__)}, **kwargs)


if __name__ == '__main__':
    actors.original_prepare = with_direction
    actors.profile.prepare = enemy.prepare
    actors.profile.main()
