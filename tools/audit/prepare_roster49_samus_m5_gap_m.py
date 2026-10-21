"""Fresh A from the last real 2-1 lower-floor support."""
from pathlib import Path
import csv,hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'gap-preparation-m.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-koopa-l-2-v0-mmc5'
    pose=next(x for x in csv.DictReader((parent/'trace.csv').open())if x['frame']=='19670')
    assert pose['y']=='176'and pose['state']=='0';x=int(pose['x']);assert 1440<x<1450
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-19669-m.csv';prefix.write_text('\n'.join(lines[:19670])+'\n')
    s=(D/'gap-policy-i.lua').read_text()
    s=s.replace('c.world==0 and c.level==1 and c.x==1268',f'c.world==1 and c.level==0 and c.x=={x}')
    s=s.replace('actual-gap-grid-i.csv','actual-gap-grid-m.csv').replace('1232,1408,16','1408,1584,16')
    s=s.replace('c.x<1278','c.x<1470').replace('c.x>=1273','c.x>=1458').replace('c.x>=1360','c.x>=1560')
    policy=D/'gap-policy-m.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_REAL_2_1_LOWER_FLOOR_FRESH_JUMP',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),actual_start=pose,
      diagnosis='L crosses actualKoopa but reference keepsA held while grounded through1460 then walks off1472gap. Release from real lowerfloor then freshA1458, with actual leftfoot84 guard; no source/geometry change.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared actual2-1 lowerfloor fresh jump M at',x)
if __name__=='__main__':main()
