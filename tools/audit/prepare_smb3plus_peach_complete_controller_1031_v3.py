"""Place the six-byte sink tail in the other existing high-table spare."""
from pathlib import Path
import json

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/prepare_smb3plus_peach_complete_controller_1031_v1.py'
    source=R/'tools/reference/smb3plus_peach_complete_controller_1031_v2.s'
    original=R/'tools/reference/smb3plus_peach_complete_controller_1031_v1.s'
    code=original.read_text();assert code.count(' bne Sink\n')==1
    code=code.replace(' bne Sink\n',' jne MbPeachSinkOverride\n')
    code=code.replace('Sink:\n jsr MbPeachFloatSink\n jmp Override\n','')
    code+='\n.proc MbPeachSinkOverride\n jsr MbPeachFloatSink\n jmp MbPeachAfterOverride\n.endproc\n'
    assert not source.exists();source.write_text(code,encoding='utf-8',newline='\n')
    text=prior.read_text().replace("O=R/'build/smb3plus-peach-complete-controller-1031-v1'",
        "O=R/'build/smb3plus-peach-complete-controller-1031-v3'")
    text=text.replace("S=R/'tools/reference/smb3plus_peach_complete_controller_1031_v1.s'",f"S=R/{str(source.relative_to(R).as_posix())!r}")
    at='    B.write(art,text)'
    replacement="""    text=once(text,' .res 81-(*-M3Form1ChrHi),2\\n',
        parts['MbPeachSinkOverride']+' .res 81-(*-M3Form1ChrHi),2\\n')
    B.write(art,text)"""
    assert text.count(at)==1;text=text.replace(at,replacement)
    text=text.replace("sizes['MbPeachJumpRoot']<=43","sizes['MbPeachJumpRoot']+sizes['MbPeachSinkOverride']<=43")
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_complete_controller_v3'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()
    out=R/'build/smb3plus-peach-complete-controller-1031-v3/source-stage.json'
    d=json.loads(out.read_text());B=ns['B']
    negatives=[R/'build'/f'smb3plus-peach-complete-controller-1031-v{i}/main-build.json' for i in [1,2]]
    assert all(json.loads(B.read(p))['returncode']!=0 for p in negatives)
    d['retained_compile_negatives']=[str(p) for p in negatives]
    d['storage']+=' The six-byte Sink→Override tail occupies the7B spare after the revised jump-input helper. Clear retains its original15B implementation.'
    d['bindings'].update({str(p):B.sha(p) for p in [prior,original,*negatives]})
    B.write(out,json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
