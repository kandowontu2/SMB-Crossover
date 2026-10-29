"""Fresh ordinary source compilation for the half-open side successor."""
from pathlib import Path
import rogue_dawn_floor_ordinary_v2 as inherited
if __name__=='__main__':
 inherited.O=Path(__file__).resolve().parents[1]/'build/rogue-dawn-side-v1'
 inherited.main()
