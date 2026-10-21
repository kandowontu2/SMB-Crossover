"""Verify lazy health is unchanged by freeze and initialized correctly by the thaw hit."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-passives-bc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'thaw-d-review.json';assert not out.exists()
    probe=json.loads((H/'probe-c-result.json').read_text());assert probe['observation']==dict(timer=360,selected=2,id=6,hpLo=0,behavior=1,flag=1,owned=137,frame=578,hpHi=0,estate=0)
    s=(H/'original-samus-passives-202.lua').read_text()
    needle="r('MmEnemyHealthLo')==35,'Ice deals forty damage then freezes the 75-HP Goomba for six seconds'"
    assert s.count(needle)==1
    s=s.replace(needle,"r('MmEnemyHealthLo')==0 and r('MmEnemyHealthHi')==0,'Source first freeze preserves the native lazy-health sentinel without damage'")
    assert s.count('b=frame>=560 and frame<565')==1
    s=s.replace('b=frame>=560 and frame<565','b=(frame>=560 and frame<565)or(frame>=670 and frame<675)')
    addition=""" -- Authored player placement, not an enemy HP/timer outcome write. The
 -- second real Ice shot must remove freeze and deal40 to default75HP.
 if frame==665 then
  w('Player_X_Position',48);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
  w('PlayerFacingDir',1);w('SmBall',0);w('SmCrouch',1);w('CrouchingFlag',4)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 if frame==690 then
  assert(r('AvFrozen')==0 and r('AvFrozenHi')==0,'Second actual Ice hit removes existing freeze')
  assert(r('MmEnemyHealthLo')==35 and r('MmEnemyHealthHi')==0 and r('Enemy_Flag')~=0 and r('Enemy_State')&32==0,'Thaw hit initializes default75HP then deals40, leaving live35HP')
  local f=assert(io.open(OUTPUT..'thaw-result.json','w'));f:write('{"frame":690,"hp":'..r('MmEnemyHealthLo')..',"timer":'..r('AvFrozen')..',"flag":'..r('Enemy_Flag')..',"state":'..r('Enemy_State')..'}\\n');f:close()
 end
"""
    assert s.count(' if frame==699 then')==1;s=s.replace(' if frame==699 then',addition+' if frame==699 then')
    s=s.replace('PASS real Ice Beam damage, six-second freeze, native frozen-enemy platform, and acquired Screw Attack contact protection/defeat','PASS first-freeze no damage, actual thaw hit75-to35, native frozen platform, and acquired Screw Attack contact protection/defeat')
    src=H/'thaw-d';src.mkdir();body=src/'passives.lua';body.write_text(s)
    wrapper=src/'run.lua';wrapper.write_text('dofile('+json.dumps((R/'tests/menu-bootstrap.lua').as_posix())+')\ndofile('+json.dumps(body.as_posix())+')\n')
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());groups=[]
    for mapper in ['mmc3','mmc5']:
        for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
        o=H/f'thaw-d-{mapper}';o.mkdir()
        q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(o),str(wrapper),str(cp.parent/f'smb-crossover-{mapper}.nes'),'--timeout','60'],cwd=R,capture_output=True,text=True)
        log=H/f'thaw-d-{mapper}-host.log';log.write_text(q.stdout+q.stderr)
        groups.append(dict(mapper=mapper,exit=q.returncode,host_log_sha256=sha(log),files={str(p.relative_to(H)):sha(p)for p in o.iterdir()if p.is_file()}))
    r=dict(status='PASS_FIRST_FREEZE_LAZY_HEALTH_ACTUAL_THAW_DAMAGE_FROZEN_PLATFORM_AND_SCREW'if all(g['exit']==0 for g in groups)else'RETAINED_NEXT_THAW_D_PASSIVE_FAILURE',script_sha256=sha(__file__),body_sha256=sha(body),wrapper_sha256=sha(wrapper),groups=groups,
      exact_changes='First freeze expects unchanged0 health sentinel; adds real controller thaw-hit with exact35HP from default75 minus40. Original immobility, timer range, frozen-platform, no-injury and Screw effect assertions retained.',
      shared_test_modified=False,main_changed=False,goal_complete=False)
    out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],sha(out),flush=True)
if __name__=='__main__':main()
