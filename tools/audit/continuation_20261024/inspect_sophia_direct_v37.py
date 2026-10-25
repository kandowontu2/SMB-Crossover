from pathlib import Path
import csv,json
D=Path(__file__).resolve().parent
s=(D/'replay_mmc3_sophia_v37.py').read_text()
end=s.rindex('exec(compile(')
ns={'__file__':str(D/'replay_mmc3_sophia_v37.py')}
exec(compile(s[:end],'<reconstruct-read-only>','exec'),ns)
text=ns['s'];out=D/'mmc3-static-call-v37/direct-sophia-v1'
(out/'prepared-replay.py').write_text(text)
print('\n'.join(f'{i+1}: {v}'for i,v in enumerate(text.splitlines())if 18<=i+1<=30))
route=out/'direct-sophia-easy'
trace=list(csv.DictReader((route/'trace.csv').open()))
active=[z for z in trace if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0']
pairs=[(a,b)for a,b in zip(active,active[1:])if int(b['frame'])==int(a['frame'])+1]
spikes=[(a['frame'],b['frame'],a['x'],b['x'],a['camera'],b['camera'])for a,b in pairs if abs(int(b['x'])-int(a['x']))>8 or not 0<=int(b['camera'])-int(a['camera'])<=4]
visible=[z for z in csv.DictReader((route/'scroll-writes.csv').open())if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0'and z['screenDisabled']=='0'and z['renderingEnabled']=='1']
print(json.dumps(dict(raw_motion_spikes=spikes[:30],visible_writers=sorted(set((z['scanline'],z['writerBank'])for z in visible)),visible_count=len(visible))))
