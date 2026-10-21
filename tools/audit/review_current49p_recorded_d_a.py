"""All-row telemetry review of the two retained exploratory D recordings."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-recorded-d-frame-review-a.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    parent=ROOT/'build/verification/root49p-pit-rygar-live-d/report.json'
    assert sha(parent)=='7264d5851b76bfd4ff55fac8ab768b6a28cf9e156d1e3a9b3fae4d65ee76a2a3'
    report=dict(status='PASS_RETAINED_D_TELEMETRY_ALL_ROWS_WITH_NEGATIVE_GAMEPLAY',
                script_sha256=sha(Path(__file__)),parent_report_sha256=sha(parent),cases=[],
                accepted_release=False,goal_complete=False,visual_frame_by_frame_source_review_complete=False)
    for case in json.loads(parent.read_text())['cases']:
        folder=Path(case['expected']);manifest=json.loads((folder/'manifest.json').read_text())
        assert manifest['assemble_exit']==manifest['delivery_exit']==0
        proof=folder/'playthrough-lossless.verification/report.json'
        assert json.loads(proof.read_text())['result']=='passed-exact-rgb-and-pcm'
        oam=list(csv.DictReader((folder/'oam.csv').open()))
        maximums=Counter();overloaded=0;hudFrames=0
        for row in oam:
            raw=bytes.fromhex(row['oamHex']);assert len(raw)==256
            edges=[0]*257;visible=hud=0
            for at in range(0,256,4):
                y=raw[at]+1
                if y<240:
                    visible+=1;hud+=y<32
                    first,last=max(32,y),min(240,y+16)
                    if first<last:edges[first]+=1;edges[last]-=1
            count=maximum=0
            for y in range(32,240):count+=edges[y];maximum=max(maximum,count)
            assert (visible,hud,maximum)==tuple(int(row[k])for k in ('visible','hudSprites','maxSprites'))
            maximums[maximum]+=1;overloaded+=maximum>8;hudFrames+=hud>0
        renders=list(csv.DictReader((folder/'render.csv').open()))
        active=[r for r in renders if all(int(r[k])==v for k,v in [('mode',1),('task',3),('engine',8),('screenDisabled',0)])]
        audio=Counter(r['event']for r in csv.DictReader((folder/'audio-events.csv').open()))
        trace=list(csv.DictReader((folder/'trace.csv').open()));deltas=[]
        for a,b in zip(trace,trace[1:]):
            if all(a[k]==b[k]for k in ('world','level','area','areaType'))and a['engine']==b['engine']=='8':
                deltas.append(dict(frame=int(b['frame']),delta=int(b['camera'])-int(a['camera'])))
        stomp=json.loads((folder/'stomp-summary.json').read_text());assert stomp['illegal_guest_events']==stomp['resident_opcode_mismatches']==0
        report['cases'].append(dict(character=case['name'],result=manifest['result'],
            actual_oam_rows=len(oam),max_sprites_histogram=dict(sorted(maximums.items())),
            overloaded_oam_rows=overloaded,hud_visible_oam_rows=hudFrames,
            active_render_rows=len(active),active_rows_lag_NMI=sum(int(r['lagNmi'])for r in active),
            source_flight_rows=sum(int(r['pitFlight'])!=0 for r in active),audio_queue_events=dict(audio),
            max_same_area_camera_step=max((abs(d['delta'])for d in deltas),default=0),
            camera_steps_above4=[d for d in deltas if abs(d['delta'])>4],
            illegal_stomp_summary=stomp,lossless_report_sha256=sha(proof),
            retained_media=case['retained_media'],
            actual_csv_hashes={n:sha(folder/n)for n in ['oam.csv','render.csv','trace.csv','audio-events.csv','scroll-writes.csv']}))
    report['qualification']='All committed DMA rows and gameplay telemetry were examined; native video RGB and PCM are verified lossless. These are failed adaptive attempts, not final/fixed clears. Sprite counts quantify potential NES scanline overflow, not character-specific disappearance; queue presence does not prove every required SFX or visual/source parity.'
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT),cases=[{k:c[k]for k in ['character','actual_oam_rows','overloaded_oam_rows','active_render_rows','active_rows_lag_NMI','max_same_area_camera_step']}for c in report['cases']])))

if __name__=='__main__':main()
