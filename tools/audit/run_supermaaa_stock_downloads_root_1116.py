"""Root actual-Downloads SuperMaaa earned Flower, Star or hidden life."""
import argparse
from run_excitebike_mushroom_downloads_root_1116 import run_case

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=('flower', 'star', 'oneup'))
    kind = parser.parse_args().kind
    if kind == 'flower':
        import replay_supermaaa_flower_native6_91dc_1116 as F
    elif kind == 'star':
        import replay_supermaaa_star_recovery_91dc_1116 as F
    else:
        import replay_supermaaa_stock_91dc_1116 as F
    run_case(F, F.R/f'docs/qa/allocations/supermaaa-{kind}-downloads-root-1116.json', kind)
