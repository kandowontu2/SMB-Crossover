"""Full ordinary Pit/Rygar adaptive discovery on P, no movie/prefix/grants."""
from pathlib import Path
import concurrent.futures,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-pit-rygar-live-c'
PACKET=ROOT/'build/verification/mm48-private-reference-runner-u'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
REFERENCE=ROOT/'build/verification/root49p-three-fixed-a/current-p-mmc3-reference.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    cat=json.loads((CP/'manifest.json').read_text())['source_hashes'];assert all(sha(ROOT/n)==h for n,h in cat.items())
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+150_000_000+135_000_000<50_000_000_000
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    OUT.mkdir();cases=[];reference_sha=sha(REFERENCE)
    for char,name,tag in [(6,'Pit','pit-38d-full-audit-a-6-v0-mmc3'),(7,'Rygar','rygar-38d-full-audit-a-7-v0-mmc3')]:
        original=ROOT/'build/roster-through-2-2'/tag/'policy.lua';text=original.read_text()
        assert not re.search(r'emu\.(?:write|setState|saveState|loadState|setInput)\s*\(',text)
        assert not re.search(r'\bdofile\s*\(',text),'Only the inspected self-contained geometry controller is admitted'
        good,error=parse(text,str(original));assert good,error
        policy=OUT/(name.lower()+'-policy.lua');policy.write_bytes(original.read_bytes());assert sha(policy)==sha(original)
        expected=ROOT/'build/roster-through-2-2'/f'root49p-pit-rygar-live-c-{char}-v0-mmc3';assert not expected.exists()
        command=[sys.executable,str(PACKET/'roster_run_reference.py'),'--reference-descriptor',str(REFERENCE),
                 '--reference-sha256',reference_sha,'--reference-reserve-bytes','75000000','--character',str(char),
                 '--mapper','mmc3','--tag','root49p-pit-rygar-live-c','--policy',str(policy),'--frames','38000','--timeout','300']
        cases.append({'character':char,'name':name,'policy_sha256':sha(policy),'original_geometry_policy':str(original),
                      'expected':str(expected),'command':command})
    report={'status':'running-current-P-live-ordinary-discovery','accepted_release':False,'goal_complete':False,
            'script_sha256':sha(Path(__file__)),'current_P_manifest_sha256':sha(CP/'manifest.json'),
            'reference_descriptor_sha256':reference_sha,'workspace_before':used,'own_reserve':150_000_000,
            'other_future_reserve':135_000_000,'cases':cases}
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    def run(c):
        with (OUT/(c['name']+'.log')).open('wb')as f:r=subprocess.run(c['command'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        p=Path(c['expected'])/'manifest.json';m=json.loads(p.read_text())
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
        assert m['config']['replay']is None and m['config']['prefix']is None and not m['config']['record']
        assert m['rom_sha256']==sha(CP/'smb-crossover-mmc3.nes')and m['policy_sha256']==c['policy_sha256']
        assert not m['verified_through_2_2'],'Adaptive clear is not independent fixed proof'
        result=m.get('result');clear=bool(r.returncode==0 and result and result['all_six_stages']and result['cleared']and result['deaths']==0)
        c.update(native_exit=r.returncode,result=result,manifest_sha256=sha(p),ordinary_adaptive_clear=clear,independent_fixed_proof=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        for f in concurrent.futures.as_completed([pool.submit(run,c)for c in cases]):f.result();save()
    assert all(sha(ROOT/n)==h for n,h in cat.items())
    report.update(status='COMPLETE_ORDINARY_DISCOVERIES_RETAIN_ALL_NEGATIVES_FIXED_PROOFS_PENDING',
                  workspace_after=workspace_bytes(ROOT),qualification='Full power-on ordinary adaptive controller with full audit; no historical movie/prefix, state grants or save states. Any clear requires fresh complete current-ROM fixed replay before acceptance.')
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json'),
                            'adaptive_clears':[c['name']for c in cases if c['ordinary_adaptive_clear']]}))

if __name__=='__main__':main()
