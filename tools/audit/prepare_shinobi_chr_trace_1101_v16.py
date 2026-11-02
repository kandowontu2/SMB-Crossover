"""Small read-only mapper/OAM snapshot on the real cold controller replay."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_shinobi_probes_1101_v16 as P

def main():
 c=(P.O/'native-smoke/controller.lua').read_text()
 observer="""local function dump()
 local f=assert(io.open(OUTPUT..'graphics.txt','w'))
 for _,n in ipairs({'CurrentCHRBank','X5ChrMode','SsChrActive','X5WideChrActive','ReloadCHRBank','CurrentOAMOffset','Mirror_PPUCTRL'}) do
  f:write(n..': ')
  for i=0,((n=='CurrentCHRBank' or n=='X5ChrMode') and 11 or 0) do f:write(string.format('%02x ',emu.read(L[n]+i,emu.memType.nesDebug))) end
  f:write('\n')
 end
 for a=0x200,0x23f do f:write(string.format('%02x ',emu.read(a,emu.memType.nesDebug))) end
 f:close()
end
""".replace("'\n'","'\\n'")
 c=c.replace('local function shot',observer+'local function shot',1).replace("shot('walking');","shot('walking');dump();")
 prepare(P.O/'native-chr-trace',P.O/'candidate.nes',c,[Path(__file__)],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Read-only end-frame CHR publication state and64 OAM bytes; same three screenshots, no state writes.')

if __name__=='__main__':main()
