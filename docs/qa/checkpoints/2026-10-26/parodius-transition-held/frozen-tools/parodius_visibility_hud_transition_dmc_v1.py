"""Bounded character18 DMC reachability audit and explicitly synthetic stall envelope."""
from pathlib import Path
import argparse,collections,hashlib,json,urllib.request
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','menu-run','buffer-cpu','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(a.candidate/'candidate.nes')==SHA;b=scoped_load(a.candidate/'candidate.nes')
 source=a.candidate/'source/src';family=(source/'remaining_audio.s').read_text();family=family[family.index('.proc RemainingAudioSupported'):family.index('.endproc')]
 assert 'CHARACTER_SIMON+1'in family and 'CHARACTER_RYU'in family and 'CHARACTER_SOPHIA'in family and '#18'not in family
 controls=[]
 for variant in [0,1,2,3]:
  q=Arena(b,18);q.put(VvVariant=variant);c,tr=q.invoke('RemainingAudioSupported');assert not c.p&1
  q.put(GuestAudioCharacter=5,BassDmcActive=3,GuestNativeEnable=15,GuestCombinedEnable=15);c,tr=q.invoke('GuestAudioBegin');assert q.get('BassDmcActive')==0
  hardware=[x for x in tr if 0x4000<=x['address']<=0x4017];assert not any(x['address']==0x4015 and x['value']&16 for x in hardware)
  controls.append(dict(variant=variant,RemainingAudioSupported_carry=False,actual_character_change_resets_shared_DMC=True,DMC_enable_writes=0,actual_hardware_writes=hardware,limits='Isolated source owner inputs, not a new native mode/control'))
 observed=collections.Counter();enables=[];first=None;last=None
 for line in(a.menu_run/'oam-bus.jsonl').open():
  q=json.loads(line)
  if q['kind']=='APU-write':
   observed[q['address']]+=1;first=first or q['ppu'];last=q['ppu']
   if q['address']==0x4015 and q['value']&16:enables.append(q)
 assert not enables and not any(observed[x]for x in range(0x4010,0x4014))
 primary={};refs=a.output/'primary-model-sources';refs.mkdir()
 for name in ['APU/DeltaModulationChannel.h','APU/DeltaModulationChannel.cpp','NesCpu.cpp']:
  url='https://raw.githubusercontent.com/SourMesen/Mesen2/master/Core/NES/'+name;f=refs/Path(name).name
  f.write_bytes(urllib.request.urlopen(url,timeout=30).read());primary[name]=dict(url=url,sha256=sha(f),scope='Contemporary upstream primary implementation for a disclosed model, not asserted byte/source identity with pinned localMesenCore.dll')
 assert '72,  54'in(refs/'DeltaModulationChannel.h').read_text() and '_bitsRemaining = 8'in(refs/'DeltaModulationChannel.cpp').read_text()
 # Conservative steady-sample model: fastest NTSC byte period54*8=432,
 # at most4 lost cycles per fetch, plus TWO extra startup/in-flight fetches.
 # No repeated register restarts or one-byte duplication glitch chain modeled.
 def envelope(base):
  total=base
  for _ in range(100):
   extra=4*(2+(total+431)//432);new=base+extra
   if new==total:return dict(base_cycles=base,synthetic_max_extra_cycles=extra,synthetic_total_cycles=total,assumptions='Steady uninterrupted DMC sample, fastestNTSC432CPUcycles/byte,4CPUcycles/fetch +two extra fetches. No repeated sample re-enables/glitch chain, actual DMA arbitration, input deletion or IRQ raster emulation.')
   total=new
  raise AssertionError('Unbounded envelope')
 costs=json.loads((a.buffer_cpu/'cases.json').read_text());timing=[]
 for q in costs:
  for phase in ['hold_prefix','catchup_prefix']:
   # End-before-audio CPU work is an overestimate for pre-DMA work.514 is
   # the ordinary hardware OAM allowance; this is a model, not a replay.
   v=envelope(q[phase]['cycles_to_Audio_entry_without_DMA_hardware_stall']+514);timing.append(dict(variant=q['variant'],column=q['column'],phase=phase,**v))
 maxextra=max(q['synthetic_max_extra_cycles']for q in timing)
 proof=dict(passed=True,native_run=False,ROM_sha256=SHA,character18_no_eligible_owned_DMC_path=True,source_owner_controls=controls,existing_exact_menu_APU_window=dict(first=first,last=last,DMC_register_writes=0,DMC_enable_writes=0,APU4015_writes=observed[0x4015],scope='Original immutable bus only recordsAPU afterwall440; not a wholeboot absence proof'),synthetic_timing_envelopes=timing,synthetic_max_extra_cycles=maxextra,existing_native_menu_margin_comparison=[dict(actual_frame=n,observed_margin_CPU_cycles=m,model_only_margin_after_extra=m-maxextra)for n,m in [(278,208),(376,206)]],primary_sources=primary,source_sha256={str(source/n):sha(source/n)for n in ['remaining_audio.s','guest_audio.s','expanded_audio.s','gradius_audio.s','parodius_adapter.s']},menu_receipt_sha256=sha(a.menu_run/'lifecycle-proof.json'),buffer_CPU_sha256=sha(a.buffer_cpu/'proof.json'),tool_sha256=sha(Path(__file__)),limits='Source-owned DMC eligibility is closed only for currentcharacter18 sound paths; no injected/native DMC case is proposed. Existing native observations and synthetic timing bounds are distinct. Model excludes repeated sample restarts/glitches/input deletion/raster arbitration and does not establish globalNMI60Hz or hardware worstcase for other characters. Genuine death/area/Buffer2 lifecycle coverage remains unrun.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),source_controls=len(controls),synthetic_max_extra_cycles=maxextra,actual_menu_DMC_enables=0),indent=2))


if __name__=='__main__':main()
