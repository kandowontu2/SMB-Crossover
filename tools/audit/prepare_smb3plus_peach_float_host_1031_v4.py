"""Preserve Peach's float-ready producer in all original power forms.

The original form gate belongs to the velocity override, after BAC0's ready
producer. Keep the failed v3 candidate and its source comparison untouched.
"""
from pathlib import Path
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_smb3plus_peach_float_host_1031_v1 as P


def main():
    source2=R/'tools/reference/smb3plus_peach_float_1031_v2.s'
    source3=R/'tools/reference/smb3plus_peach_float_1031_v3.s'
    negative=R/'build/smb3plus-peach-float-host-1031-v3/float-negative-v1.json'
    failure=json.loads(negative.read_text())
    assert failure['case']['kind']=='after_jump' and failure['case']['form']==4
    code=source2.read_text()
    a=code.index('.proc MbPeachAfterJump\n');z=code.index('.endproc',a)
    body=code[a:z]
    gate=' lda M3Form\n cmp #4\n bpl Done\n'
    assert body.count(gate)==1
    body=body.replace(gate,'')
    body=P.once(body,'Override:\n','Override:\n'+gate)
    code=code[:a]+body+code[z:]
    if source3.exists():assert source3.read_text()==code
    else:source3.write_text(code,encoding='utf-8',newline='\n')
    P.S=source3;P.O=R/'build/smb3plus-peach-float-host-1031-v4';P.J=P.O/'joint'
    original_write=P.B.write
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
        if path==P.J/'src/smb3_mario_art.inc' and 'MbFloatForm5ChrLo' in text:
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
            d['retained_negatives']=[str(negative),str(R/'build/smb3plus-peach-float-host-1031-v1/wobble-negative-v1.json')]
            d['correction']='Original BAC0 produces ready2 in forms4..6; original B9F3 gates only the subsequent float velocity override.'
            d['limits'].insert(0,'Transient low-table scratch pointers change for form5; exact pixels/final live outputs and ISR behavior require qualification.')
            d['bindings'].update({str(p):P.B.sha(p) for p in [Path(__file__),source2,negative]})
            text=json.dumps(d,indent=2)+'\n'
        original_write(path,text)
    P.B.write=write
    try:P.main()
    finally:P.B.write=original_write


if __name__=='__main__':main()
