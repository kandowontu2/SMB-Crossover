"""Measure the DK Jr. scene trial in the existing two-file Mesen queue."""

import argparse
from functools import cache
from unittest.mock import patch

import compose_dkjr_scene_hot_1123 as Scene
import run_sparse_sprite_occupied_1123 as Occupied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', choices=('empty', 'goomba'))
    args = parser.parse_args()
    trial = Occupied.Trial
    with patch.object(trial.Current, 'reference', cache(trial.Current.reference)):
        if args.scene == 'goomba':
            Occupied.run(('DONKEY KONG JR',), compose=Scene.compose)
        else:
            trial.run(('DONKEY KONG JR',), compose=Scene.compose)


if __name__ == '__main__':
    main()
