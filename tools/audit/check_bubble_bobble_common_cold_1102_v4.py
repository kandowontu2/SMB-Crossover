"""CPU-only common-kernel funding experiment. No ROM or shared source writes."""
import copy,json,hashlib
from pathlib import Path
import prepare_bubble_bobble_common_cold_1102_v4 as P
import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address
O=P.O


def patched(base,parts):
 b=dict(base);raw=bytearray(base['raw'])
 for bank,start,blob in parts:
  at=16+bank*8192+(start&8191);raw[at:at+len(blob)]=blob
 b['raw']=bytes(raw);return b


def call(m,target,*,bank=193,nmi=False,flags=0x71):
 for name,val in [('SafecallA_SMC',83),('FarcallJmpTarget_SMC',target&255)]:m[address(m.bundle,name)+1]=val
 m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=target>>8
 c=N.NesMPU(memory=m,pc=address(m.bundle,'FarCallCommon'));c.a=bank;c.x=71;c.y=109;c.p=flags;c.sp=224;c.stPushWord(0x5aff)
 count=0;cuts=0;low=c.sp
 for i in range(700000):
  if c.pc==0x5b00:break
  low=min(low,c.sp)
  if nmi and i%4096==100 and cuts<64:
   pc,sp=c.pc,c.sp;smc=bytes(m[0x15a:0x17b]);maps=list(m.rawtags);c.nmi()
   for _ in range(10000):
    assert m[c.pc]!=0,('NMI BRK',hex(c.pc));c.step()
    if c.pc==pc and c.sp==sp:break
   else:raise AssertionError('NMI return bound')
   assert bytes(m[0x15a:0x17b])==smc and m.rawtags==maps;cuts+=1
  assert m[c.pc]!=0,('BRK',hex(c.pc),m.rawtags)
  c.step();count+=1
 else:raise AssertionError(('cold bound',hex(c.pc)))
 assert c.sp==224
 return dict(A=c.a,X=c.x,Y=c.y,P=c.p,CPU=c.processorCycles,instructions=count,min_SP=low,disabled_NMI_cuts=cuts)


def ready(b):
 m=N.fresh(b);N.put(m,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,HorizontalScroll=23,VerticalScroll=7)
 m.ram[2][:]=bytes([0xa5])*8192;m.ram[3][:]=bytes([0x5a])*8192
 m[3:11]=[19,38,57,76,95,114,133,152]
 return m


def main():
 base=P.scoped_load(P.ROM);assert P.sha(base['raw'])==P.PIN
 layout=json.loads((O/'common-cold-layout.json').read_text());split=layout['split_pad_proposal'];ex=layout['factored_Ex_frame']
 parts=[(123,0xaf40,(O/'common-split.bin').read_bytes()),(123,0xb9d6,(O/'common-split-map.bin').read_bytes()),(65,0xae00,(O/'common-Ex-frame.bin').read_bytes()),(65,0xb011,(O/'common-Ex-fixed-ABI.bin').read_bytes())]
 new=patched(base,parts);results={};cases=[]
 for label,fault in [('cold',None),('code-readback',(3,2048)),('state-readback',(2,80)),('WRAM-protected','locked'),('disabled-NMI',None)]:
  pair=[ready(b)for b in[base,new]];out=[]
  for m in pair:
   if fault=='locked':m.protection=[0,0]
   elif fault:m.corrupt_at=fault
   smc=bytes(m[0x15a:0x17b]);scratch=bytes(m[3:11]);maps=list(m.rawtags)
   r=call(m,0xae6a,nmi=label=='disabled-NMI');out.append(r)
   assert bytes(m[3:11])==scratch and m.rawtags==maps
   # The harness sets these three incoming SMC arguments; the complete frame
   # preserves them and every other preexisting operand byte.
   for i in range(0x15a,0x17b):
    if i not in[address(m.bundle,'SafecallA_SMC')+1,address(m.bundle,'FarcallJmpTarget_SMC')+1,address(m.bundle,'FarcallJmpTarget_SMC')+2,address(m.bundle,'NextBank_SMC')+1,address(m.bundle,'SafereturnA_SMC')+1]:assert m[i]==smc[i-0x15a]
   assert m.ppuctrl==160 and m.toggle==0
  assert pair[0].ram[2:4]==pair[1].ram[2:4],label
  assert [out[0][n]for n in['A','X','Y','P']]==[out[1][n]for n in['A','X','Y','P']],label
  if label in['cold','disabled-NMI']:
   assert out[1]['P']&1 and pair[1].ram_writes[-1]==(2,0x1fe0,0xa7)
   assert pair[1].ram[2][0x1fe0:0x1ff0]==pair[1].ram[3][0x1fe0:0x1ff0]
   # Warm checks do not read CHR or write a cache byte.
   before=pair[1].ppu_reads;writes=len(pair[1].ram_writes);warm=call(pair[1],0xae6a)
   assert warm['P']&1 and pair[1].ppu_reads==before and len(pair[1].ram_writes)==writes
  else:assert not out[1]['P']&1 and pair[1].ram[2][0x1fe0]!=0xa7
  cases.append(dict(case=label,original=out[0],factored=out[1]))
 results['exact_existing_Ex_full_frame_differentials']=cases
 negatives=[]
 for fields in[dict(SelectedCharacter=0),dict(OperMode=0),dict(FamilyMainCommit=0),dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)]:
  m=ready(new);N.put(m,**fields);before=[bytes(r)for r in m.ram];writes=len(m.ram_writes);reads=m.ppu_reads;r=call(m,0xae6a)
  assert not r['P']&1 and before==[bytes(v)for v in m.ram]and len(m.ram_writes)==writes and m.ppu_reads==reads
  negatives.append(fields)
 results['existing_Ex_cold_admission_negatives']=negatives
 # Bub uses real native-private bytes as synthetic CHR-carrier inputs in the
 # in-memory bus only. No physical candidate or admitted owner is produced.
 image=(O/'native-private.bin').read_bytes();art=(O/'native-helper.chr').read_bytes()
 raw=bytearray(new['raw']);pages=[301,305,337,362,363,440,819,666]
 for i,page in enumerate(pages):raw[1048592+page*1024:1048592+(page+1)*1024]=image[i*1024:(i+1)*1024]
 raw[1048592+441*1024:1048592+442*1024]=art
 bb=dict(new);bb['raw']=bytes(raw);m=ready(bb)
 for r in m.ram[2:4]:r[0x1fe0]=0
 state=bytes(m.ram[2]);m[address(bb,'R3')]=split['labels']['BbColdBBDescriptor']&255;m[address(bb,'R4')]=split['labels']['BbColdBBDescriptor']>>8
 r=call(m,split['labels']['BbColdWorker'],bank=251)
 assert r['P']&1 and bytes(m.ram[3])==image
 assert m.ram[2][:1024]==bytes(1024)and bytes(m.ram[2][1024:4096])==state[1024:4096]
 assert bytes(m.ram[2][4096:5120])==art and bytes(m.ram[2][5120:])==state[5120:]
 assert m.ram[2][0x1fd0:0x1fd3]==bytes([0xa5])*3 and m.ram[2][0x1fe0]!=0xa7 and m.ram[3][0x1fe0]!=0xa7
 assert m.upper==0 and m.ppu_reads==2*9216+18
 results['Bub_direct_worker_only']=dict(**r,source_image_SHA256=P.sha(image),exact_code_bytes=8192,zeroed_state_bytes=1024,all_other_C2_bytes_retained=True,shared_clock_retained=True,headers_unpublished=True,buffered_PPU_reads=m.ppu_reads,public_owner_admitted=False)
 q=dict(passed=True,proposal_only=True,ROM_SHA256=P.PIN,ROM_written=False,shared_source_written=False,resident_granted=False,checks=results,layout=layout,scope='Current3 Ex full loader frame is byte-source-bound except its authenticated payload cookie, then factored only in an in-memory CPU fixture. Existing Ex public ABI/header/PPU/maps/protection behavior is compared. Direct Bub full-page worker has no owner admission. This is not a complete new-owner loader/retirement/router or native gameplay proof.',bindings={p.relative_to(P.R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),P.R/'tools/reference/bubble_bobble_common_cold_1102_v4.inc',P.R/'tools/audit/prepare_bubble_bobble_common_cold_1102_v4.py',O/'common-split.bin',O/'common-split-map.bin',O/'common-Ex-frame.bin',O/'common-Ex-fixed-ABI.bin',O/'native-private.bin']})
 (O/'common-cold-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,Ex_full_frame_cases=len(cases),negative_gates=len(negatives),Bub_state_bytes=1024,ROM_written=False)))


if __name__=='__main__':main()
