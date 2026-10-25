"""Assemble bounded, exact-hash native evidence without adopting the proposal."""
from pathlib import Path
import argparse,csv,json
from PIL import Image,ImageDraw
from mmc3_native_v42_qualify import D,V,ROOT,EXPECTED,sha

def read(p):return json.loads(p.read_text())
def sheet(paths,out,labels=None):
    image=Image.new('RGB',(1024,260*((len(paths)+3)//4)),(24,28,36));draw=ImageDraw.Draw(image)
    for i,p in enumerate(paths):
        with Image.open(p)as im:image.paste(im.convert('RGB'),(i%4*256,i//4*260+20))
        draw.text((i%4*256+4,i//4*260+3),(labels[i]if labels else p.stem),fill='white')
    image.save(out)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);assert sha(V/'candidate.nes')==EXPECTED
    route_dirs=[D/'mmc3-native-v42-sophia-easy-v1',D/'mmc3-native-v42-chip-easy-v1']
    hard=D/'mmc3-native-v42-sophia-hard-v4'
    if(hard/'proof.json').exists()and read(hard/'proof.json')['passed']:route_dirs.append(hard)
    routes=[]
    for folder in route_dirs:
        proof=read(folder/'proof.json');assert proof['passed']and proof['ROM_sha256']==EXPECTED
        route=Path(proof['route']);scroll=list(csv.DictReader((route/'scroll-writes.csv').open()))
        visible=[r for r in scroll if r['engine']=='8'and r['mode']=='1'and r['task']=='3'and r['world']==r['level']=='0'and r['screenDisabled']=='0'and r['renderingEnabled']=='1']
        assert visible and all(r['scanline']=='31'and r['writerBank']=='254'for r in visible)
        routes.append(dict(folder=str(folder),proof_sha256=sha(folder/'proof.json'),identity=proof['identity'],mode=proof['mode'],result=proof['result'],guards=proof['guards'],visible_scroll_writes=len(visible),visible_scroll_scanlines=[31],visible_scroll_actual_writer_banks=[254]))
    direct=D/'mmc3-native-v42-direct-sophia-easy-v1';pixels=read(direct/'proof.json')
    assert pixels['passed']and pixels['ROM_sha256']==EXPECTED
    for n in ['full-smc-guard','mmc3-cache-guard','completed-loop-motion']:assert read(direct/(n+'.json'))['passed']
    index=list(csv.DictReader((direct/'direct-frame-index.csv').open()))
    assert [int(r['frame'])for r in index]==list(range(200,pixels['result']['frames']))
    chosen=[int(index[round(i*(len(index)-1)/15)]['frame'])for i in range(16)]
    overview=out/'sophia-easy-direct-overview.png';sheet([direct/'frames'/f'{n:06d}.png'for n in chosen],overview)
    cold=D/'mmc3-native-v42-cold-v1';coldproof=read(cold/'proof.json');assert coldproof['passed']
    captures=[];labels=[]
    for row in coldproof['runs']:
        for stage in ['selection','lives','entry']:
            captures.append(cold/row['identity']/(stage+'.png'));labels.append(row['identity']+' '+stage)
    coldsheet=out/'cold-menu-lives-overview.png';sheet(captures,coldsheet,labels)
    perf=D/'mmc3-native-v42-performance-v3';timing=read(perf/'proof.json');assert timing['passed']and timing['saved_cycles_per_matched_column']==[2990]
    failures=[]
    for name in ['mmc3-native-v42-sophia-hard-v1','mmc3-native-v42-sophia-hard-v2','mmc3-native-v42-sophia-hard-v3','mmc3-native-v42-sophia-hard-v4']:
        folder=D/name
        if(folder/'proof.json').exists():
            fail=read(folder/'proof.json')
            if fail['passed']:continue
            failures.append(dict(folder=str(folder),proof_sha256=sha(folder/'proof.json'),result=fail['result'],architecture_assertion_failure=False,
                                 minimum_SP=fail['guards']['full-smc-guard']['minimum_SP_from_stack_write_addresses'],
                                 maximum_committed_world_step=fail['guards']['completed-loop-motion']['max_world_step'],
                                 maximum_camera_step=fail['guards']['completed-loop-motion']['max_camera_step'],
                                 note='Ordinary native contact death stops the no-death harness. Code/bank/stack/motion assertions did not fail before contact; this is not a Hard clear or architecture pass.'))
    tools=[ROOT/'tools/audit'/n for n in ['mmc3_native_v42_qualify.py','mmc3_native_v42_profile.py','mmc3_native_v42_cold.py','mmc3_native_v42_packet.py']]
    q=dict(bounded_qualification_passed=True,full_native_qualified=False,goal_complete=False,adopted=False,
           ROM_path=str(V/'candidate.nes'),ROM_sha256=EXPECTED,baseline_ROM_sha256=timing['baseline']['ROM_sha256'],
           active_recipe_untouched=True,current_download_untouched=True,source_untouched=True,
           full_routes=routes,cold_entries=dict(proof=str(cold/'proof.json'),sha256=sha(cold/'proof.json'),identities=[r['identity']for r in coldproof['runs']],passed=True),
           independent_Sophia_Easy_PPU=dict(proof=str(direct/'proof.json'),sha256=sha(direct/'proof.json'),physical_frames=pixels['direct_frames'],raw_bytes=pixels['raw_stream_bytes'],fixed_inputs_trace_exact=True,PNG_RGB_exact=True,lossless_raw_roundtrip=True),
           native_timing=dict(proof=str(perf/'proof.json'),sha256=sha(perf/'proof.json'),matched_columns=timing['matched_native_columns'],cycles_saved_per_column=[2990],baseline_updates=128,candidate_updates=128,baseline_active_physical_frames=185,candidate_active_physical_frames=185,updates_per_physical_frame=128/185,cold_to_endpoint_physical_frames=[timing['baseline']['actual_physical_frames'],timing['candidate']['actual_physical_frames']],constant_60Hz_established=False),
           retained_failures=failures,
           retained_timing_revisions=[dict(folder=str(D/'mmc3-native-v42-performance-v1'),reason='Physical-input full-prefix replay diverges in route/cadence; old timing observer omitted7-cycle interrupt hardware entry. Retained as diagnostic; authoritative matched native measurement is performance-v3.'),dict(folder=str(D/'mmc3-native-v42-performance-v2'),reason='Long constant-fire baseline fixture reached ordinary contact death before256updates. Preserved; bounded same-position128update scene passes in performance-v3.')],
           visual_samples=[dict(path=str(overview),sha256=sha(overview)),dict(path=str(coldsheet),sha256=sha(coldsheet))],
           owned_tools=[dict(path=str(p),sha256=sha(p))for p in tools],
           sampled_visual_review=dict(reviewed=True,scope='Viewed16sampled actual direct Sophia PPU frames plus four selection/lives/entry contact sheets. Selected portraits and stage geometry are legible in these samples; no obvious full-screen terrain displacement. Cold screenshots use retained asynchronous screenshot API and are samples, not independent pixel replays or exhaustive art review.'),
           remaining_requirements=['Independent fixed-input Sophia Hard PPU replay; its ordinary-controller guarded fullroute already passes.','Remaining current-hash roster cold entries/fullroutes and mode-specific/powerup/transition/warp/music mixer cases.','Broader matched native performance scenes and full-route cadence; reduced parser cost alone did not improve this185-frame active cadence.','Independent Chip/cold/menu/lives PPU replays and full art/audio/pose review; initial life samples do not establish all respawn/power-state portraits.','Exact rebuild/integration and full architecture qualification before any adoption; accepted recipe and MMC5 download remain unchanged.'],
           scope='Bounded exact-hash private MMC3 native architecture evidence. Strict six-byte tiny code and49-byte resident common, SP>=5b, all five operand fields across native NMI, actual banks, CHR/cache/OAM/VBlank and completed-loop world<=8/camera0..4. Sophia independent PPU frames retained. No full-roster/all-items/release or60Hz claim.')
    (out/'proof.json').write_text(json.dumps(q,indent=2))
    (out/'README.txt').write_text('PRIVATE V42 BOUNDED NATIVE QUALIFICATION\n\nROM SHA256 '+EXPECTED+'\nNot adopted; no full-roster/release/60Hz claim.\n\nPassing ordinary-controller zero-death1-1 routes:\nSophia Easy5524physicalframes; Sophia Hard5850; Chip Easy4663.\nThe Hard controller preserves the original navigation and uses8physical-poll B pulses; earlier contact deaths remain retained.\nAll strict6byte tiny/49byte common/SP>=5b/5SMC/NMI/bank/cache/OAM/committed motion guards remain enabled.\nAll visible gameplay scroll writes are actual bank254/scanline31.\n\nIndependent Sophia Easy replay:5324actualPPUframes, exact original input/trace, every saved PNG RGB verified,1,308,554,016raw bytes round-tripped losslessly.\nFour cold selections/lives full mapped-family CHR checks: Sophia Hard, Chip Easy, ZeldaII Easy, Vic Easy.\n\nMatched current-source V39 baseline SHA acebfc87a2cae899017f468bb4cedc539787dd510d9b3485caa49f3b6fd4f891.\n30matched real13row native columns save exactly2990cycles each.\nBoth versions complete128updates across185activephysicalframes and finish atX225/Y176. No measured cadence improvement.\nCold-to-endpoint frames721baseline/710candidate; broader route/performance work remains.\n\nAuthoritative measurements and retained failed fixtures are listed in proof.json.\nRoot source, active recipe, Downloads and Git were not edited by this task.\n')
    print(json.dumps(dict(packet=str(out),ROM_sha256=EXPECTED,routes=[(r['identity'],r['mode'],r['result']['frames'])for r in routes],proof_sha256=sha(out/'proof.json'))),flush=True)

if __name__=='__main__':main()
