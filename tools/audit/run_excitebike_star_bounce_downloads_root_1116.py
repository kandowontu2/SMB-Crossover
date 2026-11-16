"""Root actual-Downloads Excitebike Star with actor feedback."""
import argparse
import replay_excitebike_star_bounce_ready5_91dc_1116 as F
from run_excitebike_mushroom_downloads_root_1116 import run_case

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--lead4', action='store_true')
    args = ap.parse_args()
    if args.lead4:
        import replay_excitebike_star_bounce_lead4_91dc_1116 as F
    name = 'excitebike-star-bounce-lead4-downloads-root-1116.json' if args.lead4 else 'excitebike-star-bounce-downloads-root-1116.json'
    run_case(F, F.R/'docs/qa/allocations'/name, 'star')
