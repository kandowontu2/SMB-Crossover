"""Existing motion differentials plus actual original3 align/rapid-pound loop."""
from pathlib import Path
P=Path(__file__).with_name('bowser_source_core_controls_v3.py')
ns={'__file__':str(P),'__name__':'_construct_source_fixture'}
exec(compile(P.read_text(encoding='utf-8').rsplit("exec(compile(s,str(P),'exec'),",1)[0],str(P),'exec'),ns)
s=ns['s'].replace('bowser-source-core-v2','bowser-source-core-v5').replace('controls-v3.json','controls-v5.json')
s=s.replace('abstract_active_state_bytes=31','abstract_active_state_bytes=34')
extra='''  pound=[]
  for startX in [107,248,255]:
   call(new,labels['Bw3Fresh']);new[0x6008]=startX;new[0x6009]=120;new[0x6014]=0;trace=[]
   for tick in range(90):
    keys=0x84 if tick==1 else 0
    c,low=call(new,labels['Bw3Step'],a=keys)
    trace.append(dict(tick=tick,x=new[0x6008]+256*new[0x600c],y=new[0x6009]+256*new[0x600d],align=new[0x6018],active=new[0x601f],pose=new[0x6016],impact=new[0x601a]))
   assert sum(r['impact']for r in trace)==1,('groundpound actual landing',startX,trace)
   target=(startX+8)&0xfff0
   assert trace[11]['x']==target and trace[11]['active']==1
   assert all(r['pose']==6 for r in trace if r['active'])
   assert trace[-1]['active']==0 and trace[-1]['y']==176
   pound.append(dict(startX=startX,targetX=target,trace=trace))
  q['checks']['source3_align_rapid_pound']=dict(cases=3,rows=pound,ten_tick_alignment_world_page_edges=True,impact_persists_past_timer_until_landing=True)
'''
s=s.replace("  q['measured']=",extra+"  q['measured']=")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
