"""Bounded ordinary current-P Scrooge firebar-phase discovery; no saved state."""
from pathlib import Path
import hashlib,json,re,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-scrooge-phase-i2'
BASE=ROOT/'build/verification/root49p-scrooge-live-h/policy.lua'
WRAP=ROOT/'tools/playthroughs/scrooge_castle_phase_i2.lua'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
REF=ROOT/'build/verification/root49p-three-fixed-a/current-p-mmc3-reference.json'
U=ROOT/'build/verification/mm48-private-reference-runner-u'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    cat=json.loads((CP/'manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in cat.items())
    old=json.loads((ROOT/'build/verification/root49p-scrooge-live-h/report.json').read_text())
    assert sha(BASE)==old['policy_sha256']
    text=WRAP.read_text();needle='local base=assert(SCROOGE_P_BASE)';assert text.count(needle)==1
    code=text.replace(needle,'local base=(function()\n'+BASE.read_text()+'\nend)()')
    assert not re.search(r'\bdofile\s*\(',code)
    assert not re.search(r'emu\.(?:write|setState|saveState|loadState|setInput)\s*\(',code)
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    valid,error=LuaRuntime().eval("function(s)local f,e=load(s,'scrooge-phase-i','t');return f~=nil,e end")(code)
    assert valid,error
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+650_000_000<50_000_000_000
    OUT.mkdir();policy=OUT/'policy.lua';policy.write_text(code)
    expected=ROOT/'build/roster-through-2-2/root49p-scrooge-phase-i2-12-v0-mmc3';assert not expected.exists()
    command=[sys.executable,str(U/'roster_run_reference.py'),'--reference-descriptor',str(REF),'--reference-sha256',sha(REF),
             '--reference-reserve-bytes','150000000','--character','12','--mapper','mmc3','--policy',str(policy),
             '--tag','root49p-scrooge-phase-i2','--frames','38000','--timeout','300']
    pins={p.relative_to(ROOT).as_posix():sha(p)for p in [BASE,WRAP]}
    report=dict(status='RUNNING_SCROOGE_ORDINARY_PHASE_I2',command=command,script_sha256=sha(Path(__file__)),policy_sha256=sha(policy),
                controller_sources=pins,workspace_before=used,accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with (OUT/'native.log').open('wb')as f:p=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    report['native_exit']=p.returncode
    manifest=expected/'manifest.json'
    if manifest.exists():
        m=json.loads(manifest.read_text());report.update(result=m.get('result'),manifest_sha256=sha(manifest))
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
        assert m['config']['replay']is None and m['config']['prefix']is None and not m['config']['record']
        assert m['rom_sha256']==sha(CP/'smb-crossover-mmc3.nes')and m['policy_sha256']==sha(policy)
    assert all(sha(ROOT/n)==h for n,h in cat.items())and all(sha(ROOT/n)==h for n,h in pins.items())
    report.update(status='COMPLETE_SCROOGE_ORDINARY_PHASE_I2_ALL_OUTCOMES_RETAINED',workspace_after=workspace_bytes(ROOT),
                  qualification='Adaptive ordinary power-on discovery. All input/render/audio/OAM evidence retained. A clear needs a separate full fixed replay; no source collision or final-video claim.')
    save();print(json.dumps(dict(status=report['status'],native_exit=p.returncode,report_sha256=sha(OUT/'report.json'))))

if __name__=='__main__':main()
