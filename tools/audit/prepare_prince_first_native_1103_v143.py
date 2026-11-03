"""Observe actual long Prince cold handoff; retain fixed360-frame142 negative."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_first_native_1103_v139 as V
from prepare_selected_native_packet_v1 import prepare,sha
O=V.O


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['controls','contact-death'],default='controls');a=ap.parse_args()
 previous=O/f'native-first-{a.mode}-v142';ready=json.loads((previous/'ready.json').read_text());body=(previous/'controller.lua').read_text();assert sha(V.ROM)==ready['ROM_sha256']
 base,_=V.C.image();bank=V.C.I.address(base,'CurrentBank');bankC=V.C.I.address(base,'CurrentBankC')
 diagnostic=r'''local function handoffBoundary(tag)
 local s=emu.getState();local h2,h3={},{}
 for i=0,15 do h2[#h2+1]=string.format('%02x',ps(0x1fe0+i,2));h3[#h3+1]=string.format('%02x',ps(0x1fe0+i,3))end
 local prefix={};for i=0,15 do prefix[#prefix+1]=string.format('%02x',ps(0x100+i,2))end
 local f=assert(io.open(OUTPUT..tag..'.json','w'))
 f:write(string.format('{"frame":%d,"game_age":%d,"OperMode":%d,"task":%d,"menu":%d,"engine":%d,"selected":%d,"lives":%d,"source_ready":%d,"source_HP":%d,"CPU_PC":%d,"CPU_SP":%d,"A_bank":%d,"C_bank":%d,"RAM2_header":%q,"RAM3_header":%q,"cold_C100_prefix":%q,"source_updates":%d,"source_init_calls":%d,"controller_only":true}\n',frame,age,r('OperMode'),r('OperMode_Task'),r('CrossoverMenuState'),r('GameEngineSubroutine'),r('SelectedCharacter'),r('NumberofLives'),ps(0xab),ps(0x6cf),s['cpu.pc'],s['cpu.sp'],ram(BANK_ADDRESS),ram(BANK_C_ADDRESS),table.concat(h2),table.concat(h3),table.concat(prefix),sourceUpdates,initCalls));f:close()
end
'''.replace('BANK_C_ADDRESS',str(bankC)).replace('BANK_ADDRESS',str(bank))
 anchor="local log=assert(io.open(OUTPUT..'observations.csv','w'))";assert body.count(anchor)==1;body=body.replace(anchor,diagnostic+'\n'+anchor)
 old=" elseif phase=='game'and age>=360 then\n";assert body.count(old)==1
 new=""" elseif phase=='game'then
  if age==360 then handoffBoundary('handoff-age360');if Q.controlMode=='controls'then shot('handoff-age360')end end
  if age==1199 then handoffBoundary('handoff-last')end
  assert(age<1200,'Bounded actual Prince cold/native stage handoff')
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('CrossoverMenuState')==0 and r('SelectedCharacter')==38 and r('GameEngineSubroutine')==8 and ps(0xab)==0xa7 then
""";body=body.replace(old,new)
 old="  controls_begin()\n elseif phase=='controls'";assert body.count(old)==1;body=body.replace(old,"  handoffBoundary('handoff-active');controls_begin()\n  end\n elseif phase=='controls'")
 for bad in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in body
 refs={Path(__file__),previous/'controller.lua',previous/'ready.json',*[Path(p)for p in ready['bindings']]}
 prepare(O/f'native-first-{a.mode}-v143',V.ROM,body,refs,expected=ready['ROM_sha256'],timeout=240,scope=ready['scope']+' Distinct143 records actual native task/menu/engine/ready/fullheaders/maps/PC/SP atgameage360, permits bounded1200actualhandoff frames, then retains strict original assertions. Controls-only may add one boundaryPNG; contact mode keeps existing4PNGcap. No RAM/mapper/outcome writes.')


if __name__=='__main__':main()
