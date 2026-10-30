"""Standalone mapper experiment for future roster code storage, never a game patch.

Tests executable 32KB PRG-RAM banking and a real CHR-to-RAM copy. It does not
allocate any shared-game memory or change the installed cartridge format.
"""
from pathlib import Path
import hashlib
import json
import subprocess

R=Path(__file__).resolve().parents[2]
O=R/'build/mmc5-overlay-lab-v1'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir(parents=True)
    payload=bytearray((i*29+13)&255 for i in range(1024))
    payload[:6]=bytes([0xa9,0x5a,0xa2,0xa5,0x38,0x60])
    chr_data=bytearray(1048576);chr_data[884*1024:885*1024]=payload
    (O/'test.chr').write_bytes(chr_data)
    header=bytes([0x4e,0x45,0x53,0x1a,2,128,0x50,0x08,0,0,9,0,0,0,0,0])
    (O/'header.bin').write_bytes(header)
    cfg='''MEMORY {
 HEADER: start=$0000,size=$10,type=ro,file=%O;
 ROM0: start=$8000,size=$2000,type=ro,file=%O,fill=yes,fillval=$ff,bank=0;
 ROM1: start=$a000,size=$2000,type=ro,file=%O,fill=yes,fillval=$ff,bank=1;
 ROM2: start=$c000,size=$2000,type=ro,file=%O,fill=yes,fillval=$ff,bank=2;
 FIXED: start=$e000,size=$2000,type=ro,file=%O,fill=yes,fillval=$ff,bank=3;
 CHR: start=0,size=$100000,type=ro,file=%O;
}
SEGMENTS {
 HEADER:load=HEADER,type=ro;
 CODE:load=FIXED,type=ro;
 VECTORS:load=FIXED,type=ro,start=$fffa;
 CHR:load=CHR,type=ro;
}
'''
    (O/'lab.cfg').write_text(cfg,newline='\n')
    source='''.setcpu "6502"
.macpack longbranch
.export LabStatus,LabStage,Reset
LabStatus=$6001
LabStage=$6002
.segment "HEADER"
.incbin "header.bin"
.segment "CODE"
Reset:
 sei
 cld
 ldx #$ff
 txs
 inx
 stx $2000
 stx $2001
 stx $4015
 lda #$40
 sta $4017
 lda #3
 sta $5100
 sta $5101
 lda #2
 sta $5102
 lda #1
 sta $5103
 lda #0
 sta $5113
 sta LabStatus
 sta LabStage
 lda #$83
 sta $5117
 lda #$80
 sta $5114
 lda #$b3
 sta $6000
 lda #$c7
 sta $7fff
 lda #1
 sta $5115
 lda #2
 sta $5116
 lda #$3c
 sta $c000
 lda #$77
 sta $a000
 cmp $c000
 jeq Fail
 lda #1
 sta LabStage
 ; PPU direct reads: render disabled, all12 bank latches agree on page884.
 lda #3
 sta $5130
 lda #$74
 ldx #11
MapChr:
 sta $5120,x
 dex
 bpl MapChr
 bit $2002
 lda #0
 sta $2006
 sta $2006
 lda $2007
 ldx #0
'''
    for page in range(4):
        source+=f'Copy{page}:\n lda $2007\n sta ${0xa000+page*256:04x},x\n inx\n bne Copy{page}\n'
    source+=''' lda #2
 sta LabStage
 bit $2002
 lda #0
 sta $2006
 sta $2006
 lda $2007
'''
    for page in range(4):
        source+=f'Compare{page}:\n lda $2007\n cmp ${0xa000+page*256:04x},x\n jne Fail\n inx\n bne Compare{page}\n'
    source+=''' lda #3
 sta LabStage
 jsr $a000
 cmp #$5a
 jne Fail
 cpx #$a5
 jne Fail
 jcc Fail
 ; Same physical RAM bank is executable through the C window as well.
 lda #1
 sta $5116
 jsr $c000
 cmp #$5a
 jne Fail
 cpx #$a5
 jne Fail
 jcc Fail
 lda #2
 sta $5116
 lda $c000
 cmp #$3c
 jne Fail
 lda #4
 sta LabStage
 lda $6000
 cmp #$b3
 jne Fail
 lda $7fff
 cmp #$c7
 jne Fail
 ; Write protection must preserve both the original state and loaded code.
 lda #0
 sta $5102
 lda #$ff
 sta $a000
 sta $6000
 lda $a000
 cmp #$a9
 jne Fail
 lda $6000
 cmp #$b3
 jne Fail
 lda #2
 sta $5102
 lda #$a5
 sta LabStatus
Done:jmp Done
Fail:
 lda #$e1
 sta LabStatus
 jmp Done
Interrupt:rti
.segment "VECTORS"
.word Interrupt,Reset,Interrupt
.segment "CHR"
.incbin "test.chr"
'''
    (O/'lab.s').write_text(source,newline='\n')
    ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
    commands=[[''+str(ca),'-g','-I',str(O),'-o',str(O/'lab.o'),str(O/'lab.s')],
        [str(ld),'-C',str(O/'lab.cfg'),'-Ln',str(O/'candidate.lbl'),'--dbgfile',str(O/'candidate.dbg'),
         '-o',str(O/'candidate.nes'),str(O/'lab.o')]]
    for cmd in commands:
        p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
    raw=(O/'candidate.nes').read_bytes()
    assert len(raw)==16+32768+1048576 and raw[:16]==header
    assert raw[16+32768+884*1024:16+32768+885*1024]==payload
    controller='''local frames=0
emu.addEventCallback(function()
 frames=frames+1
 local status=emu.read(0x6001,emu.memType.nesDebug)
 local stage=emu.read(0x6002,emu.memType.nesDebug)
 if status==0xa5 or status==0xe1 or frames>=60 then
  local passed=status==0xa5 and stage==4
  local f=assert(io.open(OUTPUT..'result.json','w'))
  f:write(string.format('{"passed":%s,"frames":%d,"status":%d,"stage":%d,"debug_RAM_writes":false}\\n',tostring(passed),frames,status,stage));f:close()
  emu.stop(passed and 0 or 1)
 end
end,emu.eventType.endFrame)
'''
    (O/'controller.lua').write_text(controller,newline='\n')
    paths=[Path(__file__).resolve(),O/'lab.s',O/'lab.cfg',O/'header.bin',O/'test.chr',O/'controller.lua',ca,ld]
    report=dict(prepared=True,native_run=False,standalone=True,shared_game_changed=False,
        ROM_sha256=sha(O/'candidate.nes'),PRG_ROM_bytes=32768,CHR_ROM_bytes=1048576,PRG_RAM_bytes=32768,
        code_source_CHR_page=884,copy_bytes=1024,executable_RAM_banks=[1],independent_data_RAM_banks=[0,2],
        native_checks=['Exact1024byte PPU-to-CPU copy including buffered-read discard','Execute same real6502 leaf through A/C windows',
            'Independent RAM0 persistent sentinels and RAM2 data','RAM write protection'],
        commands=commands,bindings={str(p):sha(p)for p in paths},
        primary_implementation_sources=['https://github.com/SourMesen/Mesen2/blob/master/Core/NES/Mappers/Nintendo/MMC5.h',
            'https://github.com/mist-devel/nes/blob/master/src/mappers/MMC5.sv'],
        limits=['Mapper experiment only; no allocation or shared-cartridge format change.',
            'Future loader needs actual interrupt/scroll/CHR restore, tagged RAM-bank farcalls and character-specific source integration.',
            'No physical-cartridge compatibility or installed-Mesen execution claim until tested.'])
    (O/'ready.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(prepared=True,ROM_sha256=report['ROM_sha256'])))


if __name__=='__main__':main()
