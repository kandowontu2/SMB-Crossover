"""Root actual-Downloads Peach powered Star or hidden life replay."""
import argparse
from run_excitebike_mushroom_downloads_root_1116 import run_case

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=('star', 'oneup'))
    kind = parser.parse_args().kind
    if kind == 'star':
        import replay_smb1_peach_star_effect_91dc_1116 as F
    else:
        import replay_smb1_peach_stock_91dc_1116 as F
    run_case(F, F.R/f'docs/qa/allocations/smb1-peach-{kind}-downloads-root-1116.json', kind)
