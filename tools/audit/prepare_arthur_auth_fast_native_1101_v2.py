"""Prepare the unchanged Arthur controller on the optimized candidate."""
from pathlib import Path
import json
import prepare_arthur_auth_fast_1101_v2 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 ref=P.R/'build/arthur-idle-profile-1101-v1/native/controller.lua'
 text=ref.read_text();q=json.loads((P.O/'assembly.json').read_text())
 old='emu.addMemoryCallback(authReturn,emu.callbackType.exec,51170)'
 assert text.count(old)==1
 text=text.replace(old,f'emu.addMemoryCallback(authReturn,emu.callbackType.exec,{q["auth_restore"]+8})')
 prepare(P.O/'native',P.O/'candidate.nes',text,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=120,scope='Same cold Arthur idle/walk controller as current baseline. Only read-only auth-return PC follows compiled relocation. Full Main/auth elapsed cycles include interrupts.2PNGs; no state writes.')
if __name__=='__main__':main()
