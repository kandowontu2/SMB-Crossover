"""Read-only bounded five-route pixel/scroll triage, never a visual PASS oracle.

Streams every saved frame twice, preserving source byte hashes. A fitted
ground phase and actual-world majority reference rank suspicious intervals;
neither supplies missing physical OAM/PPU scroll-state observations.
"""
from pathlib import Path
import csv,hashlib,json,struct,time
import numpy as np
from final_inventory_compact_capture_v1 import MAGIC,HEADER,decode,word_fnv
from current_roster_compact_11_v1 import ROOT,sha,png
from current_darkwing_stairs_prepare_v1 import compiled_map
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location

ROM=ROOT/'build/zelda2_easy_glove.nes'
EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
PROFILES={
 'link':'compact-326942-link-easy-v2',
 'zelda2':'compact-326942-zelda2-easy-v4',
 'octopus':'compact-326942-octopus-easy-v1',
 'twinbee':'compact-326942-twinbee-easy-v1',
 'pentarou':'compact-326942-pentarou-easy-v1'}
OUT=ROOT/'build/current326-five-route-visual-scan-v3'
SELECTIONS=[('link',873),('zelda2',988),('octopus',3261),('octopus',3557),
            ('twinbee',1382),('twinbee',3513),('pentarou',3169),('pentarou',3506)]
HEIGHT,WIDTH=208,4096
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def frame_records(folder):
    """Same RLE decoder; NumPy XOR. Full decoded SHA must equal prior receipt.

    Per-record FNV is not rerun: exact header/index plus the previously
    verified full-stream SHA authenticate all decoded bytes independently.
    """
    index=[q for q in map(json.loads,(folder/'captures-index.jsonl').read_text().splitlines())if q['type']=='record']
    previous=None;stream=hashlib.sha256();count=0
    with(folder/'captures.nesppuv1').open('rb')as f:
        assert f.read(16)==MAGIC
        while header:=f.read(HEADER.size):
            at=f.tell()-HEADER.size;kind,mode,reserved,sequence,ml,pl,checksum=HEADER.unpack(header)
            assert kind==1 and reserved==0 and sequence==count+1
            m=json.loads(f.read(ml));payload=f.read(pl);assert len(payload)==pl and m['decoded_bytes']==245760
            raw=payload if mode==0 else decode(1,payload,None,245760)
            if mode==2:
                assert previous is not None
                raw=np.bitwise_xor(np.frombuffer(raw,dtype=np.uint8),np.frombuffer(previous,dtype=np.uint8)).tobytes()
            assert mode in[0,1,2]and len(raw)==245760
            previous=raw;stream.update(raw);count+=1
            actual=dict(type='record',record=sequence,offset=at,bytes=f.tell()-at,kind=kind,mode=mode,name=m['name'],decoded_bytes=len(raw),stamp=m['stamp'],full_ordinal=m['full_ordinal'],word_fnv1a32=checksum)
            assert actual==index[count-1]
            yield actual,raw
    review=json.loads((folder/'review.json').read_text())
    assert count==review['container']['full_frames']and stream.hexdigest()==review['container']['decoded_full_sha256']

def decoder_controls():
    previous=bytes(range(256))*960
    payload=b''.join(bytes([127])+previous[i:i+512]for i in range(0,len(previous),512))
    raw=decode(1,payload,None,245760);assert raw==previous
    expected=decode(2,payload,previous,245760)
    assert np.bitwise_xor(np.frombuffer(raw,dtype=np.uint8),np.frombuffer(previous,dtype=np.uint8)).tobytes()==expected==bytes(245760)
    assert word_fnv(raw)==word_fnv(previous)
    return dict(literal_RLE_and_XOR_exact=True,raw_size=245760)

def complete_columns(b):
    # The reused stair helper stops at column161. Extend the genuine parser
    # to the full observed level; absent dictionary entries cannot be used
    # as an all-air ground registration mask at the final pyramid/castle.
    old=compiled_map(b);q=Arena(b,12)
    q.put(DarkwingVariant=1,AreaPointer=37,AreaType=1,WorldNumber=0,LevelNumber=0)
    q.invoke('GetAreaDataAddrs')
    assert q.get('AreaDataLow')+256*q.get('AreaDataHigh')==address(b,'L_GroundArea6')+2
    q.array('AreaObjectLength',[255]*3);cols={}
    for col in range(256):
        q.put(CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32)
        q.invoke('AreaParserCore')
        cols[col]=[q.get('Block_Buffer_1',col%32//16*208+row*16+col%16)for row in range(13)]
    assert all(cols[k]==v for k,v in old.items())
    return cols

def body_box(row,cam):
    return max(0,row['x']-cam-48),max(32,row['y']-24),min(256,row['x']-cam+80),min(240,row['y']+64)

def player_mask(row,cam):
    mask=np.ones((208,256),dtype=bool);l,t,r,b=body_box(row,cam)
    if l<r and t<b:mask[t-32:b-32,l:r]=False
    return mask

def intervals(rows,field,predicate):
    result=[];start=None;previous=None
    for r in rows:
        if predicate(r[field]):
            if start is None:start=r
            previous=r
        elif start is not None:
            result.append(dict(first=start['frame'],last=previous['frame'],captured_frames=previous['ordinal']-start['ordinal']+1,peak=max(x[field]for x in rows[start['ordinal']-1:previous['ordinal']])));start=None
    if start is not None:result.append(dict(first=start['frame'],last=previous['frame'],captured_frames=previous['ordinal']-start['ordinal']+1))
    return result

def main():
    assert sha(ROM)==EXPECTED and not OUT.exists();OUT.mkdir()
    b=scoped_load(ROM);cols=complete_columns(b)
    floor=np.array([cols.get(x//16,[0]*13)[11]==84 for x in range(WIDTH)])
    mutable_ids=set(b['raw'][location(b,'BrickQBlockMetatiles'):location(b,'BrickQBlockMetatiles')+14])|{0x51,0x52,0x88}
    mutable=np.zeros((HEIGHT,WIDTH),dtype=bool)
    for col,values in cols.items():
        for row,tile in enumerate(values):
            if tile in mutable_ids:
                # A bump animates a sprite above its original metatile.
                mutable[max(0,row*16-16):min(HEIGHT,row*16+32),max(0,col*16-8):col*16+24]=True
    atlas=np.zeros((HEIGHT,WIDTH),dtype=np.uint32);votes=np.zeros((HEIGHT,WIDTH),dtype=np.int32);seen=np.zeros((HEIGHT,WIDTH),dtype=np.int32)
    profiles={};template=None;template_owner=None;bindings={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(ROM.relative_to(ROOT)):sha(ROM)}
    for file in [ROM.with_suffix('.dbg'),ROOT/'tools/audit/final_inventory_compact_capture_v1.py',ROOT/'src/player.s',ROOT/'src/game.s',ROOT/'src/reset.s',ROOT/'src/collision.s',ROOT/'src/level_tiles.s']:
        bindings[str(file.relative_to(ROOT))]=sha(file)
    ys=np.arange(216,240,4);xs=np.arange(0,256,2);clock=time.time()
    for name,folder_name in PROFILES.items():
        folder=ROOT/'build/verification'/folder_name
        for file in ['ready.json','result.json','review.json','trace.csv','inputs.csv','captures.nesppuv1','captures-index.jsonl']:
            bindings[str((folder/file).relative_to(ROOT))]=sha(folder/file)
        trace={int(r['frame']):{k:int(v)for k,v in r.items()}for r in csv.DictReader((folder/'trace.csv').open(newline=''))}
        result=json.loads((folder/'result.json').read_text());review=json.loads((folder/'review.json').read_text())
        assert result['passed']and result['ROM_sha256']==EXPECTED and result['actual_mode']==0
        metrics=[];previous=None;previous_cam=None;hud=None;counts=dict(all_frames=0,active_1_1=0,excluded=0,identical_consecutive=0,active_identical_consecutive=0);rawsha=hashlib.sha256()
        for meta,raw in frame_records(folder):
            frame=meta['stamp']['ppu_frame'];q=trace[frame];a=np.frombuffer(raw,dtype='<u4').reshape(240,256);rawsha.update(raw);counts['all_frames']+=1
            r=dict(frame=frame,ordinal=meta['full_ordinal'],x=q['x'],y=q['y'],engine=q['engine'],world=q['world'],level=q['level'],camera_recorded=q['camera'],captured_gap=1 if previous is None else frame-previous['frame'],eligible=int(q['world']==q['level']==0 and q['engine']==8 and q['task']==3),camera_fit=q['camera'],ground_bad=0,ground_samples=0,camera_delay=0,ground_y_phase=0,adjacent_changed=0,hud_changed=0,hud_checked=0,atlas_static_changed=0,atlas_mutable_changed=0,atlas_checked=0,body_residual=-1)
            if template is None and r['eligible']and q['camera']==0 and np.unique(a[208:240,:16]).size>=3:
                template=a[208:240,:16].copy();template_owner=dict(identity=name,frame=frame,raw_sha256=hashlib.sha256(raw).hexdigest())
            if r['eligible']and template is not None:
                counts['active_1_1']+=1;cams=sorted({trace[max(1,frame-d)]['camera']for d in range(11)})
                scored=[];got=a[ys[:,None],xs]
                for cam in cams:
                    if not 0<=cam<=WIDTH-256:continue
                    use=floor[xs+cam];want=template[(ys-208)[:,None],(xs+cam)%16]
                    bad=int(np.count_nonzero((got!=want)[:,use]));total=int(use.sum())*len(ys)
                    scored.append((bad/max(1,total),abs(cam-q['camera']),bad,total,cam))
                score,_,bad,total,cam=min(scored)
                assert total>0,('No measured ground phase',name,frame,cam)
                r.update(camera_fit=cam,ground_bad=bad,ground_samples=total,camera_delay=q['camera']-cam)
                if score>.08:
                    phase_scores=[]
                    for dy in range(-8,8):
                        want=template[(ys-208-dy)%16][:,(xs+cam)%16];use=floor[xs+cam]
                        phase_scores.append((int(np.count_nonzero((got!=want)[:,use])),abs(dy),dy))
                    if min(phase_scores)[0]<bad*.3:r['ground_y_phase']=min(phase_scores)[2]
                region=a[32:240];mask=player_mask(q,cam)
                av=atlas[:,cam:cam+256];vv=votes[:,cam:cam+256];ss=seen[:,cam:cam+256]
                replace=(vv==0)&mask;av[replace]=region[replace]
                agree=(av==region)&mask;disagree=(~agree)&mask
                vv[agree]+=1;vv[disagree]-=1;ss[mask]+=1
                hh=np.concatenate([a[8:16,144:184].ravel(),a[8:16,200:240].ravel()])
                if hud is None and frame>=int(result['first_active']if 'first_active'in result else result['markers']['first-active']['frame'])+10:hud=hh.copy()
                if hud is not None:r.update(hud_changed=int(np.count_nonzero(hh!=hud)),hud_checked=640)
                if previous is not None and previous['eligible']:
                    delta=cam-previous_cam
                    if 0<=delta<=12:
                        before=previous['a'][32:208,delta:];after=a[32:208,:256-delta]
                        use=mask[:176,:256-delta]&previous['mask'][:176,delta:]
                        r['adjacent_changed']=int(np.count_nonzero((before!=after)&use))
                previous_cam=cam
            else:counts['excluded']+=1
            if previous is not None and raw==previous['raw']:
                counts['identical_consecutive']+=1
                if r['eligible']and previous['eligible']:counts['active_identical_consecutive']+=1
            metrics.append(r);previous=dict(frame=frame,raw=raw,a=a.copy(),mask=player_mask(q,r['camera_fit']),eligible=r['eligible'])
        assert rawsha.hexdigest()==review['container']['decoded_full_sha256']and counts['all_frames']==result['full_frames']
        profiles[name]=dict(folder=str(folder.relative_to(ROOT)),native=result,counts=counts,raw_stream_sha256=rawsha.hexdigest(),metrics=metrics)
        print(json.dumps(dict(pass_number=1,identity=name,frames=counts['all_frames'],eligible=counts['active_1_1'],seconds=round(time.time()-clock,2))),flush=True)
    reliable=(seen>=8)&(votes*2>=seen)
    selected_images={};selected_meta={};body_window=[]
    for name,z in profiles.items():
        folder=ROOT/z['folder'];metrics=z['metrics'];assert len(metrics)==z['counts']['all_frames']
        for meta,raw in frame_records(folder):
            r=metrics[meta['full_ordinal']-1]
            if not r['eligible']:continue
            cam=r['camera_fit'];a=np.frombuffer(raw,dtype='<u4').reshape(240,256);region=a[32:240];reli=reliable[:,cam:cam+256]
            mask=player_mask(r,cam);difference=(region!=atlas[:,cam:cam+256])&reli;mut=mutable[:,cam:cam+256]
            r['atlas_static_changed']=int(np.count_nonzero(difference&mask&~mut));r['atlas_mutable_changed']=int(np.count_nonzero(difference&mask&mut));r['atlas_checked']=int(np.count_nonzero(reli&mask&~mut))
            l,t,right,bottom=body_box(r,cam)
            if l<right and t<bottom and 24<r['x']-cam<232 and 40<=r['y']<208:
                check=reli[t-32:bottom-32,l:right]
                if np.count_nonzero(check)>500:r['body_residual']=int(np.count_nonzero(difference[t-32:bottom-32,l:right]))
            if(name,r['frame'])in SELECTIONS:
                selected_images[name,r['frame']]=raw;selected_meta[name,r['frame']]=meta
            if name=='octopus'and(3255<=r['frame']<=3266 or r['frame']==3557):
                cx=r['x']-cam;left,top,right,bottom=cx-16,r['y']-8,cx+16,r['y']+24
                body_window.append(dict(frame=r['frame'],trace_x=r['x'],trace_y=r['y'],fitted_camera=cam,
                    coarse_box=[l,t,min(256,cx+80),min(240,r['y']+64)],coarse_residual=r['body_residual'],
                    core_inspection_box=[left,top,right,bottom],core_reference_pixels=int(np.count_nonzero(reli[top-32:bottom-32,left:right])),
                    core_residual_pixels=int(np.count_nonzero(difference[top-32:bottom-32,left:right]))))
        print(json.dumps(dict(pass_number=2,identity=name,seconds=round(time.time()-clock,2))),flush=True)
    fields=list(next(iter(profiles.values()))['metrics'][0]);csvpath=OUT/'all-frame-metrics.csv'
    with csvpath.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=['identity']+fields);w.writeheader()
        for name,z in profiles.items():
            for row in z['metrics']:w.writerow(dict(identity=name,**row))
    summary={}
    for name,z in profiles.items():
        rows=z.pop('metrics');eligible=[r for r in rows if r['eligible']]
        peaks={key:sorted(eligible,key=lambda r:r[key],reverse=True)[:12]for key in['ground_bad','adjacent_changed','atlas_static_changed','atlas_mutable_changed','hud_changed']}
        lowbody=[r for r in eligible if 0<=r['body_residual']<=12]
        summary[name]=dict(folder=z['folder'],counts=z['counts'],raw_stream_sha256=z['raw_stream_sha256'],peak_candidates=peaks,
            camera_delay_pixels={str(k):sum(r['camera_delay']==k for r in eligible)for k in sorted({r['camera_delay']for r in eligible})},
            strong_vertical_ground_phase_candidates=[r for r in eligible if r['ground_y_phase']],
            low_body_residual_candidates=dict(count=len(lowbody),first=lowbody[:12],scope='Coarse background-consensus residual, not physical sprite ownership or a visibility verdict.'),
            quantiles={k:{str(q):float(np.quantile([r[k]for r in eligible],q))for q in[0,.5,.9,.99,1]}for k in['ground_bad','adjacent_changed','atlas_static_changed','atlas_mutable_changed','hud_changed']})
    assert len(selected_images)==8
    sheet=OUT/'eight-additional-whole-frames.png';png(sheet,[selected_images[p]for p in SELECTIONS])
    placements=[dict(identity=n,frame=f,row=i//2,column=i%2,metadata=selected_meta[n,f],raw_sha256=hashlib.sha256(selected_images[n,f]).hexdigest())for i,(n,f)in enumerate(SELECTIONS)]
    put(OUT/'placements.json',placements)
    proof=dict(scan_completed=True,visual_pass_claim=False,native_run=False,ROM_sha256=EXPECTED,total_full_frames=sum(z['counts']['all_frames']for z in profiles.values()),
        all_decoded_streams_exact_prior_verified_SHA256=True,decoder_controls=decoder_controls(),ground_template=template_owner,consensus_reference=dict(source='Actual five streams after fitted horizontal camera, player rectangle excluded; Boyer-Moore majority',reliable_world_pixels=int(reliable.sum()),world_canvas_pixels=HEIGHT*WIDTH,minimum_observations=8,minimum_vote_ratio=.5),
        profiles=summary,metrics_sha256=sha(csvpath),bindings=bindings,selected_whole_frames=dict(path=str(sheet.relative_to(ROOT)),sha256=sha(sheet),placements=placements,agent_visual_review=False),
        octopus_body_window=dict(rows=body_window,scope='Trace-centred empirical background residual; core32x32 is a declared inspection box, not the unknown actual PnFrame art mask. No physical OAM/hurt/source-pose attribution.'),
        limitations='Every raw frame decoded and aggregate-hash verified; only active world0/level0 gets pixel metrics. Ground phase uses recorded camera history and static floor pattern, not observed hardware scroll registers. Majority pixels are empirical and can miss common persistent corruption; enemies, animation, source-sanctioned block mutations and epoch lag can trigger residuals. Physical OAM/CHR/art ownership and hurt/blink flags are absent in these route captures. Coarse body-box residual is not an eight-sprite or full-fidelity proof. This tool ranks actual images for manual review; it is not a green all-visual/audio/gameplay certification.')
    put(OUT/'scan.json',proof);print(json.dumps(dict(scan_completed=True,report=str(OUT/'scan.json'),sha256=sha(OUT/'scan.json'),total_full_frames=proof['total_full_frames']),indent=2))

if __name__=='__main__':main()
