"""Root genuine Star check on the unchanged actual Downloads launch context."""
import replay_excitebike_star_return_91dc_1116 as F
from run_excitebike_mushroom_downloads_root_1116 import run_case

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--feedback',action='store_true')
    if ap.parse_args().feedback:
        import replay_excitebike_star_head_feedback_91dc_1116 as Feedback
        run_case(Feedback,Feedback.R/'docs/qa/allocations/excitebike-star-feedback-downloads-root-1116.json','star')
    else:
        run_case(F,F.R/'docs/qa/allocations/excitebike-star-downloads-root-1116.json','star')
