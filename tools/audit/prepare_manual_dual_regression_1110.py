"""Bind unchanged Mini full1-1 and Getsu earned-powerup regression inputs."""
import argparse,re
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_manual_dual_native_1110 as P

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--proof',type=Path,required=True);a=p.parse_args()
 raw=a.rom.read_bytes();digest=sha(a.rom)
 old=P.R/'build/getsu-current-regression-1110/mini';source=(old/'controller.lua').read_text()
 oldpin='095c164a574479401f284c1669264034404b83cb2e1d6cdc4a1f5ef37dcafe79'
 oldkernel=re.search(r'\["kernel_SHA256"\]="([0-9a-f]{64})"',source)[1]
 start=16+128*8192+962*1024;kernel=raw[start:start+5120]
 import hashlib
 for pc,physical,kind,values in re.findall(r'\["pc"\]=(\d+),\["physical"\]=(\d+),\["memory"\]="(nesWorkRam|nesPrgRom)",\["bytes"\]=\{([\d,]+)\}',source):
  pc,physical=int(pc),int(physical);expected=bytes(map(int,values.split(',')))
  data=kernel[pc-0xa000:pc-0xa000+len(expected)] if kind=='nesWorkRam' else raw[16+physical:16+physical+len(expected)]
  assert data==expected,(hex(pc),kind)
 assert source.count(oldpin)==source.count(oldkernel)==1
 source=source.replace(oldpin,digest).replace(oldkernel,hashlib.sha256(kernel).hexdigest())
 refs={Path(__file__),a.proof,old/'controller.lua',old/'capture/result.json'}
 a.output.mkdir(exist_ok=True)
 symbols=(P.Old.SYMBOL_BASE.with_suffix('.lbl'),P.Old.SYMBOL_BASE.with_suffix('.dbg'))
 prepare(a.output/'mini',a.rom,source,refs,expected=digest,timeout=180,allow_interactive=True,rom_symbols=symbols,
  scope='Unchanged normal Mini1-1 route, exact public observer PCs/bytes, new source-bound kernel digest.')
 prior=P.R/'build/getsu-fast-head-native-1110/powerup';source=(prior/'controller.lua').read_text()
 oldpin='66a7b9325d90efb7751387e0c1c95a756fde57d92f13d6180178ade3e535090c';assert source.count(oldpin)==1
 prepare(a.output/'getsu',a.rom,source.replace(oldpin,digest),{Path(__file__),a.proof,prior/'controller.lua',prior/'capture/result.json'},
  expected=digest,timeout=180,allow_interactive=True,rom_symbols=symbols,scope='Unchanged Getsu real mushroom/flower pickup and recovery regression.')

if __name__=='__main__':main()
