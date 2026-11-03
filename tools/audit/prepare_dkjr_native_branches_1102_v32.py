"""Recover private code bytes by equivalent short conditional encodings only.

No movement, timing counter, art/state or service policy is removed. Original
relocation used longbranch macros conservatively even for nearby labels.
"""
import json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    prior=json.loads((O/'native-lifecycle-v30-layout.json').read_text())
    assert json.loads((O/'native-lifecycle-v31-CPU.json').read_text())['passed']
    source=(O/'native-lifecycle-v30.s').read_text();branches=[]
    def mark(m):
        label='DkShortCandidate%d'%len(branches)
        branches.append((label,m[1],m[2]))
        return label+':\n j'+m[1]+' '+m[2]
    source=re.sub(r'(?m)^ j(eq|ne|cc|cs|mi|pl|vc|vs) ([A-Za-z_]\w*)[ \t]*$',mark,source)
    exports='\n.export '+','.join(sorted({n for n,_,_ in branches}|{t for _,_,t in branches}))+'\n'
    source+=exports
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-branches-pause-v32.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-branches-main-v32.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-branches-ports-v32.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    relaxed=set()
    initial_body=None
    for iteration in range(16):
        blob,L=A.assemble('native-branches-v32',source,cfg)
        if initial_body is None:
            initial_body=blob
            assert blob==(O/'native-lifecycle-v30.bin').read_bytes()
        changes=[]
        for name,condition,target in branches:
            old=name+':\n j'+condition+' '+target
            if old in source and -128<=L[target]-(L[name]+2)<=127:
                changes.append((old,name+':\n b'+condition+' '+target));relaxed.add(name)
        if not changes:break
        for old,new in changes:source=source.replace(old,new,1)
    else:raise AssertionError('short-branch relaxation convergence')
    assert L['DkPauseThaw']==0xd60c and L['DkNativePortsEnd']==prior['metadata_end']
    recovered=prior['body_bytes']-len(blob)
    assert recovered>0 and recovered%3==0
    # Strip our labels/exports and restore every short spelling. This is an
    # exact textual semantic source comparison, including all data/imports.
    normalized=source
    for name,condition,target in branches:
        normalized=normalized.replace(name+':\n b'+condition+' '+target,name+':\n j'+condition+' '+target)
        normalized=normalized.replace(name+':\n','')
    normalized=normalized.replace(exports,'')
    assert normalized==(O/'native-lifecycle-v30.s').read_text()
    out=dict(prior)
    out.update(passed=True,qualified=False,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),labels=L,
        conservative_long_branches=len(branches),explicit_short_branches=len(relaxed),shortened_branches=recovered//3,bytes_recovered=recovered,iterations=iteration+1,
        semantic_source_normalization_exact=True,source_cycle_counters_and_abilities_unchanged=True,
        scope='Conditional encoding compaction only. CPU duration changes, original logical counters/state do not. Native/source differential qualification is required before using this successor.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-lifecycle-v30.s',O/'native-lifecycle-v31-CPU.json',O/'native-branches-v32.s',O/'native-branches-v32.bin']})
    out['short_branch_rows']=[dict(label=n,condition=c,target=t,PC=L[n],target_PC=L[t])for n,c,t in branches if n in relaxed]
    (O/'native-branches-v32-layout.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','body_bytes','header_spare','shortened_branches','bytes_recovered','iterations']}))


if __name__=='__main__':main()
