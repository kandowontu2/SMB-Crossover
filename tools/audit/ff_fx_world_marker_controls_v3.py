"""Rebind unchanged strict marker leaf pairs to the actual shared successor."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_fx_world_marker_controls_v2 as K
K.P=R/'build/ff-fx-world-marker-reference-v1/joint'
K.O=R/'build/ff-fx-world-marker-proposal-v2';K.H.O=K.O/'joint'
if __name__=='__main__':K.main()
