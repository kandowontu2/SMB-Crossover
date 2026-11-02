"""Bounded observer of the unchanged failing Andre route near first-pit landing."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    source=O/'native-andre3/controller.lua';text=source.read_text()
    marker='local function nearest()'
    assert text.count(marker)==1
    text=text.replace(marker,"local contactRows,lastContact=0,-1\nlocal contactFile=assert(io.open(OUTPUT..'contact.csv','w'))\ncontactFile:write('update,player_x,player_y,state,cooldown,jumping,slot,flag,id,enemy_x,enemy_y,enemy_state\\n')\n"+marker)
    marker='  local danger=nearest()'
    insert="""
  if x>=1136 and x<=1220 and updates~=lastContact and contactRows<180 then
   lastContact=updates;contactRows=contactRows+1
   for i=0,5 do
    contactFile:write(string.format('%d,%d,%d,%d,%d,%s,%d,%d,%d,%d,%d,%d\\n',updates,x,y,r('Player_State'),cooldown,tostring(jumping),i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i),r('Enemy_Y_Position',i),r('Enemy_State',i)))
   end
   contactFile:flush()
  end
"""
    assert text.count(marker)==1;text=text.replace(marker,marker+insert)
    rom=O/'candidate2.nes'
    prepare(O/'native-andre-contact',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Read-only compact contact observer, max180 updates/1080CSV rows, unchanged failing Andre3 controls. Negative expected; diagnose first-pit enemy approach without ROM or physics changes.')
if __name__=='__main__':main()
