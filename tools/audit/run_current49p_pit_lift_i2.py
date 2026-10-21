"""Root ordinary power-on Pit discovery; actual support, retained lossless video."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-pit-final-lift-i2'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
H=ROOT/'build/verification/pit49p-final-lifts-h-passive'
U=ROOT/'build/verification/mm48-private-reference-runner-u'
REF=ROOT/'build/verification/root49p-three-fixed-a/current-p-mmc3-reference.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    catalog=json.loads((CP/'manifest.json').read_text())['source_hashes'];assert all(sha(ROOT/n)==v for n,v in catalog.items())
    assert sha(H/'actual-attempt-receipt.json')=='c77efb6fdf979ac031bcf30583059cc922a9949463ab186faed5c9f4c6a72e19'
    old=ROOT/'build/verification/root49p-pit-rygar-live-g/pit-policy.lua'
    wrapper=ROOT/'tools/playthroughs/pit_final_lift_i2.lua'
    code='local base=(function()\n'+old.read_text()+'\nend)()\n'+wrapper.read_text()
    assert not re.search(r'emu\.(?:write|setState|saveState|loadState|setInput)\s*\(',code)and not re.search(r'\bdofile\s*\(',code)
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    good,error=parse(code,'Pit I2 ordinary controller');assert good,error
    # H's physical hooks remain literal. Only the new passive window/limits
    # follow the controller's live region instead of the old death's frames.
    obs=(H/'observer.lua').read_text()
    token="return frame>=7800 and frame<=8001 and r('SelectedCharacter')==6"
    assert obs.count(token)==1
    obs=obs.replace(token,"return r('Player_PageLoc')*256+r('Player_X_Position')>=2368 and r('Player_PageLoc')*256+r('Player_X_Position')<=2688 and r('SelectedCharacter')==6")
    obs=obs.replace('8000000','16000000').replace('Bounded8MB','Bounded16MB').replace('8000','16000')
    # Reject accidental further emulated-control operations in passive text.
    assert not re.search(r'emu\.(?:write|setState|saveState|loadState|setInput)\s*\(',obs)
    good,error=parse(obs,'Pit I2 region observer');assert good,error
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+2_000_000_000+250_000_000<50_000_000_000
    OUT.mkdir();(OUT/'observer.lua').write_text(obs)
    policy=OUT/'policy.lua'
    hpolicy=(H/'policy.lua').read_text();line=next(s for s in hpolicy.splitlines()if s.startswith('PIT_LIFT_HOOKS='))
    policy.write_text(line+'\ndofile([=['+(OUT/'observer.lua').as_posix()+']=])\n'+code)
    good,error=parse(policy.read_text(),'Pit I2 bound actual hooks+policy');assert good,error
    expected=ROOT/'build/roster-through-2-2/root49p-pit-final-lift-i2-6-v0-mmc3';assert not expected.exists()
    command=[sys.executable,str(U/'roster_run_reference.py'),'--reference-descriptor',str(REF),'--reference-sha256',sha(REF),
             '--reference-reserve-bytes','2000000000','--character','6','--mapper','mmc3','--policy',str(policy),
             '--tag','root49p-pit-final-lift-i2','--frames','38000','--timeout','600','--record-segments','--segment-frames','512','--keep-avi']
    report=dict(status='RUNNING_PIT_I2_ORDINARY_REAL_LIFT_CONTROL',command=command,script_sha256=sha(Path(__file__)),
                policy_sha256=sha(policy),base_G_policy_sha256=sha(old),observer_sha256=sha(OUT/'observer.lua'),
                actual_H_passive_receipt_sha256=sha(H/'actual-attempt-receipt.json'),workspace_before=used,
                accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with (OUT/'native.log').open('wb')as stream:p=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    report.update(native_exit=p.returncode)
    manifest=expected/'manifest.json'
    if manifest.exists():
        m=json.loads(manifest.read_text());report.update(manifest_sha256=sha(manifest),result=m.get('result'))
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']
        assert m['config']['replay']is None and m['config']['prefix']is None
        assert not m['verified_through_2_2']and not m.get('recording_verified',False)
        report.update(assemble_exit=m.get('assemble_exit'),delivery_exit=m.get('delivery_exit'),recording_failure=m.get('recording_failure'))
        proof=expected/'playthrough-lossless.verification/report.json'
        if proof.exists():report.update(lossless_result=json.loads(proof.read_text())['result'],lossless_report_sha256=sha(proof))
    assert all(sha(ROOT/n)==v for n,v in catalog.items())
    report.update(status='COMPLETE_PIT_I2_ORDINARY_OUTCOME_RETAINED',workspace_after=workspace_bytes(ROOT),
                  qualification='Current P power-on adaptive attempt using real live-platform support and ordinary inputs. Passive hooks are data only. No independent fixed-clear, complete source/SFX review or final recording claim.')
    save();print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT/'report.json'),native_exit=p.returncode)))

if __name__=='__main__':main()
