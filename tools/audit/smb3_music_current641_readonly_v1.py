"""Existing SMB3 music route/storage/core cost review; no source/ROM/native changes."""
from pathlib import Path
from collections import Counter
import argparse, gzip, hashlib, json, statistics
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from smb3_native_core_cpu_v3 import Bus,source_state
from verify_native_relocation import NesMPU
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):assert not p.exists();p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def regions(b,bank):
 return[dict(name=g['name'].strip('"'),PC=int(g['start'],0),physical_start=int(g['ooffs'],0)-16-bank*8192,size=int(g['size'],0))for g in b['segs'].values()if all(n in g for n in ['ooffs','start','size'])and int(g['size'],0)>0 and 16+bank*8192<=int(g['ooffs'],0)<16+(bank+1)*8192]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 paths=[D/'root-luigi641-adoption-build-v1/candidate.nes',D/'root-current-roster-composition-v1/candidate.nes'];hashes=['641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c','3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'];bs=[]
 for path,h in zip(paths,hashes):assert sha(path)==h;bs.append(scoped_load(path))
 routes=[]
 for path,b in zip(paths,bs):
  for mode in [0,1]:
   for variant in [0,1]:
    q=Arena(b,17);q.put(M3Variant=variant,CrossoverBehaviorVersion=mode,AreaMusicQueue=1,EventMusicQueue=0,XgAudioCharacter=255,GuestAudioCharacter=255,GamePauseStatus=0)
    calls=[]
    for phase in ['cold-area','steady']:
     c,trace=q.invoke('AudioUpdate');assert q.get('XgAudioCharacter')==6 and q.get('XgAudioBase')==0 and q.get('XgAudioSelection')==0
     calls.append(dict(phase=phase,whole_AudioUpdate_cycles=c.processorCycles,selected_music_family=q.get('XgAudioCharacter'),playlist_area_index=q.get('XgAudioSelection'),APU_writes=[[r['address'],r['value']]for r in trace if 0x4000<=r['address']<=0x4017]))
    routes.append(dict(ROM_sha256=sha(path),character=17,M3Variant=variant,mode=mode,family=6,source_music='Kid Icarus/Pit',calls=calls))
 # Every original compiled route span is identical on both current hashes.
 spans={}
 for name in ['AudioUpdate','ExpandedAudioUpdate','VgAudioDispatch','LmNativeMusicGate','ExpandedAudioTick','KbAudioFamily','GuestDmcStatus']:
  records=[]
  for b in bs:
   count=int(b['syms'][name].get('size','0'),0)or(18 if name=='LmNativeMusicGate'else 24);off=location(b,name);records.append(dict(PC=address(b,name),bank=(off-16)//8192,bytes=count,sha256=hashlib.sha256(b['raw'][off:off+count]).hexdigest()))
  assert records[0]==records[1];spans[name]=records[0]
 current=bs[1];capacity=[]
 for bank in [78,86,90,93,95,96,98,118,119]:
  off=16+bank*8192+4096;overlap=[g for g in regions(current,bank)if g['physical_start']+g['size']>4096]
  assert not overlap and current['raw'][off:off+4096]==bytes([255])*4096
  capacity.append(dict(bank=bank,proposed_page_offset=4096,size=4096,currently_unallocated_FF=True,preserved_prefix=regions(current,bank)))
 off=16+86*8192+0x800;assert current['raw'][off:off+0x200]==bytes([255])*0x200
 clone_diffs=[];oldcore=D/'smb3-native-core-v5/candidate.nes';assert sha(oldcore)=='a4be8e02de0f8c0c43e5a7c94e4719e8b62c2ae80c1b1769978b06e73f2cac98';core=scoped_load(oldcore)
 fixed=current['raw'][16+127*8192:16+128*8192]
 for bank in [70,97]:
  previous=core['raw'][16+bank*8192:16+(bank+1)*8192];outside=[i for i,(x,y)in enumerate(zip(previous,fixed))if x!=y and not 0x1140<=i<0x1fc1]
  clone_diffs.append(dict(old_clone_bank=bank,outside_sample_region_differing_bytes=len(outside),first_differences=[dict(PC=0xe000+i,old=previous[i],current=fixed[i])for i in outside[:32]],old_E005=list(previous[5:13]),current_E005=list(fixed[5:13]),safe_to_copy_old_clone=False))
 assert all(r['outside_sample_region_differing_bytes']>0 for r in clone_diffs)
 # ONE isolated old-core normal-role prefix, no new implementation. Its original
 # oracle remains intact; profiling counters never touch emulated RAM/CPU state.
 nsf=ROOT/'reference/new-roster-audio/mario3/crossover-named.nsf';assert sha(nsf)=='4f22166e5baf4db867564b57c3d152dacb85b6365f7bf94cf0883d612e7f915c'
 m=Bus(core,nsf.read_bytes()[128:]);m.armed=False;m.page(1,86);m.page(2,38);m[address(core,'CurrentBank')]=214;m[address(core,'CurrentBankC')]=166;m.writer_start=address(core,'B3Write4012');m.writer_end=address(core,'B3Write4015');m.armed=True;c=NesMPU(memory=m);profile=[]
 entries={address(core,n):n for n in ['B3ReadAbsX','B3ReadAbsY','B3Read6B','B3Read71']};bank_fields={address(core,'CurrentBank'),address(core,'B3SavedABank'),0x5115}
 tracepath=D/'smb3-original-music-closure-v3/normal-09/calls.jsonl.gz'
 with gzip.open(tracepath,'rt')as f:
  for line in f:
   want=json.loads(line);tick=want['tick']
   if tick>1024:break
   m.armed=False;m[510],m[511]=255,126;m.armed=True;c.pc=address(core,'B3StandaloneCold'if tick==0 else'B3SourceA000');c.a=8 if tick==0 else 0;c.x=c.y=0;c.p=0x24;c.sp=253;m.logical=[];m.physical=[];m.sourcewrites=[];m.virtualwrites=[];m.writes=[];start=c.processorCycles;active=None;reads=[]
   for _ in range(200000):
    if c.pc==0x7f00:break
    if c.pc in entries:
     assert active is None;active=dict(kind=entries[c.pc],SP=c.sp,entry=c.processorCycles,bank_protocol_cycles=0,mapping=[])
    pc=c.pc;opcode=m[pc];target=(m[pc+1]|m[pc+2]<<8)if opcode in [0xad,0x8d]else None;before=len(m.writes);clock=c.processorCycles;m.pc=pc;c.step();cost=c.processorCycles-clock
    if active:
     if target in bank_fields:active['bank_protocol_cycles']+=cost
     active['mapping']+=[v&127 for at,v in m.writes[before:]if at==0x5115]
     if opcode==0x60 and c.sp==(active['SP']+2)&255:
      active['cycles']=c.processorCycles-active['entry'];reads.append(active);active=None
   else:raise AssertionError(('Core timeout',tick))
   assert active is None and[c.a,c.x,c.y,c.p&207,c.sp]==[v if i!=3 else v&207 for i,v in enumerate(want['post_AXY_P_SP'])]
   assert list(map(list,m.logical))==want['APU']and list(map(list,m.sourcewrites))==want['ordered_nonstack_RAM_writes']and list(map(list,m.virtualwrites))==want['mapper']
   assert hashlib.sha256(source_state(m,core)).hexdigest()==want['full_nonstack_source_RAM_sha256']
   targets=[]
   for read in reads:
    assert read['mapping']==[]or len(read['mapping'])==2 and read['mapping'][-1]==86
    if read['mapping']:targets.append(read['mapping'][0])
   lease_stores=0;leased=86
   for bank in targets:
    if bank!=leased:lease_stores+=1;leased=bank
   if leased!=86:lease_stores+=1
   profile.append(dict(tick=tick,core_cycles=c.processorCycles-start,original_cycles=want['cycles'],translated_read_calls=len(reads),ROM_read_calls=len(targets),all_read_helper_cycles=sum(r['cycles']+6 for r in reads),bank_protocol_cycles=sum(r['bank_protocol_cycles']for r in reads),actual5115_stores=2*len(targets),ideal_source_order_Alease_5115_stores=lease_stores,ideal_mapper_store_cycles_saved=4*(2*len(targets)-lease_stores),per_read_save_restore_instructions_removable_before_lease_control_cost=16*len(targets),read_types=dict(Counter(r['kind']for r in reads))))
 plays=profile[1:];agg={n:dict(mean=sum(r[n]for r in plays)/len(plays),max=max(r[n]for r in plays))for n in ['core_cycles','original_cycles','translated_read_calls','ROM_read_calls','all_read_helper_cycles','bank_protocol_cycles','actual5115_stores','ideal_source_order_Alease_5115_stores','ideal_mapper_store_cycles_saved','per_read_save_restore_instructions_removable_before_lease_control_cost']}
 put(a.output/'actual-current-routes.json',routes);put(a.output/'current-layout-and-clones.json',dict(route_spans=spans,free_payload_tails=capacity,cold86_A800_512B_currently_unallocated_FF=True,required_existing_data_moves=['Z2_GFX70→95','MIKE_GFX97→95','BILL_ORBIT_2 38→85'],old_clone_rebase_rejection=clone_diffs));put(a.output/'old-core-normal-prefix-profile.json',profile)
 put(a.output/'proof.json',dict(passed=True,read_only=True,native_run=False,source_or_ROM_or_settings_changed=False,installed641_ROM_sha256=hashes[0],frozen3b_ROM_sha256=hashes[1],actual_full_AudioUpdate_route_pairs=len(routes),all_SMB3_variants_modes_use_Pit_family6=True,prior_standalone_core_ROM_sha256=sha(oldcore),new_profile_scope='Existing isolated a4be core coldnormal9 +first1024plays only; every original source RAM/APU/mapper/physicalflag/store contract rechecked. No new implementation or host/PPU/DMC/IRQ lease qualification.',profile_calls=len(profile),profile_aggregates=agg,old_fixed_E_clones_fail_current_resident_code_identity=True,source_profile_method='Actual per-instruction elapsed cycles inside existing read helpers; includes nestedcalls and outerJSR6. Bank protocol is actual LDA/STA CurrentBank/B3SavedABank/5115 instructions. Ideal lease count is a read-only source-order lower bound, NOT an implemented saving; caching/ABI/IRQ/restore/lifecycle cost still required.',tool_sha256=sha(__file__)))
 print(json.dumps(get(a.output/'proof.json')if False else json.loads((a.output/'proof.json').read_text()),indent=2))
if __name__=='__main__':main()
