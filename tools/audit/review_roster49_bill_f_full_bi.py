"""Independent root execution and additional current-main checks for Bill F."""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'specialist-bill-lance-current-f-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-bill-f-full-review-bi.json';assert not out.exists()
    hashes={'phase-freeze-w.json':'a3ffd5b95e666c43375072cce83c24f8931d2e27d7f4ff4d596c0d96e82ada21',
      'phase-handoff-w.json':'c75de87894b372eb59964bda9e03e5ec3f1b1217e4c22c817c63563a6944245f',
      'review-w.py':'4656e76cd8f9044a71fe53e6e49423d2433945a9ebe968b6f8a32a6e0dbc2e66'}
    for n,h in hashes.items():assert sha(H/n)==h,n
    q=subprocess.run([sys.executable,str(H/'review-w.py'),'--catalogue-sha256',hashes['phase-freeze-w.json'],'--handoff-sha256',hashes['phase-handoff-w.json']],cwd=R,capture_output=True,text=True)
    assert q.returncode==0,q.stdout+q.stderr;review=json.loads(q.stdout)
    assert review['files']==2375 and review['native_packets']==22 and review['unknown']==[]and review['result']['cleared']
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['generated11'].items():assert sha(R/'build/generated'/n)==h,n
    for b in c['builds']:
        for info in b['artifacts'].values():assert sha(R/info['path'])==sha(R/info['frozen_path'])==info['sha256']
    a=R/'build/roster-through-2-2/specialist-f-bill-responsive-u-3-v0-mmc3'
    b=R/'build/roster-through-2-2/specialist-f-bill-fixed-v-3-v0-mmc3'
    ma,mb=[json.loads((p/'manifest.json').read_text())for p in [a,b]]
    assert not ma['verified_through_2_2']and mb['verified_through_2_2']
    assert mb['rom_sha256']==sha(b/'smb-crossover-mmc3.nes')=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
    assert mb['config']['character']==3 and mb['config']['variant']==0 and mb['config']['mapper']=='mmc3'
    aa,bb=rows(a/'trace.csv'),rows(b/'trace.csv')
    fields=['frame','poll','world','level','area','areaType','x','y','yHigh','state','vx','vy','power','engine','mode','task','lives','camera','buttons']
    assert len(aa)==len(bb)==34401 and all(all(x[k]==y[k]for k in fields)for x,y in zip(aa,bb))
    excluded={k:sum(x[k]!=y[k]for x,y in zip(aa,bb))for k in aa[0]if k not in fields}
    assert rows(a/'bill-telemetry.csv')==rows(b/'bill-telemetry.csv')
    assert (a/'inputs.csv').read_bytes()==(b/'inputs.csv').read_bytes()
    oam=rows(b/'oam.csv');render=rows(b/'render.csv')
    import collections
    dma=collections.Counter({int(z['frame'])-1:int(z['dmaCount'])for z in render if int(z['dmaCount'])})
    assert collections.Counter(int(z['frame'])for z in oam)==dma
    assert all(len(bytes.fromhex(z['oamHex']))==256 for z in oam)
    result=dict(status='PASS_ROOT_CURRENT_F_BILL_EASY_MMC3_COMPLETE_FIXED',script_sha256=sha(__file__),pinned_packet=hashes,independently_executed_review=review,
      checkpoint_sha256=sha(cp),current_main_rehashed=dict(sources=457,generated=11,artifacts=8),
      discovery_manifest_sha256=sha(a/'manifest.json'),fixed_manifest_sha256=sha(b/'manifest.json'),
      movement_19_fields_exact_rows=34401,native_16_fields_exact_rows=33902,input_sha256=sha(b/'inputs.csv'),
      extra_trace_fields_actual_differences=excluded,whole_trace_bytes_identical=(a/'trace.csv').read_bytes()==(b/'trace.csv').read_bytes(),
      actual_DMA_snapshots_rechecked=len(oam),OAM_callback_epoch='Previous completed endFrame; render frame is callback frame+1.',
      limits=review['qualification'],all_weapons_complete=False,final_recording_complete=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),excluded,flush=True)
if __name__=='__main__':main()
