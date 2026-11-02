"""Unchanged failed terrain controller against the installed baseline."""
from pathlib import Path
import json
import prepare_arthur_auth_fast_1101_v2 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 ref=P.O/'terrain/controller.lua';text=ref.read_text()
 q=json.loads((P.O/'assembly.json').read_text())
 old=f'emu.addMemoryCallback(authReturn,emu.callbackType.exec,{q["auth_restore"]+8})'
 assert text.count(old)==1;text=text.replace(old,'emu.addMemoryCallback(authReturn,emu.callbackType.exec,51170)')
 prepare(P.O/'terrain-baseline',P.BASE,text,[Path(__file__),ref],expected=sha(P.BASE),timeout=150,scope='Exactly same first-pipe controller as failed candidate terrain. Only read-only auth-return PC follows baseline. Distinguish preexisting/control issue from optimization regression.')
if __name__=='__main__':main()
