"""Typed private PPU staging/decode/finalizer proof, bootstrap rows as input."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_host_services_1102_v18 as C
P,O,W,N=C.P,C.O,C.W,C.N
POOL=[341,343,345,347,349,351,353,355,357,359,361,365,369,373,377,381,383,385,387,389,391,393,544,545,605,607,609,611,613,615,617,619,621,623,625,627,690,691,692,693,695,795,291]


def main():
 b=W.scoped_load(C.E.C.BASE);raw=bytearray(b['raw']);payload=(O/'cold-pool-v19.bin').read_bytes()
 for i,page in enumerate(POOL):
  part=payload[i*1024:(i+1)*1024];start=1048592+1024*page;raw[start:start+len(part)]=part
 private=dict(b,raw=bytes(raw));lab=P.T.labels(O/'cold-worker-v19.lbl');codec=P.T.labels(O/'cold-decoder-v19.lbl');life=P.T.labels(O/'host-life-v12.lbl');spec=json.loads((O/'cold-worker-layout-v19.json').read_text())
 def execute(corruption=None,activation='immediate',guards=None):
  m=N.fresh(private);m.ram[2][:]=bytes([0x9d])*8192;m.ram[3][:]=bytes([0x6b])*8192
  # Exact existing common-worker descriptor supplies these two whole verified
  # rows and zeroes8state pages. The new shared branch/actual common call is
  # explicitly not implemented or claimed by this isolated input fixture.
  m.ram[2][:0x800]=bytes(0x800)
  for i,page in enumerate([617,619]):
   at=1048592+1024*page;m.ram[2][0x1000+i*1024:0x1400+i*1024]=private['raw'][at:at+1024]
  m.ram[2][0x1fe0:0x1ff0]=bytes(16);m.ram[3][0x1fe0:0x1ff0]=bytes(16)
  m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=38,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,Player_X_Position=48,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160)
  m.ppuctrl=160;m[0x2001]=0;m.corrupt_at=corruption if activation=='immediate'else None;c=N.NesMPU(memory=m,pc=lab['PpColdBoot']);c.p=0x25;c.sp=224;c.stPushWord(0x5aff);low=c.sp;worker_cuts=set();actual_codecs=0;original_init=0;readstart=m.ppu_reads;cold_worker_active=True
  for name,value in(guards or {}).items():
   if name=='I':c.p&=~4
   elif name.startswith('RAM'):
    bank,at=map(int,name[3:].split(':'));m.ram[bank][at]=value
   else:N.put(m,**{name:value})
  for _ in range(3000000):
   if c.pc==0x5b00:break
   low=min(low,c.sp)
   if cold_worker_active and 0xc100<=c.pc<0xc300:
    # Live-source bytes are staging/decoder bytes in this phase, so raw
    # actor/ready byte values have no meaning. No constructor has executed,
    # and the resident auth commit remains invalid in both physical banks.
    worker_cuts.add(c.pc);assert original_init==0 and not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0]and c.p&4 and N.get(m,'DisableScreenFlag')and not N.get(m,'Mirror_PPUMASK')&24 and m[0x2001]==0
   if c.pc==codec['PpLdDecode']:
    actual_codecs+=1
    if actual_codecs==3:cold_worker_active=False
    if activation=='metadata-output'and actual_codecs==2:m.corrupt_at=corruption
   if c.pc==life['PpHostInit']:original_init+=1
   assert m[c.pc]!=0,('Cold component BRK',hex(c.pc),corruption);c.step()
  else:raise AssertionError(('Cold worker bound',hex(c.pc),corruption))
  assert c.sp==224
  return m,c,dict(C=bool(c.p&1),CPU=c.processorCycles,minimum_SP=low,buffered_PPU_reads=m.ppu_reads-readstart,decoder_entries=actual_codecs,original_actor_constructor_calls=original_init,distinct_cold_worker_instruction_PC=len(worker_cuts))
 m,c,positive=execute();assert positive['C']and positive['decoder_entries']==3 and positive['original_actor_constructor_calls']==1
 runtime=(O/'native-runtime-v18.bin').read_bytes();metadata=(O/'native-metadata-v18.bin').read_bytes();expected=C.host(b)
 mutable=[life[n]+2-0xa000 for n in ['ColdRead','ColdWrite']];diff=[i for i,(a,z)in enumerate(zip(m.ram[3],runtime))if a!=z]
 assert diff==mutable,(diff,mutable)
 assert bytes(m.ram[2][0x800:0x800+len(metadata)])==metadata
 assert bytes(m.ram[2][:0x800])==bytes(expected.s[:0x800]),[(hex(i),a,z)for i,(a,z)in enumerate(zip(m.ram[2][:0x800],expected.s[:0x800]))if a!=z][:16]
 assert m.ram[2][0xab]==0xa7 and m.ram[2][0xac]==0
 assert m.ram[2][0x60e:0x61c].hex()=='8038008000db96ff000000000000'and m.ram[2][0x6cf]==5
 assert not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0]
 failures=[]
 for title,at,activation in [('bootstrap-readback',(2,0x120),'immediate'),('staged-input-readback',(2,0x500),'immediate'),('decoded-runtime-readback',(3,0),'immediate'),('decoded-metadata-readback',(2,0x800),'metadata-output')]:
  z,cc,result=execute(at,activation);assert not result['C']and z.ram[2][0xab]!=0xa7 and not z.ram[2][0x1fe0]and not z.ram[3][0x1fe0],(title,result)
  failures.append(dict(name=title,**result))
 guards=[]
 for item in [{'I':0},{'SelectedCharacter':37},{'DisableScreenFlag':0},{'Mirror_PPUMASK':24},{'NmiDisable':0},{'RAM2:8160':167},{'RAM3:8160':167},{'RAM2:171':167},{'RAM2:1550':128}]:
  z,cc,result=execute(guards=item);assert not result['C']and result['buffered_PPU_reads']==0 and result['decoder_entries']==0,(item,result);guards.append(item)
 assert bytes(m.ram[2][0x200:0x235])==bytes(53)
 q=dict(passed=True,private_CPU_only=True,native_emulator=False,host_ROM_created=False,shared_sources_changed=False,base_ROM_SHA256=C.E.C.PIN,physical_carriers=POOL,payload_bytes=len(payload),physical_spare=44032-len(payload),positive=positive,corruption_fail_closed=failures,cold_guard_rejections=guards,complete_live_source_state_matches_fresh_constructor=True,runtime_exact_except_two_declared_cold_SMC_high_bytes=True,metadata_and_services_exact=True,both_headers_remain_unpublished=True,cold_code_and_decoder_never_execute_initialized_source_state=True,source_audio_quiet_WIP=True,cold_packet_execution_checked=dict(uninitialized=True,forcedblank=True,SEI=True,both_headers_invalid=True,packet_zeroed_before_live=True),bootstrap_scope='The existing common-worker two-row descriptor is input, not an executed new shared route: rows617/619 verified then supplied at D000/D400 with8source pages zero. All subsequent scattered physical PPU reads, independent reread verification, three lossless decodes with per-byte destination readback, source zero/copy and actual constructor execute6502.',required_next=['Persist root conditional cold-only packet execution amendment with these conditions.','Source-funded third-owner common manager/8B bootstrap descriptor/retirement/cold mapping/headers and native service routing.','Actual combined native Main/IRQ/menu/scene/death/controls/firstpipe tests; original native damage/combat and palette remain separate.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'tools/reference/prince_cold_worker_1102_v19.s',O/'cold-decoder-v19.bin',O/'cold-worker-v19.bin',O/'cold-pool-v19.bin',O/'cold-worker-layout-v19.json',O/'host-ingress-CPU-v18.json',C.E.C.BASE]})
 (O/'cold-worker-CPU-v19.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','physical_carriers','corruption_fail_closed']}));print(json.dumps(failures))


if __name__=='__main__':main()
