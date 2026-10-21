"""Review the current-hash Ryu fixed replay and optional native recording."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
DISCOVERY=ROOT/'build/roster-through-2-2/agent47-ryu-aj-10-v0-mmc3'
FIXED=ROOT/'build/roster-through-2-2/root48-ryu-fixed-a-10-v0-mmc3'
INPUT_SHA='53bbf9012edba6bfa73b835bd6b45f3fd45843adcbdac6e325bd97a22c4bbee6'
FILES=('audio-events.csv','chr.csv','events.csv','inputs.csv','oam.csv',
       'render.csv','scroll-writes.csv','stomp-events.csv','trace.csv')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def route(folder,rom_hash):
    m=read(folder/'manifest.json')
    assert m['verified_through_2_2']and m['full_frame_audit']
    assert m['controller_only']and not m['memory_or_register_writes']
    assert m['rom_sha256']==rom_hash and m['inputs_sha256']==sha(folder/'inputs.csv')==INPUT_SHA
    assert not m['config']['allowDeaths']and not m['config']['prefix']
    assert m['config']['character']==10 and m['config']['variant']==0 and m['config']['replay']
    assert m['result']['cleared']and m['result']['all_six_stages']
    assert m['result']['frames']==23432 and m['result']['polls']==23431
    assert m['result']['deaths']==0 and m['result']['failure']is None
    assert m['result']['stage_entries']['1-2']==23408
    stomp=read(folder/'stomp-summary.json')
    assert stomp['events']==stomp['illegal_guest_events']==stomp['resident_opcode_mismatches']==0
    assert stomp['nested_interrupt_guards']and stomp['failure']is None
    return dict(path=folder.relative_to(ROOT).as_posix(),manifest_sha256=sha(folder/'manifest.json'),
        result=m['result'],stomp_summary_sha256=sha(folder/'stomp-summary.json'))

def exact_csvs(before,after):
    results={}
    for n in FILES:
        a,b=before/n,after/n
        assert a.read_bytes()==b.read_bytes(),('Retained every-row stream mismatch',n)
        results[n]=dict(sha256=sha(b),bytes=b.stat().st_size,literal_equal=True)
    return results

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--tag',required=True)
    p.add_argument('--recorded',type=Path)
    a=p.parse_args()
    assert a.tag and all(c.isalnum()or c in '-_'for c in a.tag)
    out=ROOT/'build/verification'/('ryu48-full-route-review-'+a.tag)
    assert not out.exists()
    accepted_path=ROOT/'build/checkpoints/roster-audit-v48/manifest.json'
    assert sha(accepted_path)=='fd0770c5058acd0522008f341427878495dadcbb7dd8cbf0e3db1eb934684102'
    accepted=read(accepted_path)
    rom=ROOT/'build/checkpoints/roster-audit-v48/smb-crossover-mmc3.nes'
    assert sha(rom)==accepted['roms']['mmc3']
    fixed=route(FIXED,sha(rom))
    comparison=exact_csvs(DISCOVERY,FIXED)
    rows=list(csv.DictReader((FIXED/'trace.csv').open(newline='')))
    assert len(rows)==23432
    steps=[]
    for old,new in zip(rows,rows[1:]):
        if not all(old[k]==new[k]for k in ('world','level','area','yHigh')):continue
        if old['engine']!='8'or new['engine']!='8':continue
        dx,dy=int(new['x'])-int(old['x']),int(new['y'])-int(old['y'])
        if abs(dx)>8 or abs(dy)>16:steps.append(dict(frame=int(new['frame']),dx=dx,dy=dy,before=old,after=new))
    report=dict(result='fixed-replay-verified',script_sha256=sha(Path(__file__)),
        accepted_manifest_sha256=sha(accepted_path),rom_sha256=sha(rom),fixed=fixed,
        discovery_vs_fixed=comparison,normal_movement_large_steps=steps,
        frame_rows=len(rows),manual_full_video_review=False,
        qualification='Every captured audit stream matches the ordinary-input discovery. This is traversal/recording evidence, not proof of all enemy/pickup collection, every weapon in this route, or complete source audiovisual fidelity.')
    if a.recorded:
        recorded=a.recorded.resolve()
        report['recorded']=route(recorded,sha(rom))
        m=read(recorded/'manifest.json')
        assert m['recording_verified']and m['native_parts_retained']
        assert m['assemble_exit']==m['delivery_exit']==0
        assert m['recording_metadata']['passed']
        assert not(recorded/'capture-budget-stop.json').exists()
        assert m['capture_bridge_source_sha256']=='03e9bf92fb2bdf716ec67e9b0503a2b4e9f14adca6c83b02c55b7cbf20efb535'
        proof=recorded/'playthrough-lossless.verification/report.json'
        assert sha(proof)==m['lossless_verification_sha256']and read(proof)['result']=='passed-exact-rgb-and-pcm'
        assert sha(recorded/'playthrough.delivery.json')==m['delivery_report_sha256']
        report.update(recording_vs_fixed=exact_csvs(FIXED,recorded),
            native_master_sha256=sha(recorded/'playthrough-lossless.mkv'),
            delivery_sha256=sha(recorded/'playthrough.mp4'),
            lossless_verification_sha256=sha(proof),result='fixed-replay-and-native-recording-verified')
    out.mkdir()
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'large normal movement steps:',len(steps))

if __name__=='__main__':main()
