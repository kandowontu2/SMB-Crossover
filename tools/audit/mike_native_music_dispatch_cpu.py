"""Mike native actual dispatch, outer identities and compiled interrupt checks.



Authored CPU fixtures only. An actual nested NMI is retained as a domain

negative, never replaced by a synthetic ISR or described as a native pass.

"""

from pathlib import Path

import argparse,gzip,hashlib,itertools,json

from mike_native_music_cpu import Run,state,translated

from check_tmnt_render_oa import load,address,location

from check_tmnt_audio_fallback_oc import qualified,result

from final_item_matrix import ROSTER

from verify_native_relocation import NesMPU



sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()



def golds(path,song,count):

 rows=[]

 with gzip.open(path/f'song-{song:02d}.jsonl.gz','rt')as f:

  for i,line in enumerate(f):

   if i>count:break

   rows.append(json.loads(line))

 return rows



def configured(b,mode):

 r=Run(b)

 for n,v in dict(SelectedCharacter=16,OperMode=1,CrossoverBehaviorVersion=mode,CurrentBank=215,CurrentBankC=166,DisableScreenFlag=1,NmiDisable=255,IrqNewScroll=0x53,IrqPPUCTRL=1).items():r.set(n,v)

 r.m.page(2,38);r.m[:256]=[(i*17+41)&255 for i in range(256)]

 return r



def adapters(b,path,quick,out):

 q=json.loads((path/'coverage.json').read_text());components={}

 for lo,hi,at,target in q['pointer_components']:components[lo]=('<',target);components[hi]=('>',target)

 roles=[('area',i,s)for i,s in enumerate([1,2,4,5,14,11,22])]+[('event',i,s)for i,s in enumerate([13,15,9,17,15,9,5])];rows=[]

 for role,bit,song in roles:

  expected=golds(path,song,1700 if song==11 else 450 if song in[9,13,15]else 600 if quick else 4500)

  for mode in[0,1]:

   r=configured(b,mode);r.m[address(b,'StNativeRam'):address(b,'StNativeRam')+288]=[(31*i+17)&255 for i in range(288)]

   saved=bytes(r.m[:256]);r.set('AreaMusicQueue'if role=='area'else'EventMusicQueue',1<<bit);r.call('ExpandedAudioUpdate');assert bytes(r.m[:256])==saved

   assert state(r,False)==translated(b,expected[0],components),('Cold init did not clear/restore exact original state',role,bit,song,mode)

   assert r.m.events==[(0x4000+i,0)for i in reversed(range(16))]+[(0x4015,0)]

   assert r.get('XgAudioCharacter')==251 and r.get('RgAudioSong')==song

   cursor=1;loops=0;stores=len(r.m.events);minimum=r.depth;costs=[];calls=1;finite_end=False

   for frame in range(len(expected)-1):

    ended=r.get('StNativeZp')==0 and all(r.get('StNativeRam',i)==255 for i in range(16,22))

    prior=state(r,False);cost=r.call('ExpandedAudioUpdate',a=(frame*7)&255,x=(frame*3)&255,y=frame&255,p=[0x20,0x61,0xe1][frame%3]);costs.append(cost);calls+=1;minimum=min(minimum,r.depth)

    assert bytes(r.m[:256])==saved,('Foreground ZP leaked',role,bit,mode,frame)

    assert r.m.banks[1]==87 and r.m.banks[2]==97 and r.get('CurrentBank')==215 and r.get('CurrentBankC')==225

    if ended and role=='event'and bit!=6:

     assert r.get('XgAudioEvent')==2 and r.m.events==[(0x4015,0)]and state(r,False)==prior;finite_end=True;break

    if ended:want=expected[0];cursor=1;loops+=1;writes=[(0x4000+i,0)for i in reversed(range(16))]+[(0x4015,0)]

    else:want=expected[cursor];cursor+=1;writes=list(map(tuple,want['writes']))

    assert r.m.events==writes,('Adapter first wrong ordered source store',role,bit,song,mode,frame,r.m.events,writes)

    assert state(r,False)==translated(b,want,components),('Adapter original state diverged',role,bit,song,mode,frame)

    stores+=len(r.m.events)

   if song==11:assert loops==1

   if role=='event'and song in[9,13,15]:assert finite_end

   row=dict(role=role,bit=bit,song=song,CPU_behavior_mode=mode,source_schedule_calls=calls,source_stores=stores,whole_tune_restarts=loops,finite_event_stopped=finite_end,mean_outer_cycles=sum(costs)/len(costs),peak_outer_cycles=max(costs),minimum_SP=minimum);rows.append(row);print('ADAPTER',row,flush=True);(out/'adapter-progress.json').write_text(json.dumps(rows,indent=2)+'\n')

 # Pauses, source enable-mask restoration, persistent silence, queue precedence,

 # actual character reentry and all queued cold/paused title states.

 controls=[]

 for mode in[0,1]:

  r=configured(b,mode);r.set('AreaMusicQueue',1);r.call('ExpandedAudioUpdate');r.call('ExpandedAudioUpdate');r.call('ExpandedAudioUpdate');prior=state(r,False);mask=r.get('StNativeRam');r.set('GamePauseStatus',1)

  for _ in range(3):r.call('ExpandedAudioUpdate');assert state(r,False)==prior and r.m.events==[(0x4015,0)]

  r.set('GamePauseStatus',0);r.call('ExpandedAudioUpdate');assert r.m.events[0]==(0x4015,mask)and state(r,False)!=prior

  r.set('AreaMusicQueue',128);prior=state(r,False);r.call('ExpandedAudioUpdate');assert r.get('RgAudioSilenced')==1 and state(r,False)==prior

  for _ in range(3):r.call('ExpandedAudioUpdate');assert state(r,False)==prior

  r.set('AreaMusicQueue',4);r.set('EventMusicQueue',8);r.call('ExpandedAudioUpdate');assert r.get('RgAudioSong')==17 and r.get('XgAudioEvent')==1

  r.set('XgAudioCharacter',6);r.set('AreaMusicQueue',2);r.call('ExpandedAudioUpdate');assert r.get('RgAudioSong')==2 and state(r,False)==translated(b,golds(path,2,0)[0],components)

  controls.append(dict(mode=mode,pause_source_state_retained=True,authentic_channel_mask_restored=mask,silence_retained=True,event_over_area_priority=True,character_reentry_reset=True))

 cold=[]

 for mode,oper,paused,area,event in itertools.product([0,1],[0,1],[0,1],[0,4],[0,8]):

  r=configured(b,mode);r.set('OperMode',oper);r.set('GamePauseStatus',paused);r.set('AreaMusicQueue',area);r.set('EventMusicQueue',event);hist=address(b,'StNativeRam');r.m[hist:hist+288]=[(i*31+17)&255 for i in range(288)];before=bytes(r.m[hist:hist+288]);r.call('ExpandedAudioUpdate')

  if not oper or paused:assert bytes(r.m[hist:hist+288])==before and r.get('GuestNativeEnable')==0

  if oper and not paused:assert r.get('RgAudioSong')==(17 if event else 4 if area else 1)

  if not oper:r.set('AreaMusicQueue',area);r.set('EventMusicQueue',event)

  r.set('OperMode',1);r.set('GamePauseStatus',0);r.call('ExpandedAudioUpdate');assert r.get('RgAudioSong')==(17 if event else 4 if area else 1)

  cold.append(dict(mode=mode,initial_oper=oper,paused=paused,area=area,event=event))

 return dict(roles=rows,controls=controls,cold_title_pause_cases=cold)



def identities(old,new,quick,out):

 rows=[]

 for identity,slot,char,var,value,family in ROSTER:

  if char==16:continue

  count=0;costs=[]

  for mode,flags,request in itertools.product([0,1],[0x20,0x21,0x60,0xe1],[(1,0),(2,0),(0,4),(1,8)]):

   qs=[Run(b)for b in[old,new]]

   for r in qs:

    for n,v in dict(SelectedCharacter=char,OperMode=1,CrossoverBehaviorVersion=mode,PlayerStatus=1,GameEngineSubroutine=8,Player_Y_HighPos=1,Player_X_Position=96,Player_PageLoc=1,Player_Y_Position=160,PlayerFacingDir=1,ScreenLeft_PageLoc=1,DisableScreenFlag=1,AreaMusicQueue=request[0],EventMusicQueue=request[1]).items():r.set(n,v)

    if var:r.set(var,value)

   for tick in range(4 if quick else 8):

    for r in qs:r.set('GamePauseStatus',int(tick in[2,3]));r.set('AvAudioRequest',21 if tick==1 else 0)

    costs0=[r.call('AudioUpdate',a=0x55,x=3,y=7,p=flags)for r in qs]

    assert result(qs[0].c,qs[0].m)==result(qs[1].c,qs[1].m),('Identity full AudioUpdate divergence',identity,mode,flags,request,tick)

    costs.append(costs0[1]-costs0[0]);count+=1

  row=dict(identity=identity,character=char,variant_symbol=var,variant=value,cases=count,caller_P=[0x20,0x21,0x60,0xe1],cycle_delta=[min(costs),max(costs)]);rows.append(row);print('IDENTITY',row,flush=True);(out/'identity-progress.json').write_text(json.dumps(rows,indent=2)+'\n')

 return rows



def call_boundary(b,mode,kind,boundary,flags):

 r=configured(b,mode);r.set('AreaMusicQueue',1);r.set('Sprite0HitDetectFlag',1);r.m[0x5204]=128

 c=r.c;c.pc=address(b,'ExpandedAudioUpdate');c.a,c.x,c.y,c.p,c.sp=0x55,3,7,flags,253;r.m[510]=255;r.m[511]=126;r.m.events=[];r.m.writes=[];r.m.lowwrites=[]

 at=address(b,'StNativeFromFamily')+boundary;did=False;touch=set();irqstores=[];negative=None
 family=address(b,'KbAudioFamily');pattern=bytes([0x20,family&255,family>>8]);begin=address(b,'ExpandedAudioTick');start=location(b,'ExpandedAudioTick');blob=b['raw'][start:start+family-begin];sites=[begin+i for i in range(len(blob)-2)if blob[i:i+3]==pattern];assert len(sites)==3; r.family_calls=[]

 for i in range(200000):

  if c.pc==0x7f00:break

  if kind and not did and c.pc==at:

   before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(r.m.banks));begin=len(r.m.writes)

   if kind=='IRQ':c.irq();assert c.pc==address(b,'IrqScrollSplit')

   else:c.nmi();assert c.pc==address(b,'NonMaskableInterrupt')

   for _ in range(200000):

    c.step()

    if c.pc==before[5]and c.sp==before[4]:break

   else:raise AssertionError(('Actual ISR timeout',kind,boundary,hex(c.pc)))

   effects=r.m.writes[begin:];touch={x for x,v in effects if 256<=x<512};did=True

   if kind=='IRQ':

    after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(r.m.banks));assert before==after,(before,after);irqstores=[(x,v)for x,v in effects if not 256<=x<512];assert all(x in[0x2005,0x2006,0x5128,address(b,'IrqNewScroll')]for x,v in irqstores)

   else:

    negative=dict(before_CPU=before[:6],after_CPU=[c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc],before_banks=before[6],after_banks=list(r.m.banks),returned_PC_SP_restored=c.pc==before[5]and c.sp==before[4],A_window_lost=r.m.banks[1]!=before[6][1],actual_NMI_entry=address(b,'NonMaskableInterrupt'),nested_source_request=r.get('RgAudioSong'));assert negative['A_window_lost'];return r,touch,irqstores,negative

  if c.pc in sites:r.family_calls.append(c.pc)
  r.m.pc=c.pc;c.step()

 else:raise AssertionError(('Outer timeout',kind,boundary,hex(c.pc)))

 assert c.sp==255 and(kind is None or did)
 assert r.family_calls==[sites[0]],('Mike escaped a later family call',r.family_calls,sites)

 return r,touch,irqstores,negative



def interrupts(b):

 irq=[];nmi=[]

 for mode,flags,boundary in itertools.product([0,1],[0x20,0x61,0xe1],[0,1,2]):

  plain,_,_,_=call_boundary(b,mode,None,boundary,flags);actual,touch,stores,_=call_boundary(b,mode,'IRQ',boundary,flags)

  assert (plain.c.a,plain.c.x,plain.c.y,plain.c.p&0xcf,plain.c.sp,plain.m.banks)==(actual.c.a,actual.c.x,actual.c.y,actual.c.p&0xcf,actual.c.sp,actual.m.banks)

  allowed=touch|{0x2005,0x2006,0x5128};diff=[i for i in range(0x8000)if plain.m[i]!=actual.m[i]and i not in allowed];assert not diff,('IRQ changed non-owned RAM',diff)

  assert plain.m.events==actual.m.events and plain.m[510:512]==actual.m[510:512]

  irq.append(dict(mode=mode,P=flags,discard_boundary=boundary,actual_IRQ_stack_cells=sorted(touch),actual_IRQ_nonstack_stores=stores,actual_family_callsite=actual.family_calls))

 for mode,boundary in itertools.product([0,1],[0,1,2]):

  r,touch,stores,negative=call_boundary(b,mode,'NMI',boundary,0x20);nmi.append(dict(mode=mode,discard_boundary=boundary,**negative))

 return dict(actual_IRQ_cases=irq,actual_nested_NMI_domain_negatives=nmi,limit='AudioUpdate already runs inside the real NMI. Injecting a second NMI re-enters all audio and restores foreground A bank87 over active helper bank115. This is an explicitly retained non-reentrant-domain failure, not a native scheduling pass or an empty-ISR substitute.')



def main():

 p=argparse.ArgumentParser(description=__doc__)

 for n in ['rom','baseline','gold','output']:p.add_argument('--'+n,type=Path,required=True)

 p.add_argument('--quick',action='store_true');p.add_argument('--only',choices=['adapters','identities','interrupts']);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)

 report=dict(passed=False,accepted=False,baseline_sha256=sha(a.baseline),candidate_sha256=sha(a.rom),tool_sha256=sha(__file__),CPU_mode_values=[0,1],native_emulator_launched=False)

 if a.only in[None,'adapters']:report['actual_dispatch']=adapters(new,a.gold,a.quick,a.output)

 if a.only in[None,'identities']:report['full_outer_non_Mike_identities']=identities(old,new,a.quick,a.output)

 if a.only in[None,'interrupts']:report['compiled_interrupts']=interrupts(new)

 report['passed']=True;(a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['actual_dispatch','full_outer_non_Mike_identities','compiled_interrupts']},indent=2))

if __name__=='__main__':main()
