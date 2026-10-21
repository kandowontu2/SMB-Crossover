"""Root native equivalence and C compilation for the private 50GB runner."""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/mm48-private-reference-runner-u'
OUT=ROOT/'build/verification/root-reference-runner-u-validation-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    assert sha(PACKET/'frozen.json')=='366567ffa66ab34c5dce25e1f4b08b35b5b1a19a6faa2771c715a1e4ae1258cf'
    frozen=json.loads((PACKET/'frozen.json').read_text())
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    for n,r in frozen['inputs'].items():assert sha(ROOT/n)==r['sha256']
    plan=json.loads((PACKET/'equivalence-plan.json').read_text())
    OUT.mkdir()
    compile_command=['gcc','-shared','-O2','-Wall','-Wextra','-Wno-cast-function-type',
                     '-o',str(OUT/'capture-segments-u.dll'),str(PACKET/'capture_segments.c')]
    with (OUT/'compile.log').open('wb')as f:
        compile=subprocess.run(compile_command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    assert compile.returncode==0,str(OUT/'compile.log')
    with (OUT/'native.log').open('wb')as f:
        native=subprocess.run(plan['root_command'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    assert native.returncode==plan['expected_native_exit'],str(OUT/'native.log')
    old=ROOT/plan['existing_negative_folder'];new=ROOT/plan['prospective_output']
    shared={}
    for n,pin in plan['CSV_literal_equality_required'].items():
        assert sha(old/n)==pin['sha256'] and (old/n).stat().st_size==pin['bytes']
        assert (old/n).read_bytes()==(new/n).read_bytes(),('Complete literal nine-CSV identity',n)
        shared[n]={'sha256':sha(new/n),'bytes':(new/n).stat().st_size}
    m=json.loads((new/'manifest.json').read_text())
    assert m['result']==plan['expected_result'] and not m['verified_through_2_2']
    assert m['controller_only'] and not m['memory_or_register_writes'] and m['full_frame_audit']
    assert not any(new.glob('*.nes')) and not any(new.glob('*.dbg')) and not any(new.glob('*.lbl'))
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    for n,r in frozen['inputs'].items():assert sha(ROOT/n)==r['sha256']
    report={'status':'PASS_PRIVATE_U_NATIVE_FULL9CSV_EQUIVALENCE_AND_C_COMPILE_ONLY',
            'goal_complete':False,'accepted_release':False,'script_sha256':sha(Path(__file__)),
            'frozen_sha256':sha(PACKET/'frozen.json'),'compiler_exit':0,'compile_command':compile_command,
            'DLL_sha256':sha(OUT/'capture-segments-u.dll'),'native_exit':native.returncode,
            'native_manifest_sha256':sha(new/'manifest.json'),'complete_shared_CSVs':shared,
            'result':m['result'],'no_ROM_DBG_LBL_copies':True,
            'qualification':'Old1483-frame gameplay death remains a negative. New50GB recording/RGB/PCM runtime not yet exercised; no final route or release acceptance.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json')},indent=2))


if __name__=='__main__':main()
