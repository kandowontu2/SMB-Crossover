"""Same floor/caller controls against final carry-preserving service6 worker."""
from pathlib import Path
import rogue_dawn_floor_controls_v2 as inherited
if __name__=='__main__':
 inherited.O=Path(__file__).resolve().parents[1]/'build/rogue-dawn-floor-v4'
 inherited.main()
