"""Fit the private reset via an X-preserving four-byte loop (13B)."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/prepare_smb3plus_peach_complete_controller_1031_v1.py'
    negative=R/'build/smb3plus-peach-complete-controller-1031-v1/main-build.json'
    assert json.loads(negative.read_text())['returncode']!=0
    text=prior.read_text().replace("O=R/'build/smb3plus-peach-complete-controller-1031-v1'",
        "O=R/'build/smb3plus-peach-complete-controller-1031-v2'")
    old="    clear=m[0];text=text[:m.start()]+parts['MbPeachLeafFrame']+text[m.end():]"
    new="""    clear='''.proc MbPeachFloatClear
 phx
 lda #0
 ldx #3
Clear:sta MbFloatExpired,x
 dex
 bpl Clear
 plx
 rts
.endproc
'''
    text=text[:m.start()]+parts['MbPeachLeafFrame']+text[m.end():]"""
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace("sizes['MbPeachAfterJump']+15<=81","sizes['MbPeachAfterJump']+13<=81")
    text=text.replace('Move15B own Clear','Move13B own Clear').replace('Pure47B A81','Pure source A81')
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_complete_controller_v2'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()
    out=R/'build/smb3plus-peach-complete-controller-1031-v2/source-stage.json'
    d=json.loads(out.read_text());B=ns['B']
    d['retained_compile_negative']=str(negative)
    d['private_clear_ABI']='Preserves X/Y and clears all four fields. Its only caller restores incoming A/P itself; the loop replaces four stores without publishing a new ABI.'
    d['bindings'].update({str(p):B.sha(p) for p in [prior,negative]})
    B.write(out,json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
