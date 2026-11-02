"""43-carrier backing and decode proof for the all-bound private native image."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_host_services_1102_v18 as C
import measure_prince_lzdict_1102_v9 as D
P,O=C.P,C.O


def main():
 h=C.host(C.W.scoped_load(C.E.C.BASE));runtime=bytearray(h.m.ram[3][:0x1fdf]);state=(O/'host-state-code-v12.bin').read_bytes();services=(O/'host-services-v18.bin').read_bytes();metadata=(O/'prince-pose-packets-v11.bin').read_bytes()+services
 life=P.T.labels(O/'host-life-v12.lbl');new=P.T.labels(O/'host-services-v18.lbl');old=life['PpHostInit'];tail=bytes([0x4c,old&255,old>>8]);assert runtime[-3:]==tail
 runtime[-2:]=new['PpNativeInit'].to_bytes(2,'little')
 # Unmodified codec remains qualified/frozen. This successor changes only
 # its input-fragment page from C2 to C3, leaving cold C100..C300 available
 # for the typed staging worker until the final state decode overwrites it.
 decoder=bytearray((O/'lzdict-v9.bin').read_bytes());pattern=bytes([0xa9,0xc2,0x8d]);assert decoder.count(pattern)==1;at=decoder.index(pattern)+1;decoder[at]=0xc3
 lab=P.T.labels(O/'lzdict-v9.lbl');rows=[]
 for name,data,dest,start in [('runtime',bytes(runtime),0xa000,0xc500),('metadata',metadata,0xc800,None),('state_code',state,0xc100,0xc400)]:
  packed=D.encode(data)
  if start is None:start=0xdd32-len(packed)
  split=min(start+len(packed),0xdc00);tail=packed[split-start:];addresses=list(range(start,split))+list(range(0xc300,0xc300+len(tail)))
  class Mem(list):
   def __getitem__(self,i):
    if isinstance(i,int)and getattr(self,'watch',False)and self.cursor<len(addresses)and i==addresses[self.cursor]:self.cursor+=1
    return super().__getitem__(i)
   def __setitem__(self,i,v):
    if isinstance(i,int)and getattr(self,'watch',False)and dest<=i<dest+len(data):assert i not in addresses[self.cursor:],('Overwrite unread staged source',name,hex(i))
    return super().__setitem__(i,v)
  m=Mem([0]*65536);m[0xc000:0xc000+len(decoder)]=decoder;m[start:split]=packed[:split-start];m[0xc300:0xc300+len(tail)]=tail
  def word(label,value,off=0):a=lab[label]+off;m[a:a+2]=value.to_bytes(2,'little')
  word('PpLdLoad',start,1);word('PpLdStore',dest,1);word('PpLdRemain',len(data));m.cursor=0;m.watch=True;before=bytes(m)
  c=P.T.NesMPU(memory=m,pc=lab['PpLdDecode']);c.sp=224;c.stPushWord(0x5ffe);low=c.sp
  for _ in range(2000000):
   if c.pc==0x5fff:break
   low=min(low,c.sp);assert m[c.pc]!=0,(name,hex(c.pc));c.step()
  else:raise AssertionError(('Actual decoder bound',name))
  assert bytes(m[dest:dest+len(data)])==data and m.cursor==len(addresses)and c.sp==224
  allowed=set(range(dest,dest+len(data)))|set(range(0xc000,0xc000+len(decoder)))|set(range(0x101+low,0x200));assert all(before[i]==m[i]for i in range(65536)if i not in allowed)
  (O/f'native-{name}-v18.bin').write_bytes(data);(O/f'native-{name}-v18.lzdict').write_bytes(packed)
  rows.append(dict(name=name,uncompressed_bytes=len(data),compressed_bytes=len(packed),destination_half_open=[dest,dest+len(data)],source_half_open=[start,split],source_fragment_half_open=[0xc300,0xc300+len(tail)]if tail else None,CPU=c.processorCycles,unread_source_preserved=True,output_SHA256=hashlib.sha256(data).hexdigest()))
 (O/'native-decoder-v18.bin').write_bytes(decoder)
 total=31072+len(decoder)+sum(q['compressed_bytes']for q in rows)
 q=dict(passed=True,private_CPU_only=True,native_emulator=False,host_ROM_created=False,base_ROM_SHA256=C.E.C.PIN,granted_carriers=43,pool_bytes=44032,art_bytes=31072,decoder_bytes=len(decoder),codec_successor_only_change=dict(file_offset=at,old=0xc2,new=0xc3,reason='Input fragment moves C200 to C300; retain private cold worker below C300 until last decode.'),decoded_images=rows,physical_bytes_before_typed_cold_worker_descriptor=total,physical_spare_before_typed_cold_worker_descriptor=44032-total,cold_worker_budget=512,spare_after_512B_cold_worker_reservation=44032-total-512,runtime_half_open=[0xa000,0xbfdf],runtime_spare_before_header=1,original_state_code_live=[0xc0b0,0xc60f],state_decode_temporary=[0xc100,0xc65f],metadata_and_services_half_open=[0xc800,0xc800+len(metadata)],remaining_owned_metadata_tail=0xdd32-0xc800-len(metadata),finalizer_tailcalls_native_constructor=True,scope='Actual all-bound source/world/native/quiet-event image and exact one-byte codec successor. Last state decode may overwrite the cold worker after it jumps into C000 decoder, whose return enters existing RAM3 finalizer. Typed PPU staging/copy verification/shared owner manager and publication remain to be implemented/measured.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'host-services-v18.bin',O/'host-state-code-v12.bin',O/'lzdict-v9.bin',O/'native-decoder-v18.bin',*[O/f'native-{name}-v18.bin'for name in ['runtime','metadata','state_code']],R/'docs/qa/allocations/prince-extra-carrier-1102-v14.json',R/'docs/qa/allocations/prince-executable-state-1102-v15.json']})
 (O/'native-storage-v18.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}));assert q['spare_after_512B_cold_worker_reservation']>=0


if __name__=='__main__':main()
