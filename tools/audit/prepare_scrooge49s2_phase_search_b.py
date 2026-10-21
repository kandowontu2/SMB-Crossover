"""Private controller-search correction: retain a real phase wait and A edges."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root49s2-scrooge-phase-search-b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not H.exists();H.mkdir()
    source=R/'tools/playthroughs/roster_branch_search.lua'
    text=source.read_text()
    old="local rootWorld,rootLevel,rootFrame,rootPoll"
    assert text.count(old)==1;text=text.replace(old,old+',rootWaitX,rootWaitY')
    old="started=true;rootWorld=r('WorldNumber');rootLevel=r('LevelNumber');rootFrame=frame;rootPoll=poll"
    assert text.count(old)==1;text=text.replace(old,old+";rootWaitX=x();rootWaitY=r('Player_Y_Position')")
    old='  nextBeam={};depth=depth+1;parentIndex=1;actionIndex=1'
    extra="""  -- A grounded wait at the genuine root keeps the firebar phase reachable.
  -- This changes search retention only; it supplies no emulated state.
  local waiting
  for _,n in ipairs(nextBeam)do
   if n.stateByte==0 and n.yHigh==1 and n.x==rootWaitX and n.y==rootWaitY and n.lastMask==0 then waiting=n;break end
  end
  if waiting then
   local found=false;for _,n in ipairs(beam)do if n==waiting then found=true end end
   if not found then if #beam>=cfg.width then table.remove(beam)end;beam[#beam+1]=waiting end
  end
"""
    assert text.count(old)==1;text=text.replace(old,extra+old)
    old="  elseif action=='R-AOFF8'then mask=1+(trialAge>=8 and 128 or 0)"
    assert text.count(old)==1;text=text.replace(old,old+"\n  elseif action=='R-AOFF1'then mask=1+(trialAge>=1 and 128 or 0)\n  elseif action=='AOFF1'then mask=trialAge>=1 and 128 or 0\n  elseif action=='RDA-OFF1'then mask=5+(trialAge>=1 and 128 or 0)")
    old=" local key={};local attack=0"
    extra=""" local key={};local attack=0
 for slot=0,5 do
  local id=r('Enemy_ID',slot)
  if r('Enemy_Flag',slot)>0 and id>=0x1b and id<0x23 then
   key[#key+1]=table.concat({r('FirebarSpinState_Low',slot),r('FirebarSpinState_High',slot),r('FirebarSpinSpeed',slot),r('FirebarSpinDirection',slot)},'/')
  end
 end"""
    assert text.count(old)==1;text=text.replace(old,extra)
    core=H/'search-core.lua';core.write_text(text)
    driver=R/'tools/playthroughs/roster_branch_search.py';code=driver.read_text()
    old='ROOT = Path(__file__).resolve().parents[2]'
    assert code.count(old)==1;code=code.replace(old,'ROOT = Path('+repr(R.as_posix())+')')
    old="'R-AOFF8', 'RB'";assert code.count(old)==1
    code=code.replace(old,"'R-AOFF8', 'R-AOFF1', 'AOFF1', 'RDA-OFF1', 'RB'")
    old="ROOT/'tools/playthroughs/roster_branch_search.lua'";assert code.count(old)==1
    code=code.replace(old,'Path('+repr(core.as_posix())+')')
    ast.parse(code);(H/'run_search.py').write_text(code)
    (H/'preparation.json').write_text(json.dumps(dict(status='PRIVATE_CONTROLLER_SEARCH_ONLY',original_core_sha256=sha(source),original_driver_sha256=sha(driver),core_sha256=sha(core),driver_sha256=sha(H/'run_search.py'),changes=['Retain genuine stationary wait so firebar phase is not greedily pruned','One-frame A-release actions for the narrow native block top','Firebar phase fields retained in state distinction'],emulated_state_patches=False,ordinary_fixed_replay_still_required=True),indent=2)+'\n')
    print(str(H),sha(H/'preparation.json'))
if __name__=='__main__':main()
