"""Test observed lower-floor affordance before the high-fish trajectory."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'floor-preparation-s.json';assert not out.exists()
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-blooper-r-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-24139-s.csv';prefix.write_text('\n'.join(lines[:24140])+'\n')
    s=(D/'landing-policy-n.lua').read_text().replace('c.level==0 and c.x==1660 and c.y==112','c.level==1 and c.x==1398 and c.y==176')
    s=s.replace('actual-landing-grid-n.csv','actual-water-floor-grid-s.csv').replace('1632,1824,16','1376,1520,16').replace('96,208,16','32,208,16')
    s=s.replace('local still,previous=0,0',"local still,previous=0,0\nlocal walked,walkAge,walkStill,lastWalkX=false,0,0,0\nlocal walk=assert(io.open(ROSTER_CONFIG.out..'actual-water-floor-s.csv','w'))\nwalk:write('frame,x,y,state,foot2,foot13,front,mask\\n')")
    at=s.index(' local key=c.world')
    extra=r''' if not walked then
  walkAge=walkAge+1;assert(walkAge<700,'Bounded actual water lower-floor route')
  if c.x==lastWalkX then walkStill=walkStill+1 else walkStill=0 end
  assert(walkStill<60,'Actual water affordance blocked; retain grid diagnosis')
  lastWalkX=c.x
  local front=c.block(c.x+16,c.y+32)
  local b={right=true,b=c.poll%8<4}
  if c.grounded and front==0 then b.right=false end
  if c.x>=1600 and c.grounded then walked=true;lastStage=''end
  walk:write(table.concat({c.frame,c.x,c.y,c.state,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32),front,(b.right and 1 or 0)+(b.b and 64 or 0)},',')..'\n');walk:flush()
  return b
 end
'''
    s=s[:at]+extra+s[at:];policy=D/'floor-policy-s.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_OBSERVED_WATER_LOWER_FLOOR_TEST',script_sha256=sha(__file__),
      parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='R killsBlooper, then high water jump meets Cheep1 at1475/Y25 and later Cheep0 at2013/Y38. Test genuine lowerfloor from1398/Y176; stop before missing front support or retain bounded wall diagnosis. No terrain/physics/position writes.',
      emulated_writes=False,state_loads=False,verified=False),indent=2)+'\n')
    print('Prepared observed water lower-floor candidate S')
if __name__=='__main__':main()
