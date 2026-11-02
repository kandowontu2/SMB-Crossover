"""Rebind qualified codec/typed worker to measured public source adapter."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
import measure_prince_lzdict_1102_v9 as D
O=L.O


def main():
 # Restore the one old generated layout touched by the first adaptation's
 # incomplete output-name replacement. Its exact frozen source checkpoint
 # and original CPU binding establish the preimage; no source is rewritten.
 with zipfile.ZipFile(O/'native-binding-source-v3.zip')as z:frozen_layout=z.read('receipts/cold-worker-layout-v19.json')
 old_CPU=json.loads((O/'cold-worker-CPU-v19.json').read_text());old_key=next(k for k in old_CPU['bindings']if k.replace('\\','/').endswith('/cold-worker-layout-v19.json'))
 assert hashlib.sha256(frozen_layout).hexdigest()==old_CPU['bindings'][old_key]
 if (O/'cold-worker-layout-v19.json').read_bytes()!=frozen_layout:(O/'cold-worker-layout-v19.json').write_bytes(frozen_layout)
 decoder=bytearray((O/'lzdict-v9.bin').read_bytes());pattern=bytes([0xa9,0xc2,0x8d]);assert decoder.count(pattern)==1;decoder[decoder.index(pattern)+1]=0xc3;lab=L.P.T.labels(O/'lzdict-v9.lbl');rows=[]
 images=[('runtime',(O/'public-runtime-v24.bin').read_bytes(),0xa000,0xc500),('metadata',(O/'public-metadata-v24.bin').read_bytes(),0xc800,None),('state_code',(O/'native-state_code-v18.bin').read_bytes(),0xc100,0xc400)]
 for name,data,dest,start in images:
  packed=D.encode(data)
  # Runtime is already decoded before metadata. The cold-only fragment may
  # occupy C300..C500 in this phase; original actor state is still absent.
  # Start metadata as late as that exact512B fragment permits, so expanded
  # output cannot overtake its unread high-memory input. No byte at/above
  # DD32 is used by this virtual linear source address calculation.
  if start is None:start=0xdc00+0x200-len(packed)
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
  word('PpLdLoad',start,1);word('PpLdStore',dest,1);word('PpLdRemain',len(data));m.cursor=0;m.watch=True
  c=L.P.T.NesMPU(memory=m,pc=lab['PpLdDecode']);c.sp=224;c.stPushWord(0x5ffe)
  for _ in range(2000000):
   if c.pc==0x5fff:break
   assert m[c.pc]!=0,(name,hex(c.pc));c.step()
  else:raise AssertionError(('Actual decoder bound',name))
  assert bytes(m[dest:dest+len(data)])==data and m.cursor==len(addresses)and c.sp==224
  (O/f'native-{name}-v25.bin').write_bytes(data);(O/f'native-{name}-v25.lzdict').write_bytes(packed)
  rows.append(dict(name=name,uncompressed_bytes=len(data),compressed_bytes=len(packed),destination_half_open=[dest,dest+len(data)],source_half_open=[start,split],source_fragment_half_open=[0xc300,0xc300+len(tail)]if tail else None,CPU=c.processorCycles,unread_source_preserved=True))
 q=dict(passed=True,decoded_images=rows,scope='Exact v24 source/public runtime plus original state-code, actual249B codec decode/unread staging guard. Typed254B per-byte readback worker follows unchanged source successor.')
 (O/'native-storage-v25.json').write_text(json.dumps(q,indent=2)+'\n')
 # Reuse the frozen typed worker recipe as an explicit, recorded adaptation;
 # its source and decoder algorithm stay unchanged, only stream constants,
 # input file names and owned output names change.
 source=R/'tools/audit/prepare_prince_cold_worker_1102_v19.py';text=source.read_text();text=text.replace('native-storage-v18.json','native-storage-v25.json').replace('}-v18.lzdict','}-v25.lzdict').replace('cold-decoder-v19','cold-decoder-v25').replace('cold-worker-v19','cold-worker-v25').replace('cold-worker-layout-v19','cold-worker-layout-v25').replace('cold-pool-v19','cold-pool-v25')
 env=dict(__file__=str(source),__name__='prince_cold_public_successor');exec(compile(text,str(source),'exec'),env);env['main']()
 payload=(O/'cold-pool-v25.bin').read_bytes();assert len(payload)<=44032
 report=dict(passed=True,proposal_only=True,ROM_written=False,grant=False,pool_bytes=len(payload),pool_capacity=44032,pool_spare=44032-len(payload),all_three_actual_decoder_outputs_exact=True,all_unread_staged_inputs_preserved=True,frozen_recipe_adaptation_SHA256=hashlib.sha256(text.encode()).hexdigest(),bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,O/'public-runtime-v24.bin',O/'public-metadata-v24.bin',O/'native-state_code-v18.bin',O/'cold-pool-v25.bin',O/'cold-worker-v25.bin',O/'cold-decoder-v25.bin']})
 (O/'cold-successor-v25.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='bindings'}))


if __name__=='__main__':main()
