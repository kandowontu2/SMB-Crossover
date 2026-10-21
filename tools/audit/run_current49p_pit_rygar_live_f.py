"""New ordinary F trials with floor-aware air braking; no ROM/state changes."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-pit-rygar-live-f'
PACKET=ROOT/'build/verification/mm48-private-reference-runner-u'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
REFERENCE=ROOT/'build/verification/root49p-three-fixed-a/current-p-mmc3-reference.json'
WRAPPER=ROOT/'tools/playthroughs/pit_rygar_air_landing_f.lua'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    cat=json.loads((CP/'manifest.json').read_text())['source_hashes'];assert all(sha(ROOT/n)==h for n,h in cat.items())
    assert sha(PACKET/'frozen.json')=='366567ffa66ab34c5dce25e1f4b08b35b5b1a19a6faa2771c715a1e4ae1258cf'
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+300_000_000+4_175_000_000<50_000_000_000
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    OUT.mkdir();cases=[]
    for char,name in [(6,'Pit'),(7,'Rygar')]:
        old=ROOT/'build/verification/root49p-pit-rygar-live-e'/(name.lower()+'-policy.lua')
        code='local base=(function()\n'+old.read_text()+'\nend)()\n'+WRAPPER.read_text()
        assert not re.search(r'emu\.(?:write|setState|saveState|loadState|setInput)\s*\(',code)
        assert not re.search(r'\bdofile\s*\(',code)
        ok,error=parse(code,name+'-F');assert ok,error
        policy=OUT/(name.lower()+'-policy.lua');policy.write_text(code)
        expected=ROOT/'build/roster-through-2-2'/f'root49p-pit-rygar-live-f-{char}-v0-mmc3';assert not expected.exists()
        command=[sys.executable,str(PACKET/'roster_run_reference.py'),'--reference-descriptor',str(REFERENCE),
                 '--reference-sha256',sha(REFERENCE),'--reference-reserve-bytes','150000000','--character',str(char),
                 '--mapper','mmc3','--tag','root49p-pit-rygar-live-f','--policy',str(policy),'--frames','38000','--timeout','300']
        cases.append(dict(character=char,name=name,policy_sha256=sha(policy),base_policy_sha256=sha(old),expected=str(expected),command=command))
    report=dict(status='RUNNING_P_ORDINARY_ADAPTIVE_F',script_sha256=sha(Path(__file__)),wrapper_sha256=sha(WRAPPER),
                cases=cases,workspace_before=used,own_future_reserve=300_000_000,other_future_reserve=4_175_000_000,
                accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for c in cases:
        with (OUT/(c['name']+'.log')).open('wb')as log:p=subprocess.run(c['command'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        manifest=Path(c['expected'])/'manifest.json';c.update(native_exit=p.returncode)
        if manifest.exists():
            m=json.loads(manifest.read_text());c.update(manifest_sha256=sha(manifest),result=m.get('result'))
            assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
            assert m['config']['replay']is None and m['config']['prefix']is None and not m['config']['record']
            assert m['rom_sha256']==sha(CP/'smb-crossover-mmc3.nes')and m['policy_sha256']==c['policy_sha256']
            assert not m['verified_through_2_2']
        save()
    assert all(sha(ROOT/n)==h for n,h in cat.items())
    report.update(status='COMPLETE_P_ORDINARY_ADAPTIVE_F_ALL_OUTCOMES_RETAINED',workspace_after=workspace_bytes(ROOT),
                  qualification='New complete ordinary power-on controller attempt with full audit; only controller steering/selection changes. All deaths or stalls retained. Any clear requires full independent current-ROM fixed replay; no source collision proof inferred.')
    save();print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT/'report.json'))))

if __name__=='__main__':main()
