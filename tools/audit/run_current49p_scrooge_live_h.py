"""Fresh ordinary Scrooge discovery on P, with controller-only inlining."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-scrooge-live-h'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
U=ROOT/'build/verification/mm48-private-reference-runner-u'
REF=ROOT/'build/verification/root49p-three-fixed-a/current-p-mmc3-reference.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    catalog=json.loads((CP/'manifest.json').read_text())['source_hashes'];assert all(sha(ROOT/n)==h for n,h in catalog.items())
    paths=[ROOT/'tools/playthroughs/mario_luigi_scrooge_nav.lua',ROOT/'tools/playthroughs/mario_luigi_scrooge_policy.lua',
           ROOT/'tools/playthroughs/scrooge_native_policy.lua',ROOT/'build/verification/root49n-scrooge-live-d/policy.lua',
           ROOT/'build/roster-through-2-2/root49n-scrooge-platform-g-12-v0-mmc3/policy.lua']
    pins={p.relative_to(ROOT).as_posix():sha(p)for p in paths}
    code=paths[0].read_text()
    substitutions=["local travel=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))",
                   "local normal=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))",
                   "local base=assert(dofile(root..'/tools/playthroughs/scrooge_native_policy.lua'))",
                   "local prior=assert(dofile(root..'/build/verification/root49n-scrooge-live-d/policy.lua'))"]
    for path,needle in zip(paths[1:],substitutions):
        text=path.read_text();assert text.count(needle)==1
        text=text.replace(needle,needle.split('=')[0]+'=(function()\n'+code+'\nend)()')
        code=text
    observer="dofile(root..'/build/verification/root49n-scrooge-platform-route-g/observer-bound.lua')"
    assert code.count(observer)==1;code=code.replace(observer,'-- The private-N passive observer is omitted from this fresh P controller.')
    assert not re.search(r'\bdofile\s*\(',code)
    assert not re.search(r'emu\.(?:write|setState|saveState|loadState|setInput)\s*\(',code)
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    good,error=parse(code,'Scrooge P self-contained controller');assert good,error
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+150_000_000+500_000_000<50_000_000_000
    OUT.mkdir();policy=OUT/'policy.lua';policy.write_text(code)
    expected=ROOT/'build/roster-through-2-2/root49p-scrooge-live-h-12-v0-mmc3';assert not expected.exists()
    command=[sys.executable,str(U/'roster_run_reference.py'),'--reference-descriptor',str(REF),'--reference-sha256',sha(REF),
             '--reference-reserve-bytes','150000000','--character','12','--mapper','mmc3','--policy',str(policy),
             '--tag','root49p-scrooge-live-h','--frames','38000','--timeout','300']
    report=dict(status='RUNNING_SCROOGE_P_ORDINARY_POWERON_H',command=command,script_sha256=sha(Path(__file__)),
                policy_sha256=sha(policy),input_controller_sources=pins,private_N_observer_omitted=True,
                historical_movie_or_prefix=False,workspace_before=used,accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with (OUT/'native.log').open('wb')as stream:p=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    report.update(native_exit=p.returncode)
    manifest=expected/'manifest.json'
    if manifest.exists():
        m=json.loads(manifest.read_text());report.update(result=m.get('result'),manifest_sha256=sha(manifest))
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
        assert m['config']['replay']is None and m['config']['prefix']is None and not m['config']['record']
        assert m['rom_sha256']==sha(CP/'smb-crossover-mmc3.nes')and m['policy_sha256']==sha(policy)
        assert not m['verified_through_2_2']
    assert all(sha(ROOT/n)==h for n,h in pins.items())and all(sha(ROOT/n)==h for n,h in catalog.items())
    report.update(status='COMPLETE_SCROOGE_P_ORDINARY_H_ALL_OUTCOMES_RETAINED',workspace_after=workspace_bytes(ROOT),
                  qualification='Full ordinary current-P discovery, no historical movie/prefix/grants. Inherited geometry functions are literal, with only source inlining and omission of the source-N passive observer. Any clear requires independent complete fixed replay.')
    save();print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT/'report.json'),native_exit=p.returncode)))

if __name__=='__main__':main()
