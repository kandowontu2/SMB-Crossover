"""Exact44-carrier storage for v42, live/cold phase separation measured."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
import measure_prince_lzdict_1102_v9 as D
import prepare_prince_successor_manifest_1102_v26 as M
from check_tmnt_render_oa import address
P,O=A.L.P,A.O;POOL=M.POOL+[514]


def main():
 base,_,_,_=M.bundle();decoder=bytearray((O/'lzdict-v9.bin').read_bytes());pattern=bytes([0xa9,0xc2,0x8d]);assert decoder.count(pattern)==1;decoder[decoder.index(pattern)+1]=0xc3;lab=P.T.labels(O/'lzdict-v9.lbl');rows=[]
 images=[('runtime',(O/'native-runtime-v42.bin').read_bytes(),0xa000,0xc500),('metadata',(O/'native-metadata-v42.bin').read_bytes(),0xc800,None),('state_code',(O/'native-state_code-v18.bin').read_bytes(),0xc100,0xc400)]
 for name,data,dest,start in images:
  packed=D.encode(data)
  # Runtime is fully decoded before this metadata stage. Only its cold
  # fragment expands from C300..C500 to C300..C800. Worker ends beforeC300;
  # authentic source state is still absent. Metadata output begins atC800.
  if start is None:start=0xdc00+0x500-len(packed)
  split=min(start+len(packed),0xdc00);tail=packed[split-start:];assert 0xc300+len(tail)<=0xc800
  addresses=list(range(start,split))+list(range(0xc300,0xc300+len(tail)))
  class Mem(list):
   def __getitem__(self,i):
    if isinstance(i,int)and getattr(self,'watch',False)and self.cursor<len(addresses)and i==addresses[self.cursor]:self.cursor+=1
    return super().__getitem__(i)
   def __setitem__(self,i,value):
    if isinstance(i,int)and getattr(self,'watch',False)and dest<=i<dest+len(data):assert i not in addresses[self.cursor:],('Unread staged source overwritten',name,hex(i),self.cursor)
    return super().__setitem__(i,value)
  m=Mem([0]*65536);m[0xc000:0xc000+len(decoder)]=decoder;m[start:split]=packed[:split-start];m[0xc300:0xc300+len(tail)]=tail
  for label,value,off in [('PpLdLoad',start,1),('PpLdStore',dest,1),('PpLdRemain',len(data),0)]:a=lab[label]+off;m[a:a+2]=value.to_bytes(2,'little')
  m.cursor=0;m.watch=True;c=P.T.NesMPU(memory=m,pc=lab['PpLdDecode']);c.sp=224;c.stPushWord(0x5ffe)
  for _ in range(2000000):
   if c.pc==0x5fff:break
   assert m[c.pc]!=0,('Actual codec BRK',name,hex(c.pc));c.step()
  else:raise AssertionError(('Actual codec bound',name))
  assert bytes(m[dest:dest+len(data)])==data and m.cursor==len(addresses)and c.sp==224
  (O/f'native-{name}-v44.lzdict').write_bytes(packed);rows.append(dict(name=name,compressed_bytes=len(packed),uncompressed_bytes=len(data),destination_half_open=[dest,dest+len(data)],source_half_open=[start,split],source_fragment_half_open=[0xc300,0xc300+len(tail)]if tail else None,CPU=c.processorCycles,unread_source_preserved=True))
 # Qualified per-byte-readback254B decoder, byte-identical v25. Only typed
 # stream constants and physical source table gain44th granted carrier514.
 decoder=(O/'cold-decoder-v25.bin').read_bytes();codeclab=P.T.labels(O/'cold-decoder-v25.lbl');bindings={n:address(base,n)for n in ['R0','R1','SelectedCharacter','DisableScreenFlag','Mirror_PPUMASK','NmiDisable']};bindings.update(DecoderBytes=len(decoder),PpLdDecode=codeclab['PpLdDecode'],PpLdLoad=codeclab['PpLdLoad'],PpLdRemain=codeclab['PpLdRemain'],PpHostColdFinalize=P.T.labels(O/'host-life-v12.lbl')['PpHostColdFinalize'])
 for row,prefix in zip(rows,['Runtime','Metadata','State']):bindings.update({prefix+'Input':row['source_half_open'][0],prefix+'Packed':row['compressed_bytes'],prefix+'Bytes':row['uncompressed_bytes']})
 text=(R/'tools/reference/prince_cold_worker_1102_v19.s').read_text();assert text.count(',<291')==1 and text.count(',>291')==1;text=text.replace(',<291',',<291,<514').replace(',>291',',>291,>514')
 cfg=f'MEMORY{{B:start=${0xd160+len(decoder):04x},size=$100,file=%O;W:start=$c100,size=$200,file=%O;}}SEGMENTS{{BOOT:load=B,type=ro;WORKER:load=W,type=ro;}}';size=0
 for _ in range(4):
  physical=31072+len(decoder)+size;bindings.update(InitialSourcePage=physical//1024-30,InitialSourceAddress=0xc00+physical%1024)
  worker,labels=A.assemble('cold-worker-v44',''.join(f'{n}=${v:04x}\n'for n,v in bindings.items())+text,cfg)
  if size==len(worker):break
  size=len(worker)
 else:raise AssertionError('Cold worker source reference did not converge')
 art=(O/'prince-body-8x16.chr').read_bytes();payload=art+decoder+worker+b''.join((O/f'native-{n}-v44.lzdict').read_bytes()for n in ['runtime','metadata','state_code']);assert len(payload)<=len(POOL)*1024,(len(payload),len(POOL)*1024)
 (O/'cold-pool-v44.bin').write_bytes(payload)
 q=dict(passed=True,CPU_codec_only=True,actual_typed_cold_CPU_pending=True,ROM_written=False,base_SHA256=M.A.PIN,physical_carriers=POOL,physical_pages=len(POOL),pool_capacity=len(POOL)*1024,payload_bytes=len(payload),physical_spare=len(POOL)*1024-len(payload),source_art_bytes=31072,source_art_SHA256=hashlib.sha256(art).hexdigest(),decoder_bytes=len(decoder),worker_storage_bytes=len(worker),boot_half_open=[labels['PpColdBoot'],labels['PpColdBootEnd']],worker_half_open=[0xc100,labels['PpColdWorkerEnd']],decoded_images=rows,all_three_actual_decoder_outputs_exact=True,unread_staged_inputs_preserved=True,metadata_phase_fragment_half_open=[0xc300,0xc800],required_execution_amendment='Existing43+page514 physical grants only. Live RAM2 grid/battle/proxy/services throughDFA2 and41B renderer pointer tail require exact closure/CPU/root amendment; cold fragmentC300..C800 is only before source initialization/auth publication. No shared clock, new RAM or menu assumption.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-runtime-v42.bin',O/'native-metadata-v42.bin',O/'native-state_code-v18.bin',O/'cold-pool-v44.bin',O/'cold-worker-v44.bin',O/'cold-decoder-v25.bin',R/'docs/qa/allocations/prince-carrier514-1102-v35.json',M.A.BASE]})
 (O/'cold-link-storage-v44.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','physical_carriers']}))


if __name__=='__main__':main()
