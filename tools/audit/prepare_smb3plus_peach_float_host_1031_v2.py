"""Keep float code in C91; factor the identical CHR low-table shape in A90.

The v1 failure executed an A90 helper while A92 owned the native controller.
Its wobble factorization also omitted indices16/48. Both failures are retained.
"""
from pathlib import Path
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_smb3plus_peach_float_host_1031_v1 as P


def main():
    source1=R/'tools/reference/smb3plus_peach_float_1031_v1.s'
    source2=R/'tools/reference/smb3plus_peach_float_1031_v2.s'
    assert not source2.exists()
    negative=R/'build/smb3plus-peach-float-host-1031-v1/wobble-negative-v1.json'
    n=json.loads(negative.read_text());assert not n['passed'] and n['failures']
    code=source1.read_text()
    code=P.once(code,' and #$1f\n beq One\n cmp #7\n beq Two\n rts',
        ' and #$1f\n cmp #7\n beq Two\n and #$0f\n beq One\n rts')
    source2.write_text(code,encoding='utf-8',newline='\n')
    P.S=source2;P.O=R/'build/smb3plus-peach-float-host-1031-v2';P.J=P.O/'joint'
    original_write=P.B.write
    # This exact shape equality lets us reuse form3 low bytes plus4. No CHR
    # bytes or form5 descriptor/pointer output names are changed.
    art=(P.P/'joint/src/smb3_mario_art.inc').read_text()
    arrays={int(m[1]):list(map(int,m[2].split(','))) for m in re.finditer(r'M3Form(\d)ChrLo: \.byte ([0-9,]+)',art)}
    assert len(arrays[3])==81 and arrays[5]==[v+4 for v in arrays[3]]
    wobble=re.search(r'\.proc MbPeachFloatWobble\n(.*?)\.endproc',code,re.S)[1]
    sign=wobble.split('Sign:\n',1)[1]
    helper='''::MbFloatReadChrLow:
 php
 lda M3RenderForm
 cmp #5
 bne MbFloatLowOriginal
 lda (R0),y
 clc
 adc #4
 jmp MbFloatLowStore
MbFloatLowOriginal:
 lda (R0),y
MbFloatLowStore:
 sta SmChrBank
 plp
 rts
'''

    def write(path,text):
        path=Path(path)
        if path==P.J/'src/smb3_mario_art.inc':
            assert text.count('MbFloatForm5ChrLo')==2
            text=text.replace('MbFloatForm5ChrLo','M3Form3ChrLo')
        if path==P.J/'src/smb3_mario_render.s' and '::MbPeachFloatSign:' in text:
            a=text.index('::MbPeachFloatSign:');z=text.index(' .res 37-6-(*-MbFloatPaletteBody)',a)
            text=text[:a]+helper+text[z:]
            text=P.once(text,' lda (R0),y\n sta SmChrBank\n',
                ' jsr MbFloatReadChrLow\n nop\n nop\n')
        if path==P.J/'smb3plus_float_data.s':
            text='.pushseg\n.segment "M3_GFX"\n.proc MbPeachFloatSign\n'+sign+'.endproc\nMbFloatDataEnd:\n.assert MbFloatDataEnd<=$d400,lderror,"Preserve Rogue Dawn upper audio"\n.popseg\n'
        if path==P.O/'source-stage.json':
            d=json.loads(text)
            d['relocation']='Form5 low CHR bytes are exactly form3 plus4 for all81 frames. A90 low-reader applies that offset while preserving its incoming flags; source float helpers execute only C91.'
            d['retained_negative']=str(negative)
            d['limits'].insert(0,'Transient low-table scratch pointers change for form5; exact pixels/final live outputs and ISR behavior require qualification.')
            d['bindings'].update({str(p):P.B.sha(p) for p in [Path(__file__),source1,negative]})
            text=json.dumps(d,indent=2)+'\n'
        original_write(path,text)
    P.B.write=write
    try:P.main()
    finally:P.B.write=original_write


if __name__=='__main__':main()
