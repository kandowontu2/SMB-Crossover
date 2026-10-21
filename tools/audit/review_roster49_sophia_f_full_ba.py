"""Independently verify Sophia's unchanged-current-build complete fixed replay."""
from pathlib import Path
import csv,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent-lsr-sophia-current-f-route-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-sophia-f-full-review-ba.json';assert not out.exists()
    frozen=H/'freeze.json';assert sha(frozen)=='c9ee2d3ac612539ad6bc041bd493cacc55b9816a689cf309db35944332ea70b8'
    f=json.loads(frozen.read_text());q=H/'route-review.json';assert sha(q)==f['review_sha256'];r=json.loads(q.read_text())
    catalog=H/'file-catalog.json';assert sha(catalog)==f['catalog_sha256'];files=json.loads(catalog.read_text());assert len(files)==101
    for name,h in files.items():assert sha(H/name)==h,name
    src=H/'source-catalog.json';assert sha(src)==f['source_catalog_sha256'];sources=json.loads(src.read_text());assert len(sources)==457
    prep=r['preparation'];cp=Path(prep['checkpoint']['path']);assert sha(cp)==prep['checkpoint']['sha256']=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    c=json.loads(cp.read_text());assert sources==c['source_hashes']
    for name,h in sources.items():assert sha(Path(prep['source'])/name)==sha(R/name)==h,name
    for name,h in c['generated11'].items():assert sha(R/'build/generated'/name)==h,name
    for b in c['builds']:
        for info in b['artifacts'].values():assert sha(R/info['path'])==sha(R/info['frozen_path'])==info['sha256']
    for image in prep['images'].values():
        for info in image.values():
            if isinstance(info,dict)and'path'in info:assert sha(info['path'])==info['sha256']
    a=Path(r['candidate']);b=Path(r['independent_fixed']);ma=json.loads((a/'manifest.json').read_text());mb=json.loads((b/'manifest.json').read_text())
    assert sha(b/'manifest.json')==f['fixed_manifest_sha256']and mb['verified_through_2_2']and not ma['verified_through_2_2']
    for p,m in [(a,ma),(b,mb)]:
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        assert m['config']['character']==11 and m['config']['variant']==0 and m['config']['mapper']=='mmc3'
        assert m['rom_sha256']==sha(p/'smb-crossover-mmc3.nes')=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
        assert m['result']==r['result']and m['result']['cleared']and m['result']['all_six_stages']and not m['result']['deaths']and not m['result']['failure']
        summary=json.loads((p/'stomp-summary.json').read_text());assert not summary['illegal_guest_events']and not summary['resident_opcode_mismatches']and summary['behavior_version']==0
    assert sha(a/'inputs.csv')==sha(b/'inputs.csv')==f['input_sha256']
    for name,info in r['streams'].items():
        assert (a/name).read_bytes()==(b/name).read_bytes()
        assert sha(a/name)==info['candidate_sha256']==info['fixed_sha256']
    assert len(r['streams'])==9
    trace=rows(b/'trace.csv');end=[x for x in trace if x['world']=='1'and x['level']=='2'and x['engine']=='8'and x['mode']=='1'and x['task']=='3']
    assert len(trace)==25404 and len(end)==25 and end[0]['frame']=='25380'and end[0]['x']=='40'and end[-1]['x']=='67'
    assert not [z for z in trace if z['engine']=='11']
    ramfile=Path(r['endpoint_RAM']['path']);assert sha(ramfile)==r['endpoint_RAM']['sha256'];rr=rows(ramfile)
    memory={int(x['address']):int(x['value'])for x in rr}
    assert len(rr)==len(memory)==10240 and set(memory)==set(range(2048))|set(range(0x6000,0x8000))
    assert all(0<=x<=255 for x in memory.values())
    dep=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('actual_F_Sophia_root',dep)
    im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(b/'smb-crossover-mmc3.nes')
    identity={n:memory[image.ram[n]]for n in ['SelectedCharacter','CrossoverBehaviorVersion','MarioVariant','BillVariant','PlayerOutlinesOff']}
    assert identity==dict(SelectedCharacter=11,CrossoverBehaviorVersion=0,MarioVariant=0,BillVariant=0,PlayerOutlinesOff=1)
    assert memory[image.ram['GameEngineSubroutine']]==8 and memory[image.ram['WorldNumber']]==1 and memory[image.ram['LevelNumber']]==2 and memory[image.ram['Player_X_Position']]==67
    for old in r['attempts']:assert sha(R/old['receipt'])==old['sha256']
    result=dict(status='PASS_ROOT_CURRENT_F_SOPHIA_COMPLETE_FIXED_NINE_WHOLE_STREAMS_LITERAL',script_sha256=sha(__file__),
      freeze_sha256=sha(frozen),original_review_sha256=sha(q),receipt_files_rehashed=101,source_files_rehashed=457,main_generated_rehashed=11,primary_artifacts_rehashed=8,
      identity=identity,result=r['result'],literal_streams=list(r['streams']),next_level_control=dict(rows=25,x=[40,67]),
      fixed_single_endpoint_RAM=dict(sha256=sha(ramfile),bytes=10240,identity_and_active2_3_rechecked=True,not_two_run_RAM_equality=True),
      negative_and_positive_attempt_receipts_rehashed=len(r['attempts']),fixed_manifest_sha256=sha(b/'manifest.json'),candidate_manifest_sha256=sha(a/'manifest.json'),
      limits=r['scope'],goal_complete=False,final_recording_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),flush=True)
if __name__=='__main__':main()
