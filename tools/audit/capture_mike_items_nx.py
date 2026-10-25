"""Retain native StarTropics art evidence at the visible-world CHR mapping.

The original cartridge's existing debug-loader flag and explicit inventory/drop
arrangements make these source component fixtures, never campaign certificates.
Production ROMs, game sources and installed art are not modified.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-mike-art-nx')
NATIVE_SHA = 'ff20d5e9600565ae61e4eae6594c9f1e55e2a748a46bba0c88285140420a219a'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dungeon', type=int, choices=(0, 12), default=0)
    parser.add_argument('--run', default=None)
    args = parser.parse_args()
    out = OUT / (args.run or ('native-v1' if args.dungeon == 0 else 'native-d12-v2'))
    out.mkdir(parents=True, exist_ok=False)
    original = Path('C:/NES/StarTropics (USA).nes')
    raw = bytearray(original.read_bytes()); assert sha(original) == NATIVE_SHA
    address = 16 + 30 * 8192 + 1
    assert raw[address] == 0; raw[address] = 1
    rom = out / 'original-debug-fixture.nes'; rom.write_bytes(raw)
    old = (ROOT / 'build/mike-kd-private/original-weapons-d.lua').read_text()
    # Preserve all thirteen original setups/input timings. Add a continuous
    # mapping log: the old end-frame PPU read sees the later lower HUD banks.
    first = old.index('local f=0;'); last = old.index('local rows=')
    old = old[:first] + '''local f=0;local fixture=0;local reg=0;local ctrl=0
local regs={0,2,4,5,6,7,0,1}
local wr=assert(io.open(TEST_DIR..'mapper.csv','w'))
wr:write('frame,scanline,cycle,select,ctrl,r0,r1,r2,r3,r4,r5,r6,r7,palette\\n')
emu.addMemoryCallback(function(a,v)ctrl=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(a,v)reg=v end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(a,v)
 regs[(reg%8)+1]=v
 if f>=610 then
  local s=emu.getState();local c={}
  for i=0,15 do c[#c+1]=string.format('%02x',emu.read(0x3f10+i,emu.memType.nesPpuDebug))end
  wr:write(f..','..s['ppu.scanline']..','..s['ppu.cycle']..','..reg..','..ctrl..','..table.concat(regs,',')..','..table.concat(c)..'\\n')
 end
end,emu.callbackType.write,0x8001)
''' + old[last:]
    if args.dungeon == 12:
        # Native debug selector PRG25:B59A..B5D8 uses Down=-1; two
        # ordinary Down edges wrap the fourteen entries from 0 to 12.
        old = old.replace('right=f==100 or f==160 or f==590 or f==591,',
                          'down=(f>=280 and f<285)or(f>=340 and f<345),right=f==590 or f==591,')
        old = old.replace('a=f==400 or(f>=500 and f<520)',
                          'a=(f>=400 and f<405)or(f>=500 and f<520)')
        old = old.replace(' f=f+1', ''' f=f+1
 if f==402 then
  assert(emu.read(1,emu.memType.nesDebug)==7 and emu.read(2,emu.memType.nesDebug)==133,
   'Native dungeon12 must actually load7-1 before any inventory arrangement')
 end''')
    # Screenshots are the original emulator output. Preserve every frame of
    # the three primary attacks, rather than selecting one attractive moment.
    position = old.index(" if f>=610 and(f-610)%90==23")
    old = old[:position] + ''' if f>=610 and f<880 then
  local p=assert(io.open(TEST_DIR..'frame-'..f..'.png','wb'))
  p:write(emu.takeScreenshot());p:close()
 end
''' + old[position:]
    script = out / 'native.lua'; script.write_text(old)
    spec = importlib.util.spec_from_file_location('nx_mesen', ROOT / 'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    runner.ROOT = out
    result = runner.run(script, rom, timeout=55)
    assert result == 0, result
    for name in ('original-weapons-d.csv', 'mapper.csv'):
        path = out / name; raw = path.read_bytes()
        packed = path.with_suffix(path.suffix + '.gz')
        packed.write_bytes(gzip.compress(raw, mtime=0))
        assert gzip.decompress(packed.read_bytes()) == raw
        path.unlink()
    report = dict(original=dict(path=str(original), sha256=NATIVE_SHA),
                  component_ROM=dict(path=str(rom), sha256=sha(rom)),
                  only_ROM_change=dict(offset=address, old=0, new=1),
                  debug_dungeon_entry=args.dungeon,
                  script_sha256=sha(script), exit=result,
                  scope=__doc__, production_files_changed=False)
    (out / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
