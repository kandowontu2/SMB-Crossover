"""Keep the Bell restoration assertion and retain its exact compared bytes."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.mkdir(exist_ok=False);rom=a.rom.resolve()
 body=(ROOT/'tests/parodius-bells.lua').read_text();needle="  assert(colors()==paletteBefore,'Super Bomb restores every captured palette color')"
 assert body.count(needle)==1
 diagnostic=r"""  local function hex(s)return(s:gsub('.',function(c)return string.format('%02x',string.byte(c))end))end
  local shadow={};for i=0,31 do shadow[#shadow+1]=string.char(r('PnBombPaletteShadow',i))end
  local f=assert(io.open(OUTPUT..'palette-compare.txt','w'));f:write('expected='..hex(paletteBefore)..'\nactual='..hex(colors())..'\nshadow='..hex(table.concat(shadow))..'\nclock='..r('VvClock')..' queue='..r('VRAM_Buffer1_Offset')..'\n');f:close()
"""
 script=out/'bells-diagnostic.lua';script.write_text('PN_VARIANT=2\n'+(ROOT/'tests/parodius-integration.lua').read_text().split('local pulses=')[0]+body.replace(needle,diagnostic+needle))
 s=importlib.util.spec_from_file_location('palette_ns',ROOT/'tools/run_mesen.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);r.ROOT=out
 code=r.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 receipt=dict(exit=code,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),assertion_preserved=True)
 (out/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
