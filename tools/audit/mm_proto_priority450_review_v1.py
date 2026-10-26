"""Independent actual450 hardware/pixel comparison; preserve cadence negatives."""
from pathlib import Path
import argparse,bisect,collections,csv,hashlib,json
import numpy as np
from PIL import Image,ImageDraw

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASELINE=D/'root-presentation450-731-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,z):Path(p).write_text(json.dumps(z,indent=2)+'\n')


def rawbytes(z):
    if isinstance(z,dict):return bytes(z[str(i)]for i in range(1,257))
    return bytes(z)


def load(root):
    receipt=json.loads((root/'native-receipt.json').read_text());result=json.loads((root/'result.json').read_text())
    assert receipt['passed']and result['passed']and receipt['result']==result
    logs=[json.loads(line)for line in(root/'timing.jsonl').read_text().splitlines()]
    dm=[q['DMA']for q in logs if q['kind']=='DMA-complete']
    assert[q['id']for q in dm]==list(range(1,len(dm)+1))
    for q in dm:
        assert q['completed_writes']==256 and len(q['source'])==len(q['hardware'])==256
        assert q['source']==q['hardware']and q['mask']&24==q['end_mask']&24==0
        assert q['first']['cpu']<=q['last']['cpu']<q['complete']['cpu']
    enables=[q for q in logs if q['kind']=='render-enable']
    assert all(q['safe']and(241<=q['ppu']['scanline']<=260 or q['ppu']['scanline']==-1 and q['ppu']['dot']<=274)for q in enables)
    with(root/'direct-index.csv').open(newline='')as f:index=list(csv.DictReader(f))
    assert[int(q['ppuFrame'])for q in index]==list(range(176,451))and all(int(q['pixels'])==61440 for q in index)
    assert(root/'direct.argb').stat().st_size==len(index)*245760
    pixels=np.memmap(root/'direct.argb',dtype=np.uint8,mode='r',shape=(len(index),240,256,4))
    rgb=np.asarray(pixels[:,:,:,[2,1,0]])
    return dict(root=root,receipt=receipt,result=result,logs=logs,DMAs=dm,enables=enables,index=index,rgb=rgb)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=[load(p)for p in[BASELINE,a.candidate]]
    assert old['result']['ROM_sha256']=='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
    assert new['result']['ROM_sha256']=='00fb4a72ec9788f7b2878d6201f70a96ae6e47b4935ba186648c7edc04806a62'
    assert(BASELINE/'prefix.csv').read_bytes()==(a.candidate/'prefix.csv').read_bytes()
    def inputs(z):return[(q['poll'],q['ppu']['frame'],q['mask'])for q in z['logs']if q['kind']=='input']
    ii,jj=[inputs(q)for q in[old,new]]
    same_inputs=ii==jj
    input_diffs=[dict(index=i,baseline=x,candidate=y)for i,(x,y)in enumerate(zip(ii,jj))if x!=y]
    frames=[];times=[[q['complete']['cpu']for q in z['DMAs']]for z in[old,new]]
    for i,(left,right)in enumerate(zip(old['index'],new['index'])):
        f=int(left['ppuFrame']);assert f==int(right['ppuFrame'])
        counts=[bisect.bisect_right(t,int(q['cpuCycle']))for t,q in zip(times,[left,right])]
        snapshots=[z['DMAs'][n-1]if n else None for z,n in zip([old,new],counts)]
        arr=[rawbytes(q['source'])if q else None for q in snapshots]
        def active_parts(data):return collections.Counter(tuple(data[k:k+4])for k in range(0,256,4)if data[k]<240)if data else None
        delta=np.any(old['rgb'][i]!=new['rgb'][i],axis=2)
        yy,xx=np.nonzero(delta)
        frames.append(dict(frame=f,baseline_completed_DMA=counts[0],candidate_completed_DMA=counts[1],DMA_delta=counts[1]-counts[0],
                           baseline_capture_cpu=int(left['cpuCycle']),candidate_capture_cpu=int(right['cpuCycle']),
                           baseline_last_DMA_id=snapshots[0]['id']if snapshots[0]else None,candidate_last_DMA_id=snapshots[1]['id']if snapshots[1]else None,
                           baseline_last_DMA=snapshots[0]['complete']if snapshots[0]else None,candidate_last_DMA=snapshots[1]['complete']if snapshots[1]else None,
                           active_OAM_record_multiset_exact=active_parts(arr[0])==active_parts(arr[1]),raw_OAM_exact=arr[0]==arr[1],
                           different_RGB_pixels=int(delta.sum()),difference_box=None if not len(xx)else[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
                           baseline_RGB_sha256=hashlib.sha256(old['rgb'][i].tobytes()).hexdigest(),candidate_RGB_sha256=hashlib.sha256(new['rgb'][i].tobytes()).hexdigest()))
    selected=[184,194,204,371,372,373,403,404]
    for group,chosen in [('menu-start',[184,194,204,371]),('early-game',[372,373,403,404])]:
        sheet=Image.new('RGB',(768,4*260),'#202020');draw=ImageDraw.Draw(sheet)
        for row,frame in enumerate(chosen):
            i=frame-176
            for column,(z,label)in enumerate([(old,'731baseline'),(new,'00fbcandidate')]):
                img=Image.fromarray(z['rgb'][i]);img.save(a.output/f'{label}-{frame:06d}.png')
                draw.text((column*256,row*260),f'{label} actual{frame}',fill='white');sheet.paste(img,(column*256,row*260+20))
            diff=np.any(old['rgb'][i]!=new['rgb'][i],axis=2)
            heat=np.zeros((240,256,3),dtype=np.uint8);heat[diff]=[255,64,255]
            draw.text((512,row*260),f'RGBdiff {int(diff.sum())}pixels',fill='white');sheet.paste(Image.fromarray(heat),(512,row*260+20))
        sheet.save(a.output/f'paired-{group}-wholeframes.png')
    focus=Image.new('RGB',(1024,4*212),'#202020');draw=ImageDraw.Draw(focus)
    for row,frame in enumerate([372,373,403,404]):
        for column,(z,label)in enumerate([(old,'731baseline'),(new,'00fbcandidate')]):
            img=Image.fromarray(z['rgb'][frame-176]).crop((0,144,256,240)).resize((512,192),Image.Resampling.NEAREST)
            draw.text((column*512,row*212),f'{label} actual{frame} bottom96px x2',fill='white');focus.paste(img,(column*512,row*212+20))
    focus.save(a.output/'paired-early-game-bottom-actual.png')
    deficits=[q for q in frames if q['DMA_delta']<0]
    different=[q for q in frames if q['different_RGB_pixels']]
    summary=dict(passed=True,review_complete=True,native_run=True,adopted=False,baseline_ROM_sha256=old['result']['ROM_sha256'],candidate_ROM_sha256=new['result']['ROM_sha256'],independent_baseline_full256_DMA=len(old['DMAs']),independent_candidate_full256_DMA=len(new['DMAs']),candidate_all256_destination_exact_and_mask_disabled=True,conservative_enable_deadlines_all_pass=True,matched_controller_prefix_exact=True,actual_input_poll_frame_mask_sequence_exact=same_inputs,actual_input_differences=input_diffs,
                 native_mechanical_guards_pass=True,native_no_harm_cadence_pass=len(new['DMAs'])>=len(old['DMAs'])and not deficits,matched_completed_DMA_delta=len(new['DMAs'])-len(old['DMAs']),actual_visible_capture_prefix_deficit_frames=len(deficits),first_visible_capture_prefix_deficit=deficits[0]if deficits else None,
                 actual_lossless_pairs=len(frames),exact_RGB_pairs=len(frames)-len(different),different_RGB_pairs=len(different),first_RGB_difference=different[0]if different else None,
                 active_OAM_multiset_equal_pairs=sum(q['active_OAM_record_multiset_exact']for q in frames),selected_wholeframe_pairs=selected,
                 limits='One finite same-input MegaEasy450 startup/menu/earlygame pilot. Full401actual DMA pages and275rawframe pairs independently inspected. First8/body/shot ownership/CHR/palette/live ages/source publication/Main release were not logged; do not infer an opaque per-part or persistent projectile fairness verdict. Completion prefixes are actual observed DMA counts by matching captured visible-frame CPU cutoffs, not source-update endFrame labels. Any strict deficit remains held; a publication-cause explanation requires unlogged Main information. RGB difference is not automatically a defect.',checker_sha256=sha(__file__))
    put(a.output/'proof.json',summary);put(a.output/'all275-paired-observations.json',frames)
    deps={Path(__file__)}|{z['root']/name for z in[old,new]for name in['direct.argb','direct-index.csv','timing.jsonl','prefix.csv','native-receipt.json','result.json','launch.json','readiness.json']}
    put(a.output/'bindings.json',{str(q.resolve()):sha(q)for q in sorted(deps)})
    print(json.dumps({k:v for k,v in summary.items()if k not in['first_RGB_difference','first_visible_capture_prefix_deficit','limits']},indent=2))


if __name__=='__main__':main()
