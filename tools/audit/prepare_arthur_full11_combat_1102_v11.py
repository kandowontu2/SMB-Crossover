"""Bound Arthur's stop-and-fire attempt, then evade a surviving real enemy."""
from pathlib import Path
import argparse
from prepare_selected_native_packet_v1 import R, prepare, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(exist_ok=True)
    ref = R / 'build/arthur-side-clamp-1101-v8/full11-near/controller.lua'
    text = ref.read_text()
    old = 'if age-combatStart<180 then b.right=false;return b end'
    assert text.count(old) == 1
    text = text.replace(old, 'if age-combatStart<60 then b.right=false;return b end\n   threat=true', 1)
    # Log actual actors instead of inferring a cause from the final body pose.
    text = text.replace("injuryLog:write('frame,x,y,source_flags,mode,engine\\n')",
                        "injuryLog:write('frame,x,y,source_flags,mode,engine\\n')\n"
                        "local actors=assert(io.open(OUTPUT..'actors.csv','w'))\n"
                        "actors:write('frame,player_x,player_y,slot,id,x,y,state,flag\\n')", 1)
    text = text.replace(' injuryLog:close()\n', ' injuryLog:close();actors:close()\n', 1)
    marker = '  if age%12==0 then row() end'
    assert text.count(marker) == 1
    text = text.replace(marker, marker + '''
  if age%36==0 or r('GameEngineSubroutine')==11 then
   for i=0,5 do
    if r('Enemy_Flag',i)>0 then
     actors:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d\\n',frame,x,y,i,r('Enemy_ID',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_State',i),r('Enemy_Flag',i)))
    end
   end
  end''', 1)
    prepare(a.output / 'native', a.rom, text, [Path(__file__), ref],
            expected=sha(a.rom), timeout=240, allow_interactive=True,
            scope='Same actual-menu all4pipes/3gaps/actual1-2 no-life-loss route, '
                  'but stop/fire60physicalframes then jump a surviving actual '
                  'enemy. Read-only sparse actor log; no emulated writes, '
                  'physics changes, cheats or helper platforms. All earlier '
                  'negative receipts retained.')


if __name__ == '__main__':
    main()
