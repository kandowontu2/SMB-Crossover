"""Clear both projectile shadow columns in one pass on the delivered MMC5 ROM."""
import argparse
import json
from pathlib import Path
import subprocess

import measure_mini_parser_health_batch_1108_v2 as B


R = B.R
BASE = R/'build/mini-busy-pipeline-final-1108/candidate.nes'
PIN = '37bb9c1a69b993edda540c75cbe256aeac75396d55d34d9daf3d4de86deebeeb'
FIXED = 16 + 126*8192 + 0x1076
LEVEL = 16 + 2*8192 + 0x1fdd
FIXED_BEFORE = bytes.fromhex(
    'd004a8e00d60a25da95120b490a25ea9f120b490a263a9d120c790a200a000e00b900a'
    'bd7168f009dda104f00118a9002a910b98186910a8e8e00d90e26020c790a0c0a900'
    '38910b98e910a8a900b0f6606509850b8a650a850c60ea')
LEVEL_BEFORE = b'\xff'*18


def source():
    fixed = B.SOURCE.split('.segment "FIXED"\n',1)[1]
    first = fixed.index(' ldx #>(MmCoinHits-Block_Buffer_1)')
    last = fixed.index(' ldx #>(MmSolidTerrain-Block_Buffer_1)')
    fixed = fixed[:first]+''' ; The parser's last row stored $c0 in R0. Save R1 across the two pointers.
 lda R1
 pha
 lda M0
 clc
 adc #<(MmCoinHits-MmBrickHealth)
 sta R0
 lda M1
 adc #>(MmCoinHits-MmBrickHealth)
 sta R1
 jsr ClearBothColumns
 pla
 sta R1
 lda #$c0
 sta R0
'''+fixed[last:]
    fixed = fixed.replace('jsr PrepareAndClearColumn','jsr ColumnPointer')
    first = fixed.index('PrepareAndClearColumn:\n')
    last = fixed.index('ColumnPointer:\n',first)
    fixed = fixed[:first]+fixed[last:]
    return '''.setcpu "6502"
.segment "FIXED"
'''+fixed+'''
.segment "LEVEL_TAIL"
ClearBothColumns:
 ldy #$c0
 lda #0
 sec
ClearRow:
 sta (M0),y
 sta (R0),y
 tya
 sbc #16
 tay
 lda #0
 bcs ClearRow
 rts
.assert *-ClearBothColumns=18,error,"Bounded bank 2 tail"
'''


def assemble(out,b):
    src=out/'parser-dual.s'
    cfg=src.with_suffix('.cfg')
    obj=src.with_suffix('.o')
    fixed,level=out/'fixed.bin',out/'level.bin'
    names=(*B.A.NAMES,'R0','R1')
    src.write_text(''.join(f'{n}=${B.A.address(b,n):04x}\n' for n in names)+source())
    cfg.write_text(f'MEMORY{{F:start=$9076,size=92,file="{fixed.as_posix()}";'
                   f'L:start=$bfdd,size=18,file="{level.as_posix()}";}}\n'
                   'SEGMENTS{FIXED:load=F,type=ro;LEVEL_TAIL:load=L,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',out/'linked.bin'],check=True)
    obj.unlink()
    return fixed.read_bytes(),level.read_bytes()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=BASE.read_bytes()
    assert B.sha(raw)==PIN
    old=B.A.bundle(raw)
    # The existing column tail is the only ingress and owns the mapped bank 2.
    assert raw[16:1048592].count(bytes.fromhex('4c7690'))==1
    assert raw[16:1048592].count(bytes.fromhex('207690'))==0
    end=16+2*8192+0x1fef
    bank2=[s for s in old['segs'].values() if s.get('ooffs') and 16400<=int(s['ooffs'],0)<24592]
    assert sorted((int(s['ooffs'],0),int(s['size'],0)) for s in bank2)==[(16400,0x1fdd),(end,15)]
    args.output.mkdir(exist_ok=True)
    fixed,level=assemble(args.output,old)
    raw_new=bytearray(raw)
    patches=[]
    for bank,pc,at,before,after in ((126,0x9076,FIXED,FIXED_BEFORE,fixed),
                                    (2,0xbfdd,LEVEL,LEVEL_BEFORE,level)):
        assert len(before)==len(after) and raw[at:at+len(before)]==before
        raw_new[at:at+len(before)]=after
        patches.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+len(before)],file_offset=at,
                            old_hex=before.hex(),new_hex=after.hex()))
    new=B.A.bundle(raw_new)
    mains=B.check_mains(old,new)
    tails=B.check_tails(old,new)
    savings={int(cycles) for cycles in tails['cycle_savings']}
    assert min(savings)==0 and max(savings)>100
    result=dict(passed=True,base_SHA256=PIN,expected_memory_only_SHA256=B.sha(raw_new),
                whole_GameCore=mains,compiled_column_tail=tails,patches=patches,
                scope='Preserve both shadow clears and terrain writes. Exact terminal CPU and memory parity. Interrupt proof separate.')
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,tails=tails)))


if __name__=='__main__':
    main()
