"""Exact bit-token dictionary codec fit; actual6502 decoder, in-memory fixtures."""
from collections import Counter,defaultdict
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_core_1101_v1 as B
from private_build_outputs_v1 import validate
P,O=B.P,B.O


def encode(data):
 positions=defaultdict(list);matches=[]
 for i in range(len(data)):
  best=(0,0)
  for at in reversed(positions[data[i:i+3]]):
   distance=i-at
   if distance>4095:break
   n=0
   while n<18 and i+n<len(data)and data[at+n]==data[i+n]:n+=1
   if n>best[0]:best=(n,distance)
   if n==18:break
  matches.append(best);positions[data[i:i+3]].append(i)
 dictionary=[v for v,n in Counter(data).most_common(16)]
 dictionary+=(list(range(256))[:16-len(dictionary)])
 for iteration in range(3):
  lookup={v:i for i,v in enumerate(dictionary)};n=len(data);cost=[0]*(n+1);choice=[1]*n
  for i in range(n-1,-1,-1):
   v=(6 if data[i]in lookup else 10)+cost[i+1];step=1
   for size in range(3,matches[i][0]+1):
    candidate=17+cost[i+size]
    if candidate<v:v=candidate;step=size
   cost[i]=v;choice[i]=step
  literals=Counter();i=0
  while i<n:
   size=choice[i]
   if size==1:literals[data[i]]+=1
   i+=size
  if iteration<2:
   dictionary=[v for v,n in literals.most_common(16)];dictionary+=list(range(16-len(dictionary)))
 bits=[]
 def emit(v,n):bits.extend((v>>bit)&1 for bit in range(n))
 i=0
 while i<n:
  size=choice[i]
  if size==1:
   emit(0,1);v=data[i]
   if v in lookup:emit(1,1);emit(lookup[v],4)
   else:emit(0,1);emit(v,8)
  else:
   distance=matches[i][1];emit(1,1);emit(distance&255,8);emit(((distance>>8)<<4)|(size-3),8)
  i+=size
 assert len(bits)==cost[0];out=bytearray(dictionary)
 for start in range(0,len(bits),8):out.append(sum(v<<bit for bit,v in enumerate(bits[start:start+8])))
 return bytes(out)


def main():
 src=R/'tools/reference/prince_lzdict_decoder_1102_v9.s';cfg=O/'lzdict-v9.cfg';cfg.write_text('MEMORY{M:start=$c000,size=$100,file=%O;}SEGMENTS{DECODER:load=M,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',src,'-o',O/'lzdict-v9.o'],[cc/'ld65.exe','-C',cfg,O/'lzdict-v9.o','-o',O/'lzdict-v9.bin','-Ln',O/'lzdict-v9.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 decoder=(O/'lzdict-v9.bin').read_bytes();lab=P.T.labels(O/'lzdict-v9.lbl');rows=[]
 for name,dest,start in [('runtime',0xa000,0xc500),('state_code',0xc100,0xc400),('metadata',0xc800,None)]:
  data=(O/f'world-{name}-v8.bin').read_bytes();packed=encode(data)
  if start is None:start=0xdd32-len(packed)
  split=min(start+len(packed),0xdc00);tail=packed[split-start:];addresses=list(range(start,split))+list(range(0xc200,0xc200+len(tail)))
  class Mem(list):
   def __getitem__(self,i):
    if isinstance(i,int)and getattr(self,'watch',False)and self.cursor<len(addresses)and i==addresses[self.cursor]:self.cursor+=1
    return super().__getitem__(i)
   def __setitem__(self,i,v):
    if isinstance(i,int)and getattr(self,'watch',False)and dest<=i<dest+len(data):assert i not in addresses[self.cursor:],('Overwrite unread source',name,hex(i),self.cursor)
    return super().__setitem__(i,v)
  m=Mem([0]*65536);m[0xc000:0xc000+len(decoder)]=decoder;m[start:split]=packed[:split-start];m[0xc200:0xc200+len(tail)]=tail
  def word(n,v,off=0):at=lab[n]+off;m[at:at+2]=v.to_bytes(2,'little')
  word('PpLdLoad',start,1);word('PpLdStore',dest,1);word('PpLdRemain',len(data));m.cursor=0;m.watch=True;before=bytes(m)
  c=P.T.NesMPU(memory=m,pc=lab['PpLdDecode']);c.sp=224;c.stPushWord(0x5ffe);low=c.sp
  for _ in range(2000000):
   if c.pc==0x5fff:break
   low=min(low,c.sp);assert m[c.pc]!=0,(name,hex(c.pc));c.step()
  else:raise AssertionError(('Dictionary cold decode bound',name))
  assert c.sp==224 and bytes(m[dest:dest+len(data)])==data,(name,len(packed),next(((i,a,b)for i,(a,b)in enumerate(zip(m[dest:dest+len(data)],data))if a!=b),None))
  assert m.cursor==len(addresses)
  allowed=set(range(dest,dest+len(data)))|set(range(0xc000,0xc000+len(decoder)))|set(range(0x101+low,0x200))
  assert all(before[i]==m[i]for i in range(65536)if i not in allowed)
  (O/f'world-{name}-v9.lzdict').write_bytes(packed)
  rows.append(dict(name=name,uncompressed_bytes=len(data),compressed_bytes=len(packed),dictionary_bytes=16,destination_half_open=[dest,dest+len(data)],source_half_open=[start,split],temporary_source_tail_half_open=[0xc200,0xc200+len(tail)]if tail else None,CPU=c.processorCycles,unread_source_preserved=True,output_SHA256=hashlib.sha256(data).hexdigest()))
 total=31072+len(decoder)+sum(r['compressed_bytes']for r in rows)
 q=dict(passed=True,private_codec_only=True,common_codec_supported=False,decoder_bytes=len(decoder),decoder_half_open=[0xc000,0xc000+len(decoder)],rows=rows,physical_bytes_before_lifecycle_descriptor=total,spare_42pages=43008-total,semantics='Literal dictionary changes only lossless cold storage. Identical original source/script/art/native bytes execute after decode; dictionary remains inside cold decoder prefix below source-code C100.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),src,*[O/f'world-{n}-v8.bin'for n in ['runtime','state_code','metadata']]]})
 (O/'world-codec-v9.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
