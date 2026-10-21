"""Root independent execution of the frozen Bill/Lance F complete proof packet."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'specialist-bill-lance-current-f-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=V/'root49-lance-f-full-review-ca.json';assert not out.exists()
 pins={'phase-freeze-ak.json':'5aa9f6b7fb1e6c348d14311fd0ac888a57ada93c3aed32d30a306affbc1479d4','phase-handoff-ak.json':'7ecc17e40173fc368e57364b321318458c8e8d1d107209025f03c775b976394c','review-ak.py':'119ab17defe14cfface2c825c76fbbd48aa1126d2703b42287e77b1807f87bc1'}
 for n,h in pins.items():assert sha(H/n)==h,n
 q=subprocess.run([sys.executable,str(H/'review-ak.py'),'--catalogue-sha256',pins['phase-freeze-ak.json'],'--handoff-sha256',pins['phase-handoff-ak.json']],cwd=R,capture_output=True,text=True)
 assert q.returncode==0,q.stdout+q.stderr;review=json.loads(q.stdout)
 cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
 assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
 for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
 for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
 for b in c['builds']:
  for info in b['artifacts'].values():assert sha(R/info['path'])==sha(R/info['frozen_path'])==info['sha256']
 out.write_text(json.dumps(dict(status='PASS_ROOT_F_BILL_AND_LANCE_EASY_MMC3_FULL_FROZEN_PROOFS',script_sha256=sha(__file__),pins=pins,independently_executed_review=review,checkpoint_sha256=sha(cp),current_main_rehashed=dict(sources=457,generated=11,artifacts=8),scope='Bill34401/Lance33254 physical frames,all six stages,zero deaths and25 real2-3 controls40to70 each; full original21-field byte-identical traces and actual DMA snapshots. Frozen F/MMC3/Easy only; remaining arsenal,MMC5,current successor,media and source-perfect claims remain open.',goal_complete=False),indent=2)+'\n')
 print('ROOT_F_BILL_LANCE',sha(out),flush=True)
if __name__=='__main__':main()
