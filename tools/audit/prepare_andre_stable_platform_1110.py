"""Observe endpoint turns at completed GameLoops, not mid-render frame edges."""
import argparse
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha,R
import prepare_manual_dual_native_1110 as P


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=R/'build/manual-roster-native-1110';old=root/'wwf-v2/29-5';rom=root/'candidate.nes'
 source=(old/'controller.lua').read_text();assert source.count('local function snapshot()')==1
 source=source.replace('local function snapshot()','local function readSnapshot()',1)
 wrapper='''local stable=nil;local endpoints={}
local function copy(t)if type(t)~='table'then return t end;local r={};for k,v in pairs(t)do r[k]=copy(v)end;return r end
local function snapshot()return copy(stable or readSnapshot())end
'''
 source=source.replace('local function json(v)',wrapper+'local function json(v)',1)
 source=source.replace('births[#births+1]=snapshot()','births[#births+1]=readSnapshot()',1)
 source=source.replace('then updates=updates+1 end',
 '''then
  updates=updates+1;stable=readSnapshot()
  local h=stable.horizontal[1]
  if h and(h.travelled==0 or h.travelled==112)then endpoints[#endpoints+1]=copy(stable)end
 end''',1)
 source=source.replace('local before=snapshot();local last=before.horizontal[1].x;local carried=0',
  'local before=snapshot();local last=before.horizontal[1].x;local carried=0;local since=updates',1)
 needle="local s=snapshot();local h=s.horizontal[1]\n   assert(h and h.x>=startX"
 assert source.count(needle)==1
 source=source.replace(needle,'''local s=snapshot();local h=s.horizontal[1]
   for _,point in ipairs(endpoints)do
    if point.updates>since and point.horizontal[1].x==goal then
     local endpoint=copy(point);endpoint.name=name;endpoint.carry_updates=carried;endpoint.viewport_clipped=viewportClipped
     assert(endpoint.lives==2 and #endpoint.horizontal==1 and #endpoint.vertical<=1,'Invalid native endpoint')
     assert(carried>=(minimum or 6),'Insufficient native carry at observed completed-loop endpoint')
     samples[#samples+1]=endpoint;return endpoint
    end
   end
   assert(h and h.x>=startX''',1)
 symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg'))
 prepare(a.output,rom,source,{Path(__file__),old/'controller.lua',old/'capture/result.json'},expected=sha(rom),
  timeout=180,allow_interactive=True,rom_symbols=symbols,
  scope='Same Andre natural input and all112px/carry assertions; native endpoint turns sampled at genuine completed GameLoop boundaries to avoid lost endpoints when a video frame spans multiple updates.')


if __name__=='__main__':main()
