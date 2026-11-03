"""Typed raw40 native defeat leaf after its source-proven no-drop boundary."""
import json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O;W=A.W


def main():
    proof=json.loads((O/'native-drop-boundary-v44.json').read_text());assert proof['passed']
    prior=json.loads((O/'native-packets-v42-layout.json').read_text());source=(O/'native-packets-v42.s').read_text()
    service=proof['proposed_private_service'];assert service['physical_PRG']==126 and 0x8000<=service['genuine_native_target']<0xa000
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');address=proof['sole_observable_nonstack_write']['address']
    at=source.index('NativeVictimDefeat:\n');old=source[at:source.index('DkjrNativeVictimEnd:',at)]
    assert len(re.findall(r'^ ',old,re.M))==6
    replacement='NativeVictimDefeat:\n stx $%04x\n jmp $%04x\n'%(address,service['genuine_native_target'])
    source=source.replace(old,replacement,1)
    source+='\n.export NativeVictimDefeat\n'
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-defeat-pause-v45.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-defeat-main-v45.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-defeat-ports-v45.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    blob,L=A.assemble('native-defeat-v45',source,cfg);assert len(blob)==prior['body_bytes']-9 and L['DkPauseThaw']==0xd60c
    q=dict(prior);q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),typed_native_defeat=service,
        scope='Private owner40 specialization only: exact sole native rejected-drop side effect, then genuine unchanged lower-fixed native ShellOrBlockDefeat continuation. No shared/native hook changed. Full service and actual Main/IRQ differential required.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-packets-v42.s',O/'native-drop-boundary-v44.json',O/'native-defeat-v45.s',O/'native-defeat-v45.bin']})
    (O/'native-defeat-v45-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','body_bytes','header_spare','typed_native_defeat']}))


if __name__=='__main__':main()
