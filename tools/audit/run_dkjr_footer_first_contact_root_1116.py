"""Root first-contact Mesen calibration on the exact private current join."""
import replay_dkjr_footer_first_contact_root_1116 as F
from run_dkjr_footer_current_private_route_root_1116 import run_case

if __name__ == '__main__':
    q = run_case(F, F.C.R/'docs/qa/allocations/dkjr-footer-first-contact-root-1116.json')
    r = q['receipt']
    assert 0 < len(r.get('contact_probe', {})) <= 8
    assert r['contact_counts']['lpc'] > 0
