"""Deliver the performance successor with the same earned-pickup verification."""
import json
from pathlib import Path
from types import SimpleNamespace
import deliver_getsu_callback_1110 as D
import check_getsu_native_head_direct_1110 as Q
import prepare_getsu_earned_powerups_1110 as G
from prepare_selected_native_packet_v1 import prepare,sha

PIN='66a7b9325d90efb7751387e0c1c95a756fde57d92f13d6180178ade3e535090c'
PROOF=Q.R/'build/getsu-native-head-direct-1110/proof.json'
NATIVE=Q.R/'build/getsu-fast-head-native-1110'

def qualified(rom):
 q=json.loads(PROOF.read_text());assert q['passed'] and q['parent_SHA256']==Q.PIN and q['expected_memory_only_SHA256']==PIN
 assert len(q['patches'])==1 and len(q['cuts'])==6 and q['cases']
 for name,h in q['bindings'].items():assert sha(Q.R/name)==h,name
 raw=bytearray(Q.BASE.read_bytes());assert Q.G.Q.sha(raw)==Q.PIN
 for row in q['patches']:
  at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
  assert len(old)==len(new)==80 and raw[at:at+80]==old;raw[at:at+80]=new
 assert Q.G.Q.sha(raw)==PIN and rom.read_bytes()==raw
 idle=D.packet_result(NATIVE/'idle',NATIVE/'candidate.nes',PIN)
 assert idle['idle_main_updates']==idle['active_frames']==120 and idle['idle_without_main']==0 and idle['missed_reads']<=2
 return bytes(raw)

def stage_packet(out,rom,mode):
 old=NATIVE/mode;source=(old/'controller.lua').read_text()
 D.packet_result(old,NATIVE/'candidate.nes',PIN)
 prepare(out,rom,source,{Path(__file__),PROOF,old/'controller.lua',old/'capture/result.json'},
   expected=PIN,timeout=240,allow_interactive=True,rom_symbols=G.D.SYMBOLS,
   scope='Exact tested '+mode+' controller in actual Downloads after native head optimization.')

D.PIN=PIN;D.PROOF=PROOF
D.Q=SimpleNamespace(PIN=Q.PIN,BASE=Q.BASE)
D.qualified=qualified;D.stage_packet=stage_packet
if __name__=='__main__':D.main()
