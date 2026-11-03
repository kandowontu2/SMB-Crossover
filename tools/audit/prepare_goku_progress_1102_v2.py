"""Bounded current-menu Goku discovery with periodic compact position evidence."""
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from observe_chip_committed_write import lua
O=R/'build/goku-progress-1102-v2'
ROM=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
def main():
    O.mkdir(exist_ok=True)
    source=R/'build/goku-full11-1102-v1/native/controller.lua';text=source.read_text()
    routes=[]
    for start in range(32):
        queue=[(start,[])];seen={start}
        for node,route in queue:
            if node==31:routes.append(route[0]if route else'');break
            edges={'left':node//8*8+(node-1)%8,'right':node//8*8+(node+1)%8,'up':(node+24)%32,'down':(node+8)%32}
            for key,nxt in edges.items():
                if nxt not in seen:seen.add(nxt);queue.append((nxt,route+[key]))
    text,n=re.subn(r'C\.navigation=\{[^\n]+\}',lambda m:'C.navigation='+lua(routes),text,count=1);assert n==1
    anchor="local inputFile=assert(io.open(OUTPUT..'inputs.csv','w'));inputFile:write('poll,frame,mask\\n')"
    assert anchor in text
    text=text.replace(anchor,anchor+"\nlocal progressFile=assert(io.open(OUTPUT..'progress.csv','w'));progressFile:write('frame,updates,x,y,engine,lives,camera\\n')")
    anchor=" wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])"
    assert anchor in text
    text=text.replace(anchor,anchor+"\n if wall%120==0 then progressFile:write(table.concat({wall,updates,world(),r('Player_Y_Position'),r('GameEngineSubroutine'),r('NumberofLives'),r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')},',')..'\\n');progressFile:flush()end")
    assert 'wall>=14000' in text;text=text.replace('wall>=14000','wall>=8000')
    prepare(O/'native',ROM,text,[Path(__file__),source,R/'tools/playthroughs/full_roster_policy_og.lua'],expected='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19',timeout=240,scope='Goku Hard controller-only current32slot menu, bounded8000frame discovery with compact120frame position log. No state writes. Fullstage success requires active1-2; timeout/failure is diagnostic only.',allow_interactive=True)
if __name__=='__main__':main()
