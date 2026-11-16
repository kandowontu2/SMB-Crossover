"""Root full Excitebike route from the current actual Downloads ROM."""
import replay_excitebike_full11_underground_91dc_1116 as F
from run_excitebike_mushroom_downloads_root_1116 import run_case

if __name__=='__main__':
    run_case(F,F.R/'docs/qa/allocations/excitebike-full11-downloads-root-1116.json','excitebike')
