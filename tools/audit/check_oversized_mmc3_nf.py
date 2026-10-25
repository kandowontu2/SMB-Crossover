"""Prove 8-bit MMC3 PRG banking on installed Mesen; audit full-roster storage.

The generated ROM is a standalone mapper diagnostic, not an SMB port. Real CPU
instructions write/read mapper banks. Lua only observes its result in RAM.
"""
from pathlib import Path
import hashlib, json, subprocess, sys

R = Path(__file__).resolve().parents[2]
O = R/'build/verification/mmc3-oversized-feasibility-nf'
O.mkdir(parents=True, exist_ok=False)
sha = lambda b: hashlib.sha256(b).hexdigest()
raw = (R/'build/smb-crossover-mmc5-expanded.nes').read_bytes()
assert len(raw) == 2097168
budget = json.loads((R/'build/verification/mmc3-full-roster-feasibility-ne/measurements.json').read_text())

# Preserve all existing non-empty program banks and the entire uncompressed
# CHR image in an addressable proposed layout. This is data capacity proof,
# not executable mapper conversion. The fixed banks move to FE/FF.
prg = raw[16:16+1048576]
chr_data = raw[16+1048576:]
assert all(b == 255 for b in prg[100*8192:126*8192]), 'Review newly occupied banks before assigning graphics'
container = bytearray([255])*2097152
container[:100*8192] = prg[:100*8192]
container[100*8192:228*8192] = chr_data
container[254*8192:] = prg[126*8192:]
assert container[:100*8192] == prg[:100*8192]
assert container[100*8192:228*8192] == chr_data
assert container[254*8192:] == prg[126*8192:]

source = ['.segment "CODE"', 'Reset:', 'sei', 'cld', 'ldx #$ff', 'txs',
          'lda #0', 'sta $2000', 'sta $2001', 'sta $e000', 'sta $0002', 'lda #$80', 'sta $a001']
cases = [(0x06, 0x8000, 0xc000), (0x07, 0xa000, 0xc000),
         (0x46, 0xc000, 0x8000), (0x47, 0xa000, 0x8000)]
for index, (selector, window, fixed) in enumerate(cases):
    source += [f'lda #{index}', 'sta $0001', f'lda #${selector:02x}', 'sta $8000', 'ldx #0', f'Loop{index}:',
               'stx $8001', f'cpx ${window:04x}', f'beq FirstOK{index}', 'jmp Fail', f'FirstOK{index}:',
               'txa', 'eor #$a5', f'cmp ${window+1:04x}', f'beq SecondOK{index}', 'jmp Fail', f'SecondOK{index}:',
               f'lda ${fixed:04x}', 'cmp #$fe', f'beq FixedOK{index}', 'jmp Fail', f'FixedOK{index}:',
               'lda $e000', 'cmp #$ff', f'beq LastOK{index}', 'jmp Fail', f'LastOK{index}:',
               'inx', f'bne Loop{index}']
source += ['lda #1', 'sta $0002', 'Done:jmp Done', 'Fail:stx $0000', 'lda #$ff', 'sta $0002', 'jmp Done']
(O/'probe.s').write_text('\n'.join(source)+'\n')
(O/'probe.cfg').write_text('MEMORY { CODE: start=$e100,size=$1e00,file=%O; }\nSEGMENTS { CODE:load=CODE,type=ro; }\n')
compiler = R/'tools/Windows/cc65/bin/cl65.exe'
result = subprocess.run([str(compiler), '-t', 'none', '-C', str(O/'probe.cfg'), '-o', str(O/'probe.bin'), str(O/'probe.s')], cwd=R, capture_output=True, text=True)
(O/'compile.log').write_text(result.stdout+result.stderr)
assert result.returncode == 0, result.stderr
diagnostic = bytearray([234])*2097152
for bank in range(256):
    diagnostic[bank*8192:bank*8192+4] = bytes([bank, bank^0xa5, bank^255, 0x42])
code = (O/'probe.bin').read_bytes()
assert len(code)<0x1efa
diagnostic[255*8192+256:255*8192+256+len(code)] = code
diagnostic[-6:] = bytes([0,0xe1])*3
# NES2, mapper4, 2MiB PRG, no CHR-ROM, 8KiB PRG-RAM, 32KiB CHR-RAM.
header = bytes([78,69,83,26,128,0,0x41,8,0,0,7,9,0,0,0,0])
rom = O/'oversized-mmc3-banking-diagnostic.nes'
rom.write_bytes(header+diagnostic)
(O/'observe.lua').write_text('''
local frame=0
emu.addEventCallback(function()
 frame=frame+1
 local status=emu.read(2,emu.memType.nesDebug)
 if status==255 then error('Bank failed mode '..emu.read(1,emu.memType.nesDebug)..' bank '..emu.read(0,emu.memType.nesDebug))end
 if status==1 then
  local f=assert(io.open(TEST_DIR..'native-result.json','w'))
  f:write('{"passed":true,"PRG_banks":256,"banking_cases":1024,"PRG_modes":2,"CPU_mapper_writes":true,"Lua_emulated_writes":false,"scope":"Standalone banking diagnostic, not a game port or flash-cartridge certification"}')
  f:close();print('PASS full8-bit MMC3 PRG banking in both modes');emu.stop(0)
 end
 assert(frame<20,'Diagnostic timeout')
end,emu.eventType.endFrame)
''')
command = [sys.executable, str(R/'tools/audit/run_mesen_isolated.py'), '--output', str(O), str(O/'observe.lua'), str(rom), '--timeout','20',
           '--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
result = subprocess.run(command, cwd=R, capture_output=True, text=True)
(O/'host.log').write_text(result.stdout+result.stderr)
assert result.returncode == 0, result.stdout+result.stderr
native = json.loads((O/'native-result.json').read_text())
linked = budget['full']['PRG_linked_segment_bytes']
report = dict(passed=native['passed'], full_roster_ROM_sha256=sha(raw), native_banking=native,
    diagnostic_ROM_sha256=sha(rom.read_bytes()), executable_game_port=False,
    PRG_capacity_bytes=2097152, current_linked_PRG_bytes=linked,
    all_existing_CHR_bytes=len(chr_data), linked_plus_entire_raw_CHR_bytes=linked+len(chr_data),
    aggregate_headroom_bytes=2097152-linked-len(chr_data),
    proposed_layout=dict(code_banks=[0,99], raw_graphics_banks=[100,227],
        fixed_code_banks=[254,255], completely_free_banks=[228,253],
        completely_free_bank_bytes=26*8192, source_nonempty_program_banks_preserved_exactly=True,
        source_entire_CHR_preserved_exactly=True, proposed_container_sha256=sha(container)),
    caveats=['PRG capacity proof and installed-emulator banking proof only; not a playable converted ROM.',
        'Oversized PRG banking does not extend 8-bit CHR-bank address width. This plan uses banked CHR-RAM.',
        'Graphics upload/cache timing, ExRAM relocation, all bank-switch/IRQ adaptations and audio fallback remain implementation work.',
        '32KiB CHR-RAM is declared in the diagnostic header, but no CHR-RAM cache or broad compatibility test is claimed.',
        'Physical flash-cartridge compatibility depends on its mapper implementation/firmware.'])
(O/'proof.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
