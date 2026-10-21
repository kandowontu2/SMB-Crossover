"""Independently rehash the ordinary D Sophia clear and complete fixed replay."""
from pathlib import Path
import csv,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent-lsr-sophia-current-d-route-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-sophia-d-full-review-az.json';assert not out.exists()
    frozen=H/'freeze.json';assert sha(frozen)=='a48779654774df87837e15f8756d4ee3c15cf5325509e5671c7a91f54a9567a9'
    f=json.loads(frozen.read_text());q=H/'route-review.json';assert sha(q)==f['review_sha256'];r=json.loads(q.read_text())
    catalog=H/'file-catalog.json';assert sha(catalog)==f['catalog_sha256'];files=json.loads(catalog.read_text());assert len(files)==248
    for name,h in files.items():assert sha(H/name)==h,name
    src=H/'source-catalog.json';assert sha(src)==f['source_catalog_sha256'];sources=json.loads(src.read_text());assert len(sources)==455
    cp=Path(r['source']['checkpoint']['path']);assert sha(cp)==r['source']['checkpoint']['sha256']=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    assert sources==json.loads(cp.read_text())['source_hashes']
    for name,h in sources.items():assert sha(Path(r['source']['source'])/name)==h,name
    for info in r['source']['image'].values():
        if isinstance(info,dict)and'path'in info:assert sha(info['path'])==info['sha256']
    a=Path(r['candidate']);b=Path(r['independent_fixed']);ma=json.loads((a/'manifest.json').read_text());mb=json.loads((b/'manifest.json').read_text())
    assert sha(b/'manifest.json')==f['fixed_manifest_sha256']
    assert mb['verified_through_2_2']and not ma['verified_through_2_2']
    for m in [ma,mb]:
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        assert m['config']['character']==11 and m['config']['variant']==0
        assert m['rom_sha256']=='653ca0e82f27d9aa4a2033d9b4c68488b75ead18ae5b460bbf51bd05fa994a94'
        assert m['result']==r['result']and m['result']['cleared']and m['result']['all_six_stages']and not m['result']['deaths']
    assert sha(a/'inputs.csv')==sha(b/'inputs.csv')==f['input_sha256']
    for name,info in r['streams'].items():
        assert (a/name).read_bytes()==(b/name).read_bytes()
        assert sha(a/name)==info['candidate_sha256']==info['fixed_sha256']
    assert len(r['streams'])==9
    trace=rows(b/'trace.csv');end=[x for x in trace if x['world']=='1'and x['level']=='2'and x['engine']=='8'and x['mode']=='1'and x['task']=='3']
    assert len(trace)==25661 and len(end)==25 and end[0]['frame']=='25637'and end[0]['x']=='40'and end[-1]['x']=='67'
    ramfile=Path(r['final_RAM_snapshot']['path']);assert sha(ramfile)==r['final_RAM_snapshot']['sha256']
    ramrows=rows(ramfile);memory={int(x['address']):int(x['value'])for x in ramrows}
    assert len(ramrows)==len(memory)==10240 and set(memory)==set(range(2048))|set(range(0x6000,0x8000))
    assert all(0<=x<=255 for x in memory.values())
    dep=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('bound_D_Sophia_image',dep)
    im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(b/'smb-crossover-mmc3.nes')
    identity={n:memory[image.ram[n]]for n in ['SelectedCharacter','CrossoverBehaviorVersion','MarioVariant','BillVariant','PlayerOutlinesOff']}
    assert identity==dict(SelectedCharacter=11,CrossoverBehaviorVersion=0,MarioVariant=0,BillVariant=0,PlayerOutlinesOff=1)
    assert memory[image.ram['GameEngineSubroutine']]==8 and memory[image.ram['WorldNumber']]==1 and memory[image.ram['LevelNumber']]==2
    assert memory[image.ram['Player_X_Position']]==67
    for old in r['attempts']:assert sha(old['receipt'])==old['sha256']
    result=dict(status='PASS_ROOT_REHASHED_D_SOPHIA_FULL_FIXED_ALL_NINE_CSVS_LITERAL',script_sha256=sha(__file__),
      freeze_sha256=sha(frozen),original_review_sha256=sha(q),receipt_files_rehashed=248,source_files_rehashed=455,
      identity=identity,result=r['result'],literal_streams=list(r['streams']),next_level_control=dict(rows=25,x=[40,67]),
      fixed_single_endpoint_RAM=dict(sha256=sha(ramfile),bytes=10240,identity_and_active2_3_rechecked=True,not_two_run_RAM_equality=True),
      negative_attempt_receipts_rehashed=len(r['attempts']),fixed_manifest_sha256=sha(b/'manifest.json'),
      candidate_manifest_sha256=sha(a/'manifest.json'),limits=r['limitations'],goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),flush=True)
if __name__=='__main__':main()
