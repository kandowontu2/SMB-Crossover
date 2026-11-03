"""Align both original source head probes with the actual first question block."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-head-earned-alignment-1103-v83'
PIN='cc7b9bddfd39c62fadb5c1afc34bc82361432eab5a8a8e5b5a18bde184813a4e'

def main():
    O.mkdir(exist_ok=True)
    for identity in ['bub','bob']:
        source=R/f'build/bub-head-root-candidate-1103-v81/{identity}-mushroom/controller.lua'
        text=source.read_text()
        # Mario's native center probe accepts X329..332. The original source
        # tests X+4 first, then X+12: at X330 it first sees the adjacent brick
        # at320..335. X337..339 puts both authentic probes into336..351.
        for before,after in [('x<329,left=x>332','x<337,left=x>339'),('x>=329 and x<=332','x>=337 and x<=339')]:
            assert text.count(before)==1;text=text.replace(before,after)
        needle='local upgrade_attempts=0';assert text.count(needle)==1
        text=text.replace(needle,needle+'''
local upgrade_diag=assert(io.open(OUTPUT..'upgrade.csv','w'))
upgrade_diag:write('Main,phase,x,y,dy,native_state,source_state,held,item_state,item_x,flags,engine,block320,block336,block352,head_left,head_right\\n')
''')
        needle='  upgrade_last=q.completed_Main;upgrade_age=upgrade_age+1';assert text.count(needle)==1
        text=text.replace(needle,needle+'''
  local _,b0=full_solid(324,144);local _,b1=full_solid(340,144);local _,b2=full_solid(356,144)
  local _,bl=full_solid(x+4,144);local _,br=full_solid(x+12,144)
  upgrade_diag:write(table.concat({q.completed_Main,upgrade_phase,x,y,ram(142),r('Player_State'),full_state((Q.launch.bob==1 and 0x42 or 0x2e)+3),full_state(0x301),item and item.state or -1,item and item.x or -1,flags,engine,b0,b1,b2,bl,br},',')..'\\n');upgrade_diag:flush()
''')
        rom=R/'build/bub-head-root-candidate-1103-v81/bub-source-head.nes'
        prepare(O/f'{identity}-mushroom',rom,text,[Path(__file__),source,R/'build/bub-head-root-candidate-1103-v81/candidate.json'],expected=PIN,timeout=180,allow_interactive=True,scope='Private probe only; remaining nested IRQ qualification pending. Same cc7b source contact body. Correct controller X337..339 aligns both actual source X+4/X+12 probes inside first question block336..351, instead of native Mario center-only329..332 which first hits adjacentbrick. Retain bounded3bump/no-death/real immature+mature item/ownflags01/native animation assertions. One bounded aggregate CSV; no extra images or memory writes.')

if __name__=='__main__':main()
