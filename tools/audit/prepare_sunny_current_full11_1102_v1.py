"""Cold current-menu Sunny full1-1 controller-only qualification."""
import re
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/sunny-current-full11-1102-v1'
ROM=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'

def main():
    O.mkdir(exist_ok=True);source=R/'build/goku-progress-1102-v2/native/controller.lua';text=source.read_text()
    deps=[R/'tools/playthroughs'/name for name in ['sunny_11_v3.lua','sunny_11_v1.lua','mario_luigi_scrooge_policy.lua','mario_luigi_scrooge_nav.lua']]
    policy=deps[0]
    text,n=re.subn(r'local POLICY="[^\n]+"',lambda m:'local POLICY='+lua(policy.as_posix()),text,count=1);assert n==1
    text=text.replace("ROSTER_CONFIG={name='goku'}","ROSTER_CONFIG={name='sunny',out="+lua(O.as_posix()+'/')+"}")
    text=text.replace("r('SelectedCharacter')==24","r('SelectedCharacter')==23").replace("r('SelectedCharacter')~=24","r('SelectedCharacter')~=23").replace('char=24,variant=0','char=23,variant=0').replace('Cold Goku','Cold Sunny')
    routes=[]
    for start in range(32):
        queue=[(start,[])];seen={start}
        for node,route in queue:
            if node==22:routes.append(route[0]if route else'');break
            edges={'left':node//8*8+(node-1)%8,'right':node//8*8+(node+1)%8,'up':(node+24)%32,'down':(node+8)%32}
            for key,nxt in edges.items():
                if nxt not in seen:seen.add(nxt);queue.append((nxt,route+[key]))
    text,n=re.subn(r'C\.navigation=\{[^\n]+\}',lambda m:'C.navigation='+lua(routes),text,count=1);assert n==1
    text=text.replace('d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d',sha(ROM))
    b=A.bundle();names=set(re.findall(r"c\.r\('([^']+)'",'\n'.join(p.read_text()for p in deps)))
    extension='\nfor n,a in pairs('+lua({n:address(b,n)for n in names})+')do CURRENT_KIRBY_META_EARNED.ram[n]=a end\n'
    first,rest=text.split('\n',1);text=first+extension+rest
    prepare(O/'native',ROM,text,[Path(__file__),source,*deps],expected=sha(ROM),timeout=240,scope='Sunny actual raw23, Hard cold32slot menu, controller-only natural mushroom/full1-1. Existing original Mario-family controller; zero game-state writes; bounded8000frames and compact120frame position log.',allow_interactive=True)
if __name__=='__main__':main()
