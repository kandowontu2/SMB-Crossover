"""Bind the actual supported metatile $C0 rather than guessing its identity."""
from pathlib import Path
import csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'cap-preparation-q.json';assert not out.exists()
    grid=R/'build/roster-through-2-2/root49-d-samus-m5-paratroopa-o-2-v0-mmc5/actual-paratroopa-grid-o.csv'
    tile=next(int(x['tile'])for x in csv.DictReader(grid.open())if x['x']=='2720'and x['y']=='144');assert tile==192
    s=(D/'stair-policy-p.lua').read_text();assert s.count('c.block(c.x+2,c.y+32)==97')==1
    s=s.replace('c.block(c.x+2,c.y+32)==97','c.block(c.x+2,c.y+32)==192').replace('tile97 stair cap','measuredC0 cap')
    policy=D/'cap-policy-q.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_MEASURED_C0_CAP_SUPPORTED_JUMP',script_sha256=sha(__file__),
      parent_policy_sha256=sha(D/'stair-policy-p.lua'),policy_sha256=sha(policy),prefix_sha256=sha(D/'prefix-mmc5-20959-o.csv'),
      actual_grid_sha256=sha(grid),diagnosis='Retain O/P wrong plane/tile controller bounds. Actual column2720/Y144 is192(C0), with playergroundedY112. Use that measured cap rather than inferred97stair; ordinary controls unchanged.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared measured cap',tile)
if __name__=='__main__':main()
