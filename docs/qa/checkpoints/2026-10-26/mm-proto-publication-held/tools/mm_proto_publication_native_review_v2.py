"""Independently review the single a801450; preserve cadence and partial limits."""
from pathlib import Path
import argparse,bisect,collections,csv,hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from mm_proto_priority450_review_v1 import load,rawbytes

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'root-presentation450-731-v1'
OBS=D/'mm-proto-publication-ownership-v1/prepare-v2'
GAME=D/'mm-proto-publication-candidate-v3'
NATIVE=D/'mm-proto-publication-native-ready-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n')
def source(z):return rawbytes(z)
def active(s):return s['OperMode']==1 and s['OperMode_Task']==3 and s['GameEngineSubroutine']==8

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=[load(p)for p in[BASE,NATIVE]]
    assert new['result']['ROM_sha256']=='a801f8e397a416e1b12cb6b78bad25774670c8f9fea0e8334cd0c830cf8a3d56'
    assert(BASE/'prefix.csv').read_bytes()==(NATIVE/'prefix.csv').read_bytes()
    inp=lambda z:[(q['poll'],q['ppu']['frame'],q['mask'])for q in z['logs']if q['kind']=='input']
    assert inp(old)==inp(new)
    # The original731 ownership replay is byte-exact to the independent
    # reference in all five original files; this binds its added provenance.
    for n in['prefix.csv','direct-index.csv','direct.argb','timing.jsonl','result.json']:assert(BASE/n).read_bytes()==(OBS/n).read_bytes()
    rows=[json.loads(s)for s in(NATIVE/'ownership.jsonl').read_text().splitlines()]
    prior=[json.loads(s)for s in(OBS/'ownership.jsonl').read_text().splitlines()]
    dma=[[q['DMA']for q in rr if q['kind']=='DMA-source-owner']for rr in[prior,rows]]
    done=[q for q in rows if q['kind']=='DMA-completed-owner']
    assert len(dma[1])==len(new['DMAs'])==len(done)==399
    for q,x,y in zip(dma[1],done,new['DMAs']):
        assert q['id']==x['id']==y['id']
        assert source(q['source'])==source(x['hardware'])==source(y['source'])==source(y['hardware'])
    writes=[q for q in rows if q['kind']=='publication-state-write']
    bound=[];rom=(GAME/'candidate.nes').read_bytes()
    for q in writes:
        pc,bank=q['callback_pc'],q['callback_bank'];assert pc>=0x8003
        at=16+bank*8192+(pc-3)%8192;op=rom[at:at+3];operand=op[1]+256*op[2]
        assert(op[0]in[0x8d,0x0e,0x4e]and operand==0x5ff8)or(op[0]==0x9d and operand==0x5f00),(q,op.hex())
        bound.append(dict(value=q['value'],PC=pc,bank=bank,instruction=op.hex(),PPU=q['ppu'],NMI_depth=q['nmi_depth']))
    owned=[q for q in dma[1]if active(q['state'])and q['state']['MmPublicationState']&128]
    phases=[q['state']['MmPublicationState']for q in owned]
    assert phases==[128,192]*23
    ack=[q for q in writes if q['nmi_depth']==1 and q['callback_bank']==66]
    assert[q['value']for q in ack]==[64,0]*23
    returns=[q for q in rows if q['kind']=='NMI-return']
    assert len(returns)==442 and all('MmPublicationState'in q['state']and 'ObjectVerticalFlip'in q['state']for q in returns)
    body_rows=[]
    for q in owned:
        roster=q['last_roster'];s=roster['state'];assert source(roster['source'])==source(q['source'])
        assert q['state']['ObjectVerticalFlip']==s['ObjectVerticalFlip']==0
        S=s['RgOamPlayerStart'];B=s['CurrentOAMOffset']-S;Rsv=44 if s['ProtoVariant']else 40
        assert 0<=S<=256-Rsv and S%4==B%4==0 and 0<B<=Rsv,(q['id'],S,B)
        shot=bool(q['state']['MmPublicationState']&64);body_start=S if shot else 0;shot_start=0 if shot else Rsv
        data=source(q['source']);bset=set(range(body_start//4,(body_start+B)//4));sset=set(range(shot_start//4,(shot_start+S)//4))
        def selected(indices):
            rejects=[];accepts=[]
            for y in range(240):
                candidates=[i for i in range(64)if data[i*4]<240 and data[i*4]<y<=data[i*4]+8]
                live=set(candidates[:8]);demand=set(candidates)&indices
                if demand-live:rejects.append(dict(y=y,indices=sorted(demand-live)))
                if demand&live:accepts.append(y)
            return dict(rejected_scanlines=len(rejects),rejected_record_scanlines=sum(len(z['indices'])for z in rejects),first_rejections=rejects[:4],selected_scanlines=len(accepts))
        body_rows.append(dict(DMA=q['id'],PPU=q['start'],Roster=roster['id'],Main=roster['main'],phase='shots'if shot else'body',S=S,B=B,body_start=body_start,shot_start=shot_start,
                              body_first8=selected(bset),shots_first8=selected(sset),actual_ObjectVerticalFlip=s['ObjectVerticalFlip'],live_ordinary=s['ordinary'],live_special=s['special'],source_exact_completed_Roster=True))
    pairs=[];times=[[q['complete']['cpu']for q in z['DMAs']]for z in[old,new]]
    for i,(left,right)in enumerate(zip(old['index'],new['index'])):
        f=int(left['ppuFrame']);assert f==int(right['ppuFrame'])
        counts=[bisect.bisect_right(t,int(q['cpuCycle']))for t,q in zip(times,[left,right])]
        oo=[dma[j][n-1]if n else None for j,n in enumerate(counts)]
        delta=np.any(old['rgb'][i]!=new['rgb'][i],axis=2);yy,xx=np.nonzero(delta)
        posekeys=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','ObjectMetasprite','PlayerFacingDir']
        states=[q['last_roster']['state']if q and q.get('last_roster')else{}for q in oo]
        shared=[n for n in posekeys if all(n in x for x in states)]
        pairs.append(dict(frame=f,baseline_completed_DMA=counts[0],candidate_completed_DMA=counts[1],DMA_delta=counts[1]-counts[0],candidate_last_DMA_phase=None if not oo[1]else oo[1]['state']['MmPublicationState'],
                          candidate_source_roster=None if not oo[1]or not oo[1].get('last_roster')else oo[1]['last_roster']['id'],
                          baseline_last_complete=None if not counts[0]else old['DMAs'][counts[0]-1]['complete'],candidate_last_complete=None if not counts[1]else new['DMAs'][counts[1]-1]['complete'],
                          published_pose_shared_fields=shared,published_pose_fields_exact=bool(shared)and all(states[0][n]==states[1][n]for n in shared),different_RGB_pixels=int(delta.sum()),difference_box=None if not len(xx)else[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]))
    deficits=[q for q in pairs if q['DMA_delta']<0]
    selected_frames=[184,194,204,371,372,373,403,404,441,445,449,450]
    for page in range(0,len(selected_frames),4):
        chosen=selected_frames[page:page+4];sheet=Image.new('RGB',(768,len(chosen)*260),'#202020');draw=ImageDraw.Draw(sheet)
        for row,f in enumerate(chosen):
            for col,(z,label)in enumerate([(old,'731baseline'),(new,'a801publication')]):
                im=Image.fromarray(z['rgb'][f-176]);im.save(a.output/f'{label}-{f:06d}.png');draw.text((col*256,row*260),f'{label} actual{f}',fill='white');sheet.paste(im,(col*256,row*260+20))
            diff=np.any(old['rgb'][f-176]!=new['rgb'][f-176],axis=2);heat=np.zeros((240,256,3),dtype=np.uint8);heat[diff]=[255,64,255]
            draw.text((512,row*260),f'RGBdiff {int(diff.sum())}',fill='white');sheet.paste(Image.fromarray(heat),(512,row*260+20))
        sheet.save(a.output/f'paired-wholeframes-{page//4+1}.png')
    # All active frames are retained in finite paired galleries, including
    # repeated displays/lag. These images establish actual pixels, not an
    # invented opaque part attribution without captured CHR/palettes.
    for start in range(372,451,8):
        chosen=range(start,min(start+8,451));sheet=Image.new('RGB',(1024,len(chosen)*212),'#202020');draw=ImageDraw.Draw(sheet)
        for row,f in enumerate(chosen):
            for col,(z,label)in enumerate([(old,'731'),(new,'a801')]):
                im=Image.fromarray(z['rgb'][f-176]).crop((0,144,256,240)).resize((512,192),Image.Resampling.NEAREST)
                draw.text((col*512,row*212),f'{label} actual{f}',fill='white');sheet.paste(im,(col*512,row*212+20))
        sheet.save(a.output/f'paired-active-bottom-{start}.png')
    put(a.output/'all275-pairs.json',pairs);put(a.output/'actual-owned-publications.json',body_rows);put(a.output/'all108-tag-writers.json',bound)
    summary=dict(passed=True,review_complete=True,native_run=True,adopted=False,release_suitable=False,
                 baseline_ROM_sha256=old['result']['ROM_sha256'],candidate_ROM_sha256=new['result']['ROM_sha256'],mechanical_guards_all_pass=True,baseline_full256_DMA=len(old['DMAs']),candidate_full256_DMA=len(new['DMAs']),actual_input_poll_frame_mask_sequence_exact=True,
                 no_harm_cadence_pass=False,physical_DMA_net_delta=len(new['DMAs'])-len(old['DMAs']),visible_prefix_deficit_frames=len(deficits),first_deficit=deficits[0]if deficits else None,
                 actual_Rosters=48,actual_owned_consumed_constructions=len(owned),actual_owned_phase_sequence=phases,actual_body_and_shot_turns=23,all46_completed_source_images_exact_to_actual_DMA_source=True,
                 actual_source_tag_ack_writes=len(ack),actual_phase_writes_bound_to_compiled_opcodes=len(bound),actual_Vflip_zero_on_all_owned_DMAs=True,
                 body_priority_turns_with_any_first8_body_record_rejection=sum(x['phase']=='body'and bool(x['body_first8']['rejected_scanlines'])for x in body_rows),
                 shot_priority_turns_with_any_first8_body_record_rejection=sum(x['phase']=='shots'and bool(x['body_first8']['rejected_scanlines'])for x in body_rows),
                 body_priority_turns_with_any_first8_shot_record_rejection=sum(x['phase']=='body'and bool(x['shots_first8']['rejected_scanlines'])for x in body_rows),
                 shot_priority_turns_with_any_first8_shot_record_rejection=sum(x['phase']=='shots'and bool(x['shots_first8']['rejected_scanlines'])for x in body_rows),
                 physical_source_Y_first8_selection_only=True,opaque_pixel_attribution_proved=False,all275_actual_lossless_pairs=True,exact_RGB_pairs=sum(not x['different_RGB_pixels']for x in pairs),selected_wholeframe_pairs=selected_frames,
                 limits='ONE same-input450 MegaEasy startup/earlygame. No native retry/Proto/death/later areas/natural weapon/campaign or performance-ready claim. First8 record selection derives actual full hardware OAM/Y under bound8sprite limit; alpha/CHR/palette ownership was not captured, so this is not opaque-body/shot pixel attribution. Actual RGB pairs are retained separately. Full source ownership and Vine partial-image problem remain separate. Net3 fewer actual transfers disqualifies adoption even though46 consumed tagged construction phases alternate.',tool_sha256=sha(__file__))
    put(a.output/'proof.json',summary)
    deps={Path(__file__),R/'tools/audit/mm_proto_priority450_review_v1.py',GAME/'candidate.nes',GAME/'candidate.dbg'}|{z['root']/n for z in[old,new]for n in['direct.argb','direct-index.csv','timing.jsonl','prefix.csv','native-receipt.json','result.json','launch.json','readiness.json']}|{OBS/'ownership.jsonl',NATIVE/'ownership.jsonl',NATIVE/'ownership-config.json'}
    put(a.output/'bindings.json',{str(p.resolve()):sha(p)for p in sorted(deps)})
    print(json.dumps({k:v for k,v in summary.items()if k not in['first_deficit','actual_owned_phase_sequence','limits']},indent=2))
if __name__=='__main__':main()
