"""Bind the two actual RTI opcodes and qualify fixed-bank vector callbacks."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/thomas-full11-1102-v1'
def main():
    source=O/'native-symbols/controller.lua';text=source.read_text()
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes';raw=rom.read_bytes()
    assert raw[1032272:1032276]==bytes.fromhex('68aa6840')
    assert raw[1041434:1041440]==bytes.fromhex('68a868aa6840')
    text='L=L or {};L.IrqScrollSplit_RTI=0x8043;L.NonMaskableInterrupt_RTI=0xe40f\n'+text
    marker=" local leave=kind=='NMI'and L.NonMaskableInterrupt_RTI or L.IrqScrollSplit_RTI"
    assert text.count(marker)==1
    text=text.replace(marker,marker+"\n assert(entry and leave,'Explicit vector callback addresses')\n local function vectorBank(pc)local a=emu.convertAddress(pc);return a and a.memType==emu.memType.nesPrgRom and a.address//8192==(kind=='NMI'and 127 or 126)end")
    text=text.replace("  if active()or lastMain or#isrs>0 then","  if vectorBank(entry) and (active()or lastMain or#isrs>0) then",1)
    text=text.replace("  if#isrs>0 then local q=table.remove(isrs);local s=emu.getState()","  if vectorBank(leave) and #isrs>0 then local q=table.remove(isrs);local s=emu.getState()",1)
    prepare(O/'native-vectors',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Repair observer-only nil RTI aliases which registered nonspecific exec callbacks. Exact current RTI bytes and physical banks required; all existing stack/AXY/SMC and fullstage assertions retained.')
if __name__=='__main__':main()
