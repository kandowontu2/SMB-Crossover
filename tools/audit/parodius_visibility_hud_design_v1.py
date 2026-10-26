"""Source/CPU-only static-label admission design; no ROM build or native run."""
from pathlib import Path
import argparse,hashlib,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_nmi_vram_fast_cpu_v1 import Bus,run
from check_tmnt_render_oa import address
from parodius_visibility_trace_report import commands
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def apply(packet,ram):
 for cmd in commands(dict(bytes=packet))['commands']:
  for i in range(cmd['length']):ram[(cmd['address']+i*cmd['increment'])%16384]=cmd['data'][0 if cmd['repeat']else i]
def packet_without_labels(packet):
 output=[];decoded=commands(dict(bytes=packet));assert decoded['terminated']
 for cmd in decoded['commands']:
  if cmd['address']==0x2022 and cmd['length']==28 and not cmd['repeat']and cmd['increment']==1:continue
  c=cmd['length']|(64 if cmd['repeat']else 0)|(128 if cmd['increment']==32 else 0);output += [cmd['address']>>8,cmd['address']&255,c]+cmd['data']
 return output+[0]
def gateway(bundle,packet,variant,capture):
 m=Bus(bundle);m.page(2,88);m.palette=[(i*73+19)&63 for i in range(32)];base=address(bundle,'VRAM_Buffer1')
 values=dict(SelectedCharacter=18,CrossoverBehaviorVersion=1,OperMode=1,VvVariant=variant,PnBombCapturePending=capture,PnBombPaletteReady=0,SmFreezePalettePending=0,CurrentBankC=88|128,Mirror_PPUCTRL=0xa0,NmiR0=base&255,NmiR1=base>>8)
 for n,v in values.items():m.put(address(bundle,n),v)
 for i,v in enumerate(packet):m.put(base+i,v)
 m.put(0x2002,0x80);m.put(0x1fe,0xff);m.put(0x1ff,0x01)
 result=run(bundle,m,address(bundle,'SamusFreezeUpdateScreen'),0x0200,0x5a,3,0xa5,0x71);return dict(cycles=result['cycles'],final_AXYP_SP=result['state'],PPUDATA_writes=sum(at==0x2007 for at,v in result['writes']),palette_reads=len(result['reads']),final_pointer=m[address(bundle,'NmiR0')]+256*m[address(bundle,'NmiR1')])
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rom=a.root/'nmi-fast-candidate-v1/candidate.nes';b=scoped_load(rom);assert sha(rom)=='cf0f53f012a7830c38d4a2212ceed8bc875040b5698345a83d0b7c98213eeed5';arena=Arena(b,18);label_sets={};attr_sets={};cases=[]
 for variant in [1,2,3]:
  labels=set();attrs=set()
  for meter in range(256):
   arena.put(VvVariant=variant,VvMeter=meter,VvHudDirty=1,InvHudActive=1,VRAM_Buffer1_Offset=0,DisableScreenFlag=0);arena.array('VRAM_Buffer1',[0]*84);cpu,_=arena.invoke('PnHud');data=[arena.get('VRAM_Buffer1',i)for i in range(arena.get('VRAM_Buffer1_Offset')+1)];decoded=commands(dict(bytes=data));assert decoded['terminated']and len(decoded['commands'])==2;label,attr=decoded['commands'];assert(label['address'],label['length'],attr['address'],attr['length'])==(0x2022,28,0x23c0,8);labels.add(tuple(label['data']));attrs.add(tuple(attr['data']))
   prior=bytearray((i*71+29)&255 for i in range(16384));prior[0x2022:0x203e]=bytes(label['data']);old=prior.copy();new=prior.copy();apply(data,old);filtered=packet_without_labels(data);apply(filtered,new);assert old==new
   invalid=bytearray([0x24]*16384);invalid_old=invalid.copy();invalid_new=invalid.copy();apply(data,invalid_old);apply(filtered,invalid_new);assert invalid_old!=invalid_new
   cases.append(dict(variant=variant,meter=meter,foreground_PnHud_cycles=cpu.processorCycles,full_packet_bytes=len(data)-1,redundant_label_bytes_removed=31,PPUDATA_writes_removed=28,final_PPU_memory_exact_when_labels_valid=True,invalid_label_cache_rejected=True))
  assert len(labels)==1;label_sets[variant]=list(next(iter(labels)));attr_sets[variant]=len(attrs)
 # Admission/state model only. It is deliberately not claimed to be assembled.
 transitions=[]
 for variant in [1,2,3]:
  expected=1+2*variant
  for cache in [0,1,3,5,7]:
   for dirty in [0,1]:
    for disabled in [0,1]:
     for offset in range(84):
      ready=cache==expected;kind='none';state=cache;next_dirty=dirty
      if not disabled:
       if not ready:state=1;next_dirty=1
       if next_dirty and offset<(73 if ready else 40):kind='attributes'if ready else'full';state=expected;next_dirty=0
      assert kind!='attributes'or ready
      if kind=='none'and(dirty or not disabled and not ready):assert next_dirty==1
      if kind=='full':assert state==expected and offset+42<84
      if kind=='attributes':assert state==expected and offset+11<84
      transitions.append(dict(variant=variant,prior_cache=cache,dirty=dirty,disabled=disabled,offset=offset,publication=kind,next_cache=state,next_dirty=next_dirty))
 genuine=read(a.root/'broad-budget-v1/genuine-failing-packets.json');costs=[]
 for fail in genuine:
  raw=fail['source_packet']['bytes'];consumed=fail['decoded']['consumed_bytes'];packet=raw[:consumed]+[0];filtered=packet_without_labels(packet);before=gateway(b,packet,fail['variant'],int(fail['profile']=='pentarou-easy'));after=gateway(b,filtered,fail['variant'],int(fail['profile']=='pentarou-easy'));assert before['final_AXYP_SP']==after['final_AXYP_SP'];costs.append(dict(profile=fail['profile'],original=before,attribute_only_if_labels_valid=after,cycles_saved=before['cycles']-after['cycles'],actual_packet_bytes=consumed,filtered_packet_bytes=len(filtered)-1,source_label_cache_validity='NOT established for first cold Pentarou publish; full labels remain mandatory there. Settled Hard cache validity requires actual publication/reset proof before a candidate.',new_native_claim=False))
 source=a.root/'frozen/src';uses=[]
 for f in sorted(source.rglob('*.s')):
  data=f.read_text(encoding='utf-8').splitlines()
  for i,line in enumerate(data):
   if 'InvHudActive'in line:uses.append(dict(file=f.name,line=i+1,text=line,context=data[max(0,i-1):i+4]))
 (a.output/'HUD-component-cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n',encoding='utf-8');(a.output/'admission-state-model.json').write_text(json.dumps(transitions,separators=(',',':'))+'\n',encoding='utf-8');(a.output/'InvHudActive-source-uses.json').write_text(json.dumps(uses,indent=2)+'\n',encoding='utf-8');(a.output/'genuine-packet-costs.json').write_text(json.dumps(costs,indent=2)+'\n',encoding='utf-8')
 q=dict(source_model_passed=True,native_run=False,ROM_build=False,candidate_implemented=False,goal_complete=False,ROM_sha256=sha(rom),script_sha256=sha(Path(__file__)),compiled_existing_PnHud_cases=len(cases),modeled_admission_transitions=len(transitions),static_labels_by_variant=label_sets,distinct_attribute_rows_by_variant=attr_sets,buffer_addresses={n:address(b,n)for n in ['VRAM_Buffer1','VRAM_Buffer2','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset']},cache_encoding_proposal={'0':'inactive/invalid','1':'font owned; labels not yet guaranteed','3':'variant1 labels queued/valid','5':'variant2 labels queued/valid','7':'variant3 labels queued/valid'},constraints=['All existing active readers are boolean/nonzero; tagged values require compiled-reader regression before implementation.','Cache tag set only after successful full-label+attribute queue. First deferred queue keeps pending/dirty.','PnHud renews font each active call and retains dirty until append fits. Attribute-only queue11bytes plus terminator allows offset0..72; original full42byte limit remains0..39.','Actual VvReset/DeathStart/InventoryInit clear ownership; menu/area path and delayed flush/cancellation must be tested before native acceptance.','Moving cold palette capture earlier is unproved: current ColorRotation every8thFrameCounter queues phase-dependent3F0C..0F before capture.','No production/privateROM source was changed; full-parser/source candidate belongs to ROOT review.'],metadata_correction='Frozen root-gateway CPU field mode assigns OperMode(menu/game), not CrossoverBehaviorVersion difficulty. Actual Easy/Hard evidence is only the six native controls.',source_bindings={n:sha(source/n)for n in ['parodius_render.s','parodius_adapter.s','vic_adapter.s','vic_dispatch.s','inventory.s','game.s','screen_render.s','samus.s','guest_powerups.s','roster.s','mmc5_expanded.s','remaining_audio.s']},bindings={p.name:sha(p)for p in sorted(a.output.iterdir())if p.is_file()})
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(source_model_passed=True,native_run=False,proof_sha256=sha(a.output/'proof.json'),costs=costs)))
if __name__=='__main__':main()
