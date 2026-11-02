from pathlib import Path
import prepare_tank_walk_modes_1101_v32 as N
from prepare_selected_native_packet_v1 import sha

def main():
 N.O=N.R/'build/tank-normal-walk-1101-v33';original=N.prepare
 def prepare(output,rom,controller,refs,**kw):
  rom=N.O/'candidate.nes';kw['expected']=sha(rom)
  return original(output,rom,controller,[*refs,Path(__file__),N.R/'tools/audit/prepare_tank_normal_walk_1101_v33.py'],**kw)
 N.prepare=prepare;N.main()
if __name__=='__main__':main()
