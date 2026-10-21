"""Launch the private search with the original branch-root module available."""
from pathlib import Path
import runpy,sys
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/playthroughs'))
runpy.run_path(str(R/'build/verification/root49s2-scrooge-phase-search-b/run_search.py'),run_name='__main__')
