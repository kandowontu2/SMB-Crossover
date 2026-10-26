"""Freeze first641 route FALSE and offline Hard2056 sprite-limit diagnosis."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'luigi-profile641-route-ready-v4';N=P/'discovery';OUT=P/'failure-freeze-v3'
H=D/'luigi-profile641-native-ready-v2/luigi-hard'
BOUT=D/'luigi-profile641-Hard2056-contention-v3'
ROM='641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        while z:=f.read(2**20):h.update(z)
    return h.hexdigest()
def get(p):return json.loads(Path(p).read_text())
def rows(p):
    with Path(p).open()as f:return list(csv.DictReader(f))
def put(p,z):assert not p.exists(),p;p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def oam(row):
    z=bytes.fromhex(row['oamHex']);assert len(z)==256
    return [dict(slot=i,y=z[4*i],tile=z[4*i+1],attribute=z[4*i+2],x=z[4*i+3])for i in range(64)]


def analyze():
    assert sha(P/'readiness.json')=='a2117bb3d06b610b220ce93903a050193db0869360c3ea6be6f564978672ad0a'
    assert sha(P/'source-preparation-seal.json')=='c496a83b68e04a938aab64b3f8ace8f46b29a033cdc5ddce03dd3572398042ee'
    for p,key in [(P/'readiness.json','bindings'),(P/'source-preparation-seal.json','additional_bindings')]:
        for f,h in get(p)[key].items():assert sha(f)==h,f
    OUT.mkdir(exist_ok=False);BOUT.mkdir(exist_ok=False)
    native=get(P/'native-proof.json');assert not native['passed'] and native['actual_native_launches']==1 and native['retries']==0 and native['native_worker_released']
    assert not(P/'replay/result.json').exists() and not(P/'replay/native-host.log').exists()
    result=get(N/'result.json');assert result['failure']=='death' and result['frames']==1396 and result['deaths']==0
    trace=rows(N/'trace.csv');state={int(z['frame']):z for z in trace};inputs=rows(N/'inputs.csv')
    assert all(z['power']=='0'for z in trace if int(z['frame'])>=371)
    assert state[1395]['engine']=='8' and state[1396]['engine']=='11'
    assert state[1395]['y']=='175'and state[1395]['vy']=='5'and state[1395]['state']=='1'
    assert state[1396]['x']=='1959'and state[1396]['y']=='176'and state[1396]['vy']=='252'
    assert all(z['mask']=='65'for z in inputs if int(z['frame'])>=1334)
    # All actual raw DMA rows are independently checked despite overall FALSE.
    dma_count=0;start_count=0;pending_starts=[];safe_enables=0
    with(N/'ability-dma-epochs.jsonl').open()as f:
        for line in f:
            z=json.loads(line)
            if z['kind']=='completed-DMA-before-render-enable':
                dma_count+=1;assert z['id']==dma_count
                assert len(z['source'])==len(z['hardware'])==len(z['writes'])==256
                assert z['source']==z['hardware'] and z['differences']=={}
                assert z['start']['pc']==0xe005 and z['complete']['pc']==0xe008
                assert z['page']==2 and z['start']['oamaddr']==z['complete']['oamaddr']==0
                assert z['start']['mask']&24==z['complete']['mask']&24==0
                assert [w['value']for w in z['writes']]==z['source']
                assert [w['stamp']['oamaddr']for w in z['writes']]==list(range(256))
                assert all(w['stamp']['mask']&24==0 for w in z['writes'])
            elif z['kind']=='startFrame-hardware':
                start_count+=1
                if z.get('pending_dma_id')is not None:pending_starts.append(dict(stamp=z['stamp'],pending=z['pending_dma_id'],completed=z.get('completed_dma_id')))
            elif z['kind']=='actual-PPUMASK-write'and z['scoped']and z['enabling']:safe_enables+=1;assert z['safe']
    obs=[json.loads(x)for x in (N/'route-observation.jsonl').read_text().splitlines()]
    kinds=collections.Counter(z['kind']for z in obs)
    assert kinds['NMI-entry']==kinds['NMI-return']==1388 and kinds['IRQ-entry']==kinds['IRQ-return']==1330
    assert kinds['actual-ordinary-stomp-entry']==kinds['actual-ordinary-stomp-return']==0
    idx=rows(N/'actual-ppu-index.csv');assert len(idx)==1396 and (N/'actual-ppu.argb').stat().st_size==1396*245760
    assert [int(z['ordinal'])for z in idx]==[int(z['ppuFrame'])for z in idx]==list(range(1,1397))
    selected=[371,620,700,760,830,920,1080,1200,1250,1300,1332,1360,1384,1392,1395,1396]
    frames=[]
    with(N/'actual-ppu.argb').open('rb')as f:
        for ordinal in selected:
            f.seek((ordinal-1)*245760);raw=f.read(245760);assert len(raw)==245760
            a=np.frombuffer(raw,dtype='<u4').reshape(240,256)
            rgb=np.stack(((a>>16)&255,(a>>8)&255,a&255),axis=2).astype(np.uint8)
            p=OUT/f'actual-{ordinal:06d}.png';Image.fromarray(rgb).save(p)
            frames.append(dict(ordinal=ordinal,path=str(p),PNG_sha256=sha(p),raw_sha256=hashlib.sha256(raw).hexdigest(),source_offset=(ordinal-1)*245760,trace=state[ordinal]))
    sheets=[]
    for j in range(0,len(frames),8):
        group=frames[j:j+8];im=Image.new('RGB',(2048,1056),'#172132');draw=ImageDraw.Draw(im)
        for i,q in enumerate(group):
            x,y=i%4*512,i//4*528;draw.text((x+4,y+5),f"f{q['ordinal']} x{q['trace']['x']} y{q['trace']['yHigh']}:{q['trace']['y']} power{q['trace']['power']}",fill='white')
            im.paste(Image.open(q['path']).convert('RGB').resize((512,480),Image.Resampling.NEAREST),(x,y+36))
        p=OUT/f'route-failure-selected-{j//8+1}.png';im.save(p);sheets.append(dict(path=str(p),sha256=sha(p)))
    # Native cadence facts are descriptive on this new route, not a matched
    # performance comparison to any historical ROM/controller outcome.
    active_idx=[z for z in idx if 371<=int(z['ordinal'])<=1396]
    def longest(field):
        streak=best=0
        for a,b in zip(active_idx,active_idx[1:]):
            streak=streak+1 if a[field]==b[field]else 0;best=max(best,streak)
        return best
    facts=dict(passed=False,component_only=True,ROM_sha256=ROM,native_launches=1,retries=0,worker_released=True,replay_unrun=True,
        actual_first_failure=dict(physical_frame=1396,condition='Actual GameEngineSubroutine11 death',actual_life_decrement_counter=0,lives=2,
             prior_frame=state[1395],failure_frame=state[1396],mode=0,identity=8,variant=1),
        physical_mushroom_flower_claim=False,player_remains_small_power0_entire_route=True,
        source_controller='Unchanged historical Mario adaptive controller; initialUpgrade is set true once1-1 X>420 even without collection. This exposes a route-policy coverage gap, not evidence that native physical pickups fail.',
        ending_trajectory=trace[-100:],last_inputs=inputs[-100:],
        completed_DMA256=dma_count,DMA_data_write_checks=dma_count*256,startFrame_snapshots=start_count,pending_starts=pending_starts,
        scoped_safe_enables=safe_enables,actual_NMI_entry_returns=1388,actual_IRQ_entry_returns=1330,
        ordinary_stomp_entries_returns=0,CHR=get(N/'chr-commit.json'),motion=get(N/'completed-loop-motion.json'),
        all_endFrame_PPU=1396,raw_PPU_sha256=sha(N/'actual-ppu.argb'),selected_whole_images=frames,sheets=sheets,
        cadence=dict(active_physical_frames=len(active_idx),active_update_entry_delta=int(active_idx[-1]['updates'])-int(active_idx[0]['updates']),
                     active_draw_delta=int(active_idx[-1]['draws'])-int(active_idx[0]['draws']),active_committed_delta=int(active_idx[-1]['commits'])-int(active_idx[0]['commits']),
                     longest_consecutive_no_draw_frames=longest('draws'),longest_consecutive_no_update_frames=longest('updates'),
                     observed_NmiSkipped_start=int(active_idx[0]['NmiSkipped']),observed_NmiSkipped_end=int(active_idx[-1]['NmiSkipped']),matched_old_ROM_comparison=False),
        attribution='Actual pixels/live contact require separate review; endpoint death cannot yet be called a physics/collision defect or waived as controller-only. No retry or retuning authorized.')
    put(OUT/'component-evidence.json',facts)
    # Historical item observer logs DMA source at PREVIOUS endFrame number.
    # Actual displayed2056 retained the most recent DMA logged2054 (display2055).
    render={int(z['frame']):z for z in rows(H/'render.csv')}
    assert render[2055]['dmaCount']=='1'and render[2056]['dmaCount']=='0'and render[2056]['lagNmi']=='1'
    oldoam=rows(H/'oam.csv');row2054=next(z for z in oldoam if z['frame']=='2054')
    sprites=oam(row2054);body=[sprites[i]for i in [0,61,62,63]]
    assert [(z['slot'],z['tile'],z['y'],z['x'])for z in body]==[(0,56,177,114),(61,60,193,122),(62,60,193,114),(63,58,177,122)]
    lines=[]
    for y in range(178,210):
        live=[z for z in sprites if z['y']+1<=y<z['y']+17 and z['y']<239]
        lines.append(dict(scanline=y,admitted_slots=[q['slot']for q in live[:8]],all_overlap_slots=[q['slot']for q in live],
                          player_slots_admitted=[q['slot']for q in live[:8]if q['slot']in [0,61,62,63]]))
    assert all(not q['player_slots_admitted']for q in lines if 194<=q['scanline']<=208)
    last=lines[-1];assert last['scanline']==209 and last['player_slots_admitted']==[61,62]
    actual=Image.open(H/'frames/002056.png').convert('RGB')
    lower=collections.Counter(actual.getpixel((x,y))for y in range(194,208)for x in range(114,130))
    assert lower=={(146,144,255):145,(136,216,0):64,(0,0,0):15}
    hstate=next(z for z in rows(H/'trace.csv')if z['frame']=='2056')
    assert hstate['state']=='0'and hstate['power']=='2'and hstate['y']=='176'
    chrrow=next(z for z in rows(H/'chr-commit.csv')if z['frame']=='2056')
    assert chrrow['expected']==chrrow['actual']=='132'and chrrow['bodyParts']=='4'and chrrow['bad']=='0'
    put(BOUT/'component-evidence.json',dict(passed=True,ROM_sha256=ROM,diagnostic_only=True,game_changed=False,new_native_launches=0,
        target_display_frame=2056,actual_state=hstate,render2055=render[2055],render2056=render[2056],CHR=chrrow,
        previous_endFrame_DMA_log=2054,corresponding_completed_display_frame=2055,source_OAM= row2054,
        body_parts=body,eight_sprite_scanline_model=lines,lower_ROI=dict(x=[114,129],y=[194,207],pixels=[dict(RGB=list(k),count=v)for k,v in lower.items()]),
        interpretation='Grounded FireLuigi lower halves are authored in the retained source OAM but excluded by first-eight sprite evaluation on194..208. Terminal209 admits both lower halves and is explicitly NOT labeled excluded or transparent. Lower actual image ROI194..207 contains only sky/hill/black, no white/red/orange Fire palette. This is substantial sprite-contention dropout, not air pose or missing source body tiles; lagged display retains the unlucky rotation.',
        limits='Old item observer logs source OAM at4014, not a complete256hardware completion sample. Temporal association uses actual DMA counts/observer order and matching CHR/body parts; this is a concrete source/first-eight/pixel diagnosis, not retrospective full-hardware timing certification.',
        correction='Original42-placement no-obvious-body-corruption wording is too broad: Hard2056 has real lower-body dropout. Original checkpoint and reviewed files stay unchanged; this is an additive correction.'))
    crop=actual.crop((96,168,152,224)).resize((448,448),Image.Resampling.NEAREST);crop.save(BOUT/'Hard2056-player-neighbor-enlargement.png')
    print(json.dumps(dict(route_FALSE=True,replay_unrun=True,fullPPU=1396,DMA=dma_count,starts=start_count,enables=safe_enables,
                         Hard2056_diagnosis='source-first-eight sprite contention, grounded, lag-retained rotation'),indent=2))


def freeze():
    for out in [OUT,BOUT]:
        review=get(out/'agent-visual-review.json');assert review['actual_whole_images_reviewed']and not review['everyframe_claim']
        files=dict(get(P/'readiness.json')['bindings'])
        files.update(get(P/'source-preparation-seal.json')['additional_bindings'])
        files.update({str(f):sha(f)for p in [P]for f in p.rglob('*')if f.is_file()})
        for f in [Path(__file__),ROOT/'docs/qa/luigi-profile641-route-failure-2026-10-26.txt',ROOT/'docs/qa/luigi-profile641-Hard2056-contention-2026-10-26.txt']:
            files[str(f)]=sha(f)
        for n in ['trace.csv','render.csv','oam.csv','chr-commit.csv','audit.lua','frames/002056.png']:files[str(H/n)]=sha(H/n)
        for p in [BOUT]:
            for f in p.rglob('*'):
                if f.is_file():files[str(f)]=sha(f)
        for f,h in files.items():assert sha(f)==h,f
        put(out/'proof.json',dict(passed=out==BOUT,native_route_passed=False,ROM_sha256=ROM,new_native_launches=1 if out==OUT else 0,
            retries=0,native_worker_released=True,replay_unrun=True,game_changed=False,bindings=files,
            diagnostic_only=out==BOUT,previous_42placement_checkpoint_preserved=True))
        print(json.dumps(dict(path=str(out/'proof.json'),sha256=sha(out/'proof.json'),bindings=len(files)),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');a=p.parse_args();freeze()if a.freeze else analyze()
