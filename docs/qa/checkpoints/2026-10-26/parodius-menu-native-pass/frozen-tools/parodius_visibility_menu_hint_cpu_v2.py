"""Full menu owner/queue/display/NMI CPU components; never native coverage."""
from pathlib import Path
import argparse,hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def packet(q):
 at=address(q.b,'VRAM_Buffer1');size=q.get('VRAM_Buffer1_Offset');data=bytes(q.m[at:at+size+1]);out=[];i=0
 while data[i]:
  n=(data[i+2]&63)or 256;end=i+3+(1 if data[i+2]&64 else n);out.append(data[i:end]);i=end
 assert i==size
 return data,out


def flush(q,ppu):
 b=q.b;at=address(b,'VRAM_Buffer1');q.put(NmiR0=at&255,NmiR1=at>>8);old=q.m.banks[2];shadow=q.get('CurrentBankC');q.m.page(2,116)
 c,trace=q.invoke('SamusFreezeUpdateScreen');assert q.m.banks[2]==116
 ptr=q.get('NmiR0')+256*q.get('NmiR1');ctrl=0;hi=None;dest=0;data=[]
 for t in trace:
  a,v=t['address'],t['value']
  if a==0x2000:ctrl=v
  elif a==0x2006:
   if hi is None:hi=v
   else:dest=((hi<<8)|v)&0x3fff;hi=None
  elif a==0x2007:
   x=dest
   if x>=0x3f00:
    x=0x3f00+(x&31)
    if x in [0x3f10,0x3f14,0x3f18,0x3f1c]:x-=16
   ppu[x]=v;data.append([x,v]);dest=(dest+(32 if ctrl&4 else 1))&0x3fff
 q.m.page(2,old);q.set('CurrentBankC',shadow)
 # Explicit CPU component staging of resident InitBuffer after native flush.
 q.put(VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0);q.set('VRAM_Buffer1',0)
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],cycles=c.processorCycles,pointer=ptr,PPUDATA=data)


def setup(b,mode,variant):
 q=Arena(b,18);q.put(VvVariant=variant,CrossoverBehaviorVersion=mode,OperMode=0,OperMode_Task=3,GameEngineSubroutine=0,CrossoverMenuState=2,CrossoverMenuIndex=17,CrossoverMenuPressed=0,CrossoverMenuButtons=0,PlayerStatus=0,PlayerSize=1,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,Player_PageLoc=0,DisableScreenFlag=1)
 q.invoke('QueueSelection');data,commands=packet(q);ppu={};flush(q,ppu)
 q.put(DisableScreenFlag=0)
 return q,ppu,data


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output','native-packet']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bs=[scoped_load(a.baseline),scoped_load(a.candidate)];rows=[];case=None
 try:
  # Exact public-helper controls cover other heroes, first page/disabled
  # construction and combined inputs that must retain the full old writer.
  for char,pressed,disabled,state in itertools.product(range(20),[1,32,33],[0,1],[1,2]):
   got=[]
   for b in bs:
    q=Arena(b,char);q.put(OperMode=0,CrossoverMenuState=state,CrossoverMenuPressed=pressed,DisableScreenFlag=disabled,VRAM_Buffer1_Offset=10)
    q.array('VRAM_Buffer1',[0x3f,0x10,1,15,0x3f,0x11,3,21,8,33,0])
    c,_=q.invoke('QueueVariantHint');got.append((q,c))
   hot=char==18 and pressed==32 and disabled==0 and state==2
   if not hot:
    assert packet(got[0][0])==packet(got[1][0])
    assert [got[0][1].a,got[0][1].x,got[0][1].y,got[0][1].p,got[0][1].sp]==[got[1][1].a,got[1][1].x,got[1][1].y,got[1][1].p,got[1][1].sp]
   else:assert got[0][0].get('VRAM_Buffer1_Offset')==33 and got[1][0].get('VRAM_Buffer1_Offset')==10
   rows.append(dict(kind='helper',char=char,pressed=pressed,disabled=disabled,state=state,retains_original=not hot,CPU_delta=got[1][1].processorCycles-got[0][1].processorCycles))
  for mode,variant,pressed in itertools.product([0,1],range(4),[32,33]):
   case=dict(kind='complete-menu',mode=mode,previous_variant=variant,pressed=pressed);got=[]
   for b in bs:
    q,ppu,initial=setup(b,mode,variant)
    q.put(SavedJoypad1Bits=pressed,SavedJoypad2Bits=0)
    c,trace=q.invoke('CrossoverMenuInput');data,commands=packet(q)
    foreground=dict(regs=[c.a,c.x,c.y,c.p,c.sp],cycles=c.processorCycles,ram=bytes(q.m[:0x8000]),banks=list(q.m.banks),commands=commands,data=data)
    nmi=flush(q,ppu);got.append(dict(q=q,initial=initial,foreground=foreground,nmi=nmi,ppu=ppu))
   x,y=got;f,g=x['foreground'],y['foreground'];hot=pressed==32
   assert x['initial']==y['initial'],'Initial native full hint owner must remain exact'
   assert f['regs']==g['regs']and f['banks']==g['banks'],('Full caller public ABI',case,f['regs'],g['regs'])
   allowed=set(range(address(bs[0],'VRAM_Buffer1'),address(bs[0],'VRAM_Buffer1')+84))|{address(bs[0],'VRAM_Buffer1_Offset')}
   apps=list(range(0x100))+list(range(0x200,0x800))+list(range(0x5c00,0x8000));diffs=[i for i in apps if f['ram'][i]!=g['ram'][i]]
   assert set(diffs)<=allowed,('Whole caller nonstack RAM/OAM difference',case,[(hex(i),f['ram'][i],g['ram'][i])for i in diffs if i not in allowed])
   assert x['ppu']==y['ppu'],('Full logical nametable/attrs/palette/cursor after actual native writes',case)
   assert x['nmi']['regs']==y['nmi']['regs']
   if hot:
    assert len(f['commands'])==6 and len(g['commands'])==5
    assert f['commands'][3][0:3]==bytes([0x23,0x46,20])and f['commands'][:3]+f['commands'][4:]==g['commands']
    assert len(f['data'])-len(g['data'])==23
   else:assert f['data']==g['data']and x['nmi']==y['nmi']
   rows.append(dict(case,hot=hot,full_public_AXYP_SP_exact=True,all_nonstack_nonqueue_RAM_and_OAM_exact=True,final_nametable_palette_cursor_exact=True,initial_full_packet_exact=True,baseline_packet_bytes=len(f['data'])-1,candidate_packet_bytes=len(g['data'])-1,foreground_CPU_delta=g['cycles']-f['cycles'],baseline_NMI_gateway_cycles=x['nmi']['cycles'],candidate_NMI_gateway_cycles=y['nmi']['cycles'],NMI_gateway_CPU_delta=y['nmi']['cycles']-x['nmi']['cycles']))
  # Replay exact genuinely recorded native packet under the actual gateway.
  native=json.loads(a.native_packet.read_text());raw=bytes(v for cmd in native['commands']for v in ([cmd['PPU_address']>>8,cmd['PPU_address']&255,cmd['control']]+cmd['payload']))+b'\0'
  assert len(raw)==63;short=raw[:29]+raw[52:];assert len(short)==40
  actual=[]
  for b,data in zip(bs,[raw,short]):
   q=Arena(b,18);q.put(OperMode=0,VvVariant=1,VRAM_Buffer1_Offset=len(data)-1);q.array('VRAM_Buffer1',data);ppu={i:0x24 for i in range(0x2346,0x235a)}
   # Real prior frames show this native hint, so stage its exact source bytes
   # as already published solely for this independently labeled CPU model.
   for i,v in enumerate(raw[32:52]):ppu[0x2346+i]=v
   actual.append((flush(q,ppu),ppu))
  assert actual[0][1]==actual[1][1]
  rows.append(dict(kind='genuine-recorded-packet',baseline_encoded=62,candidate_encoded=39,final_map_exact=True,CPU_delta=actual[1][0]['cycles']-actual[0][0]['cycles'],baseline_cycles=actual[0][0]['cycles'],candidate_cycles=actual[1][0]['cycles'],component_staged_prior_published_hint=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),case=case,completed_cases=len(rows)),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
 q=dict(passed=True,native_run=False,component_only=True,cases=len(rows),baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),limits='Synthetic CPU components with true assembled menu owner/initial queue/native parser; source-valid initial hint is published by actual initial QueueSelection before same-family toggles. Resident InitBuffer clear and PPU address/palette map are explicit CPU-model setup; no native deadline/interrupt/PPU pixels or lifecycle pass. Genuine prior native128 frames separately establish original displayed help. No source audio change or broader performance guarantee.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
