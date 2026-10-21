"""Review literal retained Scrooge G controller evidence; no emulator execution."""
from pathlib import Path
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'build/roster-through-2-2'
G=BASE/'root49n-scrooge-platform-g-12-v0-mmc3'
F=BASE/'root49n-scrooge-platform-f-12-v0-mmc3'
D=BASE/'root49n-scrooge-live-d-12-v0-mmc3'
PREP=ROOT/'build/verification/root49n-scrooge-platform-route-g'
OUT=ROOT/'build/verification/root49n-scrooge-g-actual-review-a.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=lambda p:list(csv.DictReader(p.open(newline='')))


def main():
    assert not OUT.exists()
    frozen=PREP/'freeze.json'
    assert sha(frozen)=='6832f393705d84ce4021b6c62d3737ec9717caa51462dbad85b85f599a90806b'
    for info in json.loads(frozen.read_text())['files']:
        assert sha(Path(info['path']))==info['sha256']
    assert sha(G/'policy.lua')==sha(PREP/'policy.lua')
    target_pins={'nes':'dd9f1414586e91ea3228c314eefb3cdff01b05caade8b71c17e228f79922d90d',
                 'dbg':'fe88308b504392d8d7071bf698c72ae6cdd0bec4c21daefb2785933a8b1b5aad',
                 'lbl':'6d4da1399454b3c6305b450162ebc07375059306deaf912ced56e66e3f60edad'}
    for ext,h in target_pins.items():assert sha(G/('smb-crossover-mmc3.'+ext))==h
    prefixes={}
    for name in ('inputs.csv','trace.csv','audio-events.csv','chr.csv','events.csv',
                 'oam.csv','render.csv','scroll-writes.csv','stomp-events.csv'):
        a=(F/name).read_bytes();b=(G/name).read_bytes()
        prefixes[name]={'F_sha256':hashlib.sha256(a).hexdigest(),'G_sha256':hashlib.sha256(b).hexdigest(),
                        'F_bytes':len(a),'G_bytes':len(b),'entire_F_is_literal_G_prefix':b.startswith(a)}
    assert all(x['entire_F_is_literal_G_prefix'] for x in prefixes.values())
    route=rows(G/'scrooge-g-platform-route.csv')
    phases=[]
    for r in route:
        if not phases or phases[-1]['phase']!=r['phase']:phases.append(r)
    assert [r['phase'] for r in phases]==['first-air','ride-first','second-air','ride-second','bank-air','done']
    assert (int(route[-1]['frame']),int(route[-1]['x']),int(route[-1]['y']),route[-1]['feet'])==(9080,1582,144,'23:23')
    support=[]
    for phase,slot,y in [('ride-first',2,128),('ride-second',3,144)]:
        r=next(r for r in route if r['phase']==phase)
        actor=next(a.split(':') for a in r['actors'].split(';') if int(a.split(':')[0])==slot)
        ax=int(actor[4]);px=int(r['x'])
        assert [int(actor[k]) for k in (1,2,3,5,6,7)]==[40,1,0,y,1,slot]
        assert int(r['grounded'])==1 and int(r['yHigh'])==1 and int(r['y'])+32==y
        assert ax<=px and px+15<=ax+48
        support.append({'phase':phase,'frame':int(r['frame']),'x':px,'y':int(r['y']),
                        'slot':slot,'actor':actor,'actual_support':True})
    old=rows(D/'inputs.csv');new=rows(G/'inputs.csv')
    first_diff=next(({'row':i+2,'D':a,'G':b} for i,(a,b) in enumerate(zip(old,new)) if a!=b),None)
    trace=rows(G/'trace.csv');result=json.loads((G/'result.json').read_text())
    assert result['stage_entries']['0-3']==10450 and result['frames']==11147
    assert result['failure']=='death' and not result['cleared']
    assert (int(trace[-1]['x']),int(trace[-1]['y']),int(trace[-1]['engine']))==(1032,112,11)
    report={'status':'PASS_ACTUAL_CONTROLLER_PLATFORM_CROSSING_THEN_UNCLASSIFIED_CASTLE_DEATH',
            'target':'Retained private N, not current O2 independent route proof',
            'script_sha256':sha(Path(__file__)),'prep_freeze_sha256':sha(frozen),
            'manifest_sha256':sha(G/'manifest.json'),'result_sha256':sha(G/'result.json'),
            'target_pins':target_pins,'nine_F_to_G_prefixes':prefixes,'first_D_G_input_difference':first_diff,
            'phase_transitions':phases,'supported_landings':support,'result':result,
            'last_three_trace_rows':trace[-3:],
            'limitations':['Adaptive ordinary power-on controller route, not independent fixed replay',
                           'G observer covers 1-3 platforms only; castle contact owner is unsampled',
                           'F began before its preflight passed; retained post-start admission is not a prospective gate',
                           'No ROM collision defect or full-goal completion inferred from later death']}
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(OUT),'sha256':sha(OUT),
                      'support_frames':[r['frame'] for r in support],'castle_entry':10450,'death_frame':11147},indent=2))


if __name__=='__main__':main()
