"""Keep near obstacles visible after a source injury cancels a pending jump."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_excitebike_dispatch_1101_v1 import O


def main():
    old=O/'full11-v3';q=json.loads((old/'capture/result.json').read_text())
    assert not q['passed']and q['third_pipe_top_support']and q['initial_four_pipes_passed']==3
    text=(old/'controller.lua').read_text()
    before='  local obstacle=solid(x+68,math.min(232,y+28))or solid(x+68,y+12)\n  local gap=not solid(x+52,216)'
    after='''  local obstacle,gap=false,false
  for _,offset in ipairs({16,32,48,68})do
   if solid(x+offset,math.min(232,y+28))or solid(x+offset,y+12)then obstacle=true end
  end
  for _,offset in ipairs({12,28,44,52})do if not solid(x+offset,216)then gap=true end end'''
    assert text.count(before)==1;text=text.replace(before,after)
    rom=O/'current4.nes';pin='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
    prepare(O/'full11-v4',rom,text,[Path(__file__),old/'controller.lua',old/'capture/result.json',O/'current4-composition.json'],
            expected=pin,timeout=240,allow_interactive=True,
            scope='Same source-qualified/native-controls+cooldown-passing ROM and v3 fullstage inputs/policies. Concrete controller repair: scan near/middle/far terrain and pit samples so an injury-cancelled jump is retried beside a32pxwide pipe, rather than looking68px beyond it. Existing genuine windup/lean/turbo duty, progressing-cooldown deadlines, no-life-loss/active1-2 assertions and4PNG cap retained. No writes/helpers/ROM changes; third64pxtop already genuinely supported in priornegative.')


if __name__=='__main__':main()
