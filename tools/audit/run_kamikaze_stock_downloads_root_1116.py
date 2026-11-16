"""Root actual-Downloads natural Kamikaze Flower, Star or hidden life."""
import argparse
from run_excitebike_mushroom_downloads_root_1116 import run_case

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=('flower', 'star', 'oneup'))
    kind = parser.parse_args().kind
    if kind == 'flower':
        import replay_kamikaze_mario_flower_edge_91dc_1116 as F
    elif kind == 'star':
        import replay_kamikaze_mario_star_recovery_91dc_1116 as F
    else:
        import replay_kamikaze_mario_ground_stock_91dc_1116 as F
    run_case(F, F.R/f'docs/qa/allocations/kamikaze-{kind}-downloads-root-1116.json', kind)
