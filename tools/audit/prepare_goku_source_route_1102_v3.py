"""Use established Goku-specific controller rather than generic air attacks."""
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from check_tmnt_render_oa import address
from observe_chip_committed_write import lua
import audit_current_menu_indicators_1102_v1 as A
from prepare_goku_stair_settle_v9 import POLICY
O=R/'build/goku-source-route-1102-v3'
ROM=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
def main():
    O.mkdir(exist_ok=True);policy=O/'policy.lua';policy.write_text(POLICY)
    source=R/'build/goku-progress-1102-v2/native/controller.lua';text=source.read_text()
    text,n=re.subn(r'local POLICY="[^\n]+"',lambda m:'local POLICY='+lua(policy.as_posix()),text,count=1);assert n==1
    assert "ROSTER_CONFIG={name='goku'}" in text
    text=text.replace("ROSTER_CONFIG={name='goku'}","ROSTER_CONFIG={name='goku',out="+lua(O.as_posix()+'/')+"}")
    dependencies=[R/'tools/playthroughs'/('dragon_power_11_v'+str(i)+'.lua')for i in range(3,8)]
    b=A.bundle();names=set(re.findall(r"c\.r\('([^']+)'",POLICY+'\n'+''.join(p.read_text()for p in dependencies)))
    extension='\nfor n,a in pairs('+lua({n:address(b,n)for n in names})+')do CURRENT_KIRBY_META_EARNED.ram[n]=a end\n'
    first,rest=text.split('\n',1);text=first+extension+rest
    prepare(O/'native',ROM,text,[Path(__file__),source,policy,R/'tools/audit/prepare_goku_stair_settle_v9.py',*dependencies,R/'tools/playthroughs/full_roster_policy_og.lua'],expected=sha(ROM),timeout=240,scope='Current Goku Hard source-specific controller-only natural1-1; no midair attack cancellation, existing native lift boarding/stair settling; no state writes or ROM changes. Bounded8000frames compact telemetry.',allow_interactive=True)
if __name__=='__main__':main()
