"""Root ordinary adaptive trials with retained native/lossless/delivery video."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-pit-rygar-live-d'
PACKET=ROOT/'build/verification/mm48-private-reference-runner-u'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
REFERENCE=ROOT/'build/verification/root49p-three-fixed-a/current-p-mmc3-reference.json'
WRAPPER=ROOT/'tools/playthroughs/pit_rygar_third_pipe_d.lua'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    cat=json.loads((CP/'manifest.json').read_text())['source_hashes'];assert all(sha(ROOT/n)==h for n,h in cat.items())
    assert sha(PACKET/'frozen.json')=='366567ffa66ab34c5dce25e1f4b08b35b5b1a19a6faa2771c715a1e4ae1258cf'
    frozen=json.loads((PACKET/'frozen.json').read_text())
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+4_000_000_000+175_000_000<50_000_000_000
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    wrapper=WRAPPER.read_text();labels=(CP/'smb-crossover-mmc3.lbl').read_text()
    for name in set(re.findall(r"c\.r\('([^']+)'",wrapper)):
        assert re.search(r'\.'+re.escape(name)+r'(?:\s|$)',labels),name
    OUT.mkdir();cases=[]
    for char,name in [(6,'Pit'),(7,'Rygar')]:
        old=ROOT/'build/verification/root49p-pit-rygar-live-c'/(name.lower()+'-policy.lua')
        code='local base=(function()\n'+old.read_text()+'\nend)()\n'+wrapper
        assert not re.search(r'emu\.(?:write|setState|saveState|loadState|setInput)\s*\(',code)
        assert not re.search(r'\bdofile\s*\(',code)
        ok,error=parse(code,name+'-D');assert ok,error
        policy=OUT/(name.lower()+'-policy.lua');policy.write_text(code)
        expected=ROOT/'build/roster-through-2-2'/f'root49p-pit-rygar-live-d-{char}-v0-mmc3';assert not expected.exists()
        command=[sys.executable,str(PACKET/'roster_run_reference.py'),'--reference-descriptor',str(REFERENCE),
                 '--reference-sha256',sha(REFERENCE),'--reference-reserve-bytes','2000000000','--character',str(char),
                 '--mapper','mmc3','--tag','root49p-pit-rygar-live-d','--policy',str(policy),'--frames','38000',
                 '--timeout','600','--record-segments','--segment-frames','512','--keep-avi']
        cases.append(dict(character=char,name=name,policy_sha256=sha(policy),base_policy_sha256=sha(old),
                          expected=str(expected),command=command))
    report=dict(status='RUNNING_P_ORDINARY_ADAPTIVE_RECORDED_D',script_sha256=sha(Path(__file__)),
                wrapper_sha256=sha(WRAPPER),current_P_manifest_sha256=sha(CP/'manifest.json'),cases=cases,
                workspace_before=used,own_future_reserve=4_000_000_000,other_future_reserve=175_000_000,
                accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for c in cases:
        with (OUT/(c['name']+'.log')).open('wb')as log:
            p=subprocess.run(c['command'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        folder=Path(c['expected']);manifest=folder/'manifest.json'
        c.update(native_exit=p.returncode)
        if manifest.exists():
            m=json.loads(manifest.read_text());c.update(manifest_sha256=sha(manifest),result=m.get('result'))
            assert m['controller_only'] and m['full_frame_audit'] and not m['memory_or_register_writes']
            assert m['config']['replay']is None and m['config']['prefix']is None
            assert m['rom_sha256']==sha(CP/'smb-crossover-mmc3.nes') and m['policy_sha256']==c['policy_sha256']
            assert not m['verified_through_2_2'] and not m.get('recording_verified',False)
            proof=folder/'playthrough-lossless.verification/report.json'
            if proof.exists():
                q=json.loads(proof.read_text());c.update(lossless_result=q.get('result'),lossless_report_sha256=sha(proof))
            c.update(assemble_exit=m.get('assemble_exit'),delivery_exit=m.get('delivery_exit'),
                     recording_failure=m.get('recording_failure'),native_parts_retained=m.get('native_parts_retained'))
            c['retained_media']={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in folder.iterdir()
                                  if q.suffix in ('.avi','.wav','.mkv','.mp4')}
        save()
    assert all(sha(ROOT/n)==h for n,h in cat.items())
    report.update(status='COMPLETE_P_ORDINARY_ADAPTIVE_D_ALL_OUTCOMES_RETAINED',workspace_after=workspace_bytes(ROOT),
                  qualification='Ordinary power-on, full audit, no state grants/history prefix/input movie. Videos are exploratory; no successful independent fixed replay or final-recording claim. All native AVI/WAV/losslessMKV/MP4 retained.')
    save();print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT/'report.json'))))

if __name__=='__main__':main()
