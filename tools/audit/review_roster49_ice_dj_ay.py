"""Independently reexecute the frozen Ice packet without modifying its receipts."""
from pathlib import Path
import hashlib,json,traceback
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'agent49-samus-bill-arsenal-a';D=V/'root49-ice-state-review-ay'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COMMANDS=[('review_cleanup_df.py','cleanup-review-df.json'),
 ('review_state_ct.py','state-lifecycle-protocol-review-ct.json'),
 ('review_protocol_cx.py','protocol-constructor-review-cx.json'),
 ('review_palette_bw.py','palette-layout-abi-cost-bw.json'),
 ('check_ice_dh.py','ice-source-predicate-dh.json'),
 ('review_phase_di.py','phase-cost-review-di.json'),
 ('review_state_co.py','state-compiled-review-co.json'),
 ('review_cost_reset_dg.py','cost-reset-review-dg.json')]
def main():
    assert not D.exists();D.mkdir()
    frozen=A/'ice-state-freeze-dj/freeze.json';assert sha(frozen)=='fc0cc5716511979cd1345479a2ca1e3bd1f0170f0bfa90f409c88994cb13f084'
    f=json.loads(frozen.read_text());receipt=Path(f['receipts']['path']);assert sha(receipt)==f['receipts']['sha256']
    cat=json.loads(receipt.read_text());assert len(cat)==229
    for n,h in cat.items():assert sha(A/n)==h['sha256'],n
    sc=Path(f['source_catalog']['path']);assert sha(sc)==f['source_catalog']['sha256'];sources=json.loads(sc.read_text());assert len(sources)==457
    for n,h in sources.items():assert sha(Path(f['source_path'])/n)==h,n
    for b in f['builds']:
        for item in b['artifacts'].values():
            if isinstance(item,dict)and'path'in item:assert sha(item['path'])==item['sha256']
    for source in f['source_anchors']:assert sha(source['path'])==source['sha256']
    for n,h in f['generated_inputs'].items():assert sha(Path(f['source_path'])/n)==h,n
    cp=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    for n,h in c['source_hashes'].items():
        if n not in f['owned_overlay']['paths']and n not in['src/characters.s','src/sophia_source_terrain.s']:
            assert sources[n]==h,('Unowned ancestry difference',n)
    pre=dict(status='REHASHED_FROZEN_DJ_READY_FOR_ROOT_REEXECUTION',freeze_sha256=sha(frozen),
      script_sha256=sha(__file__),receipts=len(cat),sources=len(sources),
      owned_overlay=f['owned_overlay'],preserve_D_files=['src/characters.s','src/sophia_source_terrain.s'],
      main_changed=False,goal_complete=False)
    (D/'rehash.json').write_text(json.dumps(pre,indent=2)+'\n')
    reports=[]
    try:
        for script,output in COMMANDS:
            p=A/script;assert sha(p)==cat[script]['sha256'],script
            text=p.read_text();anchor="H/'"+output+"'";assert text.count(anchor)==1,(script,text.count(anchor))
            adapted=text.replace(anchor,'Path('+repr(str(D/output))+')')
            adapter=D/script;adapter.write_text(adapted)
            print('START',script,flush=True)
            exec(compile(adapted,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
            report=json.loads((D/output).read_text());assert report['status'].startswith('PASS'),report['status']
            assert sha(D/output)==f['reports'][output],('Output differs from frozen report',output)
            reports.append(dict(script=script,script_sha256=sha(p),adapter_sha256=sha(adapter),report=output,sha256=sha(D/output),status=report['status']))
            (D/'progress.json').write_text(json.dumps(dict(status='RUNNING',reports=reports),indent=2)+'\n')
            print('END',script,flush=True)
        for n,h in cat.items():assert sha(A/n)==h['sha256'],n
        for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
        result=dict(status='PASS_ROOT_REEXECUTED_FROZEN_DJ_PACKET_NOT_YET_COMPOSED_OR_ADOPTED',
          script_sha256=sha(__file__),rehash_sha256=sha(D/'rehash.json'),reports=reports,
          limits=f['limitations'],cost=f['cost'],main_changed=False,goal_complete=False)
        (D/'review.json').write_text(json.dumps(result,indent=2)+'\n')
        print('DONE',len(reports),sha(D/'review.json'),flush=True)
    except Exception as ex:
        (D/'host-or-review-negative.json').write_text(json.dumps(dict(status='FAIL_RETAINED_NO_ADMISSION',error=repr(ex),traceback=traceback.format_exc(),completed_reports=reports),indent=2)+'\n')
        raise
if __name__=='__main__':main()
