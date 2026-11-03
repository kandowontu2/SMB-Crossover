"""Replace unfinished native terrain query rows with genuine fixed probes."""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O;W=A.W


def main():
    prior=json.loads((O/'native-branches-v32-layout.json').read_text())
    assert json.loads((O/'native-branches-v33-CPU.json').read_text())['passed']
    source=(O/'native-branches-v32.s').read_text();b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes')
    targets=dict(prior['implemented_vector_rows']);targets.update({'10':'DkNativeHead','12':'DkNativeAdder','13':'DkNativeBoxProfile','14':'DkNativeSide'})
    native={}
    for public,name in [('DkNativeHead','BlockBufferColli_Head'),('DkNativeSide','BlockBufferColli_Side')]:
        pc=W.address(b,name);at=W.location(b,name);assert 0x8000<=pc<0xa000
        assert A.BASE.read_bytes()[at:at+32]==b['raw'][at:at+32]
        source=public+'=$%04x\n'%pc+source
        native[public]=dict(name=name,PC=pc,physical_PRG=(at-16)//8192,first32_SHA256=A.sha(b['raw'][at:at+32]))
    at=source.index('DkServices:\n')+len('DkServices:\n');lines=source[at:].splitlines(True)
    for i in range(38):
        assert lines[i].startswith(' jmp ');lines[i]=' jmp '+targets.get(str(i),'DkUnavailable')+'\n'
    source=source[:at]+''.join(lines)
    leaf='''
.export DkNativeHead,DkNativeSide,DkNativeAdder,DkNativeBoxProfile
; Native head/side are metatile-return APIs, so CLCRTS cannot reject them.
; The fixed genuine queries preserve native packet scratch/probe side effects.
; Original DK's own32wide16tall terrain rectangles/two hands remain sole
; movement logic. Native opaque block/coin effects use the existing16tall
; probe profile without altering SMB power state. Source FullBox remains a
; separate exact D2BD contact rectangle, never this generic fallback profile.
DkNativeAdder:
 ldy #2
 sec
 rts
DkNativeBoxProfile:
 ldy #1
 sec
 rts
'''
    marker='DkjrComponentEnd:\n.export DkjrComponentEnd\n';assert source.count(marker)==1
    source=source.replace(marker,leaf+marker)
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-terrain-pause-v36.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-terrain-main-v36.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-terrain-ports-v36.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    blob,L=A.assemble('native-terrain-v36',source,cfg)
    old=(O/'native-branches-v32.bin').read_bytes();assert blob[114:len(old)]==old[114:]
    assert len(blob)==len(old)+8 and L['DkPauseThaw']==0xd60c
    q=dict(prior);q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),implemented_vector_rows=targets,unimplemented_rows=[i for i in range(38)if str(i)not in targets],native_terrain_imports=native,
        scope='Private genuine native head/side row implementation for the retained actual Main negative. No new shared/native selector or cart writes; native compatibility predicates require actual caller qualification.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-branches-v32.s',O/'native-branches-v33-CPU.json',O/'native-terrain-v36.s',O/'native-terrain-v36.bin']})
    (O/'native-terrain-v36-layout.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','body_bytes','header_spare','unimplemented_rows']}))


if __name__=='__main__':main()
