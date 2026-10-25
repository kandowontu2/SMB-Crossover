from pathlib import Path
import collections, csv, json
R=Path(__file__).resolve().parents[2]
def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))
results={}
for name in ('mario','bill'):
    P=R/'build/verification'/('world-actors-ba-'+name)
    actors=rows(P/'actors.csv')
    owners=[z for z in actors if 0x1b<=int(z['id'])<0x23 and 0<int(z['flag'])<128]
    missing=[]
    for z in owners:
        xx=int(z['x'])-int(z['camera'])
        if 16<=xx<=239 and int(z['parts'])==0:
            missing.append({**{k:int(z[k])for k in ('frame','slot','id','x','y','camera','parts','spin')},'relativeX':xx})
    byowner=collections.defaultdict(list)
    for z in owners:byowner[(int(z['world']),int(z['level']),int(z['slot']),int(z['x']))].append(z)
    coverage=[]
    for key,zs in byowner.items():
        ons=[z for z in zs if 16<=int(z['x'])-int(z['camera'])<=239]
        coverage.append(dict(world=key[0],level=key[1],slot=key[2],x=key[3],y=int(zs[0]['y']),frames=len(zs),onscreen=len(ons),count_distribution=dict(collections.Counter(int(z['parts'])for z in ons)),first=int(zs[0]['frame']),last=int(zs[-1]['frame'])))
    bars=rows(P/'firebar-oam.csv');wrong=[];partchecks=0
    for z in bars:
        sprites=bytes.fromhex(z['oamHex'])
        actual=collections.Counter((sprites[i+3],sprites[i])for i in range(0,256,4)if sprites[i]<240 and sprites[i+1]in(0x41,0x43)and sprites[i+2]&3==2)
        expected=collections.Counter()
        for s in z['positions'].split(';'):
            if not s:continue
            x,y=map(int,s.split(':'))
            if 32<=y<240:expected[(x,(y-4)&255)]+=1
        partchecks+=sum(expected.values())
        absent=expected-actual
        if absent:wrong.append(dict(frame=int(z['frame']),slot=int(z['slot']),parts=int(z['parts']),expected=dict((str(k),v)for k,v in expected.items()),absent=dict((str(k),v)for k,v in absent.items())))
    bullets=[z for z in actors if int(z['id'])in(8,0x33)and int(z['flag'])]
    draws=rows(P/'actor-draws.csv')
    out=dict(firebar_owners=coverage,onscreen_zero_count=missing,part_checks=partchecks,part_position_misses=wrong,
             active_bullet_rows=len(bullets),bullet_draw_rows=len([z for z in draws if int(z['metasprite'])==0x72]),
             proof=json.loads((P/'summary.json').read_text()),goal_complete=False)
    (P/'actor-summary.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    results[name]=dict(firebar_owners=coverage,onscreen_zero_count=len(missing),zero_count_first=missing[:3],
        part_checks=partchecks,part_position_misses=len(wrong),miss_first=wrong[:2],active_bullet_rows=len(bullets))
print(json.dumps(results,indent=2))
