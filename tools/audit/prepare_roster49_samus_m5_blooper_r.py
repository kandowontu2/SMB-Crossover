"""Finish the observed low-health Blooper before leaving genuine lower floor."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'build/verification/root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=D/'blooper-preparation-r.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    parent=R/'build/roster-through-2-2/root49-d-samus-m5-cap-q-2-v0-mmc5'
    lines=(parent/'inputs.csv').read_text().splitlines();prefix=D/'prefix-mmc5-23369-r.csv';prefix.write_text('\n'.join(lines[:23370])+'\n')
    s=(D/'landing-policy-n.lua').read_text()
    s=s.replace('c.level==0 and c.x==1660 and c.y==112', 'c.level==1 and c.x==763 and c.y==176')
    s=s.replace('actual-landing-grid-n.csv','actual-blooper-grid-r.csv').replace('1632,1824,16','736,848,16')
    s=s.replace('local still,previous=0,0',"local still,previous=0,0\nlocal defended,defenseAge=false,0\nlocal defense=assert(io.open(ROSTER_CONFIG.out..'blooper-defense-r.csv','w'))\ndefense:write('poll,frame,x,y,flag,state,ex,ey,hp,shot0,shot1,shot2,mask\\n')")
    at=s.index(' local key=c.world')
    extra=r''' if not defended then
  defenseAge=defenseAge+1;assert(defenseAge<240,'Bounded actual Blooper beam defense')
  local flag,st=c.r('Enemy_Flag',1),c.r('Enemy_State',1)
  if defenseAge>=16 and(flag==0 or st>=32)then defended=true;lastStage=''end
  local b=c.poll%8<4
  local ex=c.r('Enemy_X_Position',1)+256*c.r('Enemy_PageLoc',1)
  defense:write(table.concat({c.poll,c.frame,c.x,c.y,flag,st,ex,c.r('Enemy_Y_Position',1),c.r('MmEnemyHealthLo',1)+256*c.r('MmEnemyHealthHi',1),c.r('SmShotType',0),c.r('SmShotType',1),c.r('SmShotType',2),b and 64 or 0},',')..'\n');defense:flush()
  return{b=b}
 end
'''
    s=s[:at]+extra+s[at:];policy=D/'blooper-policy-r.lua';policy.write_text(s)
    sys.path.insert(0,str(R/'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'))
    from lupa.lua54 import LuaRuntime
    LuaRuntime().eval('function(s) return assert(load(s)) end')(s)
    out.write_text(json.dumps(dict(status='PREPARED_REAL_LOWER_FLOOR_BLOOPER_BEAM_DEFENSE',script_sha256=sha(__file__),
      checkpoint_sha256=sha(cp),parent_manifest_sha256=sha(parent/'manifest.json'),prefix_sha256=sha(prefix),policy_sha256=sha(policy),
      diagnosis='Q Blooper1 takes observed beam hits135to95to15, then controller jumps into it at23394. Stop on actual763/Y176 floor and continue ordinary B risingedges until real actor retires before resuming pose proposals.',
      emulated_writes=False,state_loads=False,verified=False,phase_cap_bytes=1000000000,final_reserve_bytes=100000000),indent=2)+'\n')
    print('Prepared actual floor Blooper defense R')
if __name__=='__main__':main()
