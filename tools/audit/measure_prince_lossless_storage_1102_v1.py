"""Private codec/CPU cost only; no common-loader codec or host ROM claim."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,subprocess
import audit_prince_pool_1102_v1 as A
from private_build_outputs_v1 import validate
from verify_native_relocation import NesMPU
R,O=A.R,A.O


def encode(data):
 out=bytearray();positions=defaultdict(list);i=0
 while i<len(data):
  flag=len(out);out.append(0)
  for bit in range(8):
   if i==len(data):break
   best=(0,0)
   for at in reversed(positions[data[i:i+3]][-128:]):
    distance=i-at
    if distance>4095:break
    n=0
    while n<18 and i+n<len(data)and data[at+n]==data[i+n]:n+=1
    if n>best[0]:best=(n,distance)
   n,distance=best
   if n>=3:out[flag]|=1<<bit;out.extend([distance&255,((distance>>8)<<4)|(n-3)])
   else:n=1;out.append(data[i])
   for at in range(i,i+n):positions[data[at:at+3]].append(at)
   i+=n
 return bytes(out)


def main():
 src=R/'tools/reference/prince_lzss_decoder_1102_v1.s';cfg=O/'lzss.cfg'
 cfg.write_text('MEMORY{M:start=$c000,size=$400,file=%O;}SEGMENTS{DECODER:load=M,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',src,'-o',O/'lzss.o'],[cc/'ld65.exe','-C',cfg,O/'lzss.o','-o',O/'lzss.bin','-Ln',O/'lzss.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 code=(O/'lzss.bin').read_bytes();labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'lzss.lbl').read_text(),re.M)}
 rows=[]
 for file,dest in [('prince-core.bin',0xa000),('prince-pose-packets.bin',0xc800)]:
  data=(O/file).read_bytes();packed=encode(data)
  # Both staging modes stay inside the already granted state/metadata span.
  # The in-place mode ends at DD32; every unread source byte is protected.
  for inplace in [False,True]if dest==0xc800 else[False]:
   start=0xdd32-len(packed)if inplace else(0xc800 if dest==0xa000 else 0x9000)
   fragmented=inplace
   split=max(start,0xdc00)if fragmented else start+len(packed)
   tail=packed[split-start:]if fragmented else b''
   addresses=list(range(start,split))+(list(range(0xc200,0xc200+len(tail)))if fragmented else[])
   class Mem(list):
    def __getitem__(self,i):
     if isinstance(i,int)and getattr(self,'watch',False)and self.cursor<len(addresses)and i==addresses[self.cursor]:self.cursor+=1
     return super().__getitem__(i)
    def __setitem__(self,i,v):
     if isinstance(i,int)and getattr(self,'watch',False)and dest<=i<dest+len(data):
      assert i not in self.unread[self.cursor:],('Overwrite unread compressed source',file,inplace,hex(i),self.cursor)
     return super().__setitem__(i,v)
   m=Mem([0]*65536);m[0xc000:0xc000+len(code)]=code
   if fragmented:m[start:split]=packed[:split-start];m[0xc200:0xc200+len(tail)]=tail
   else:m[start:start+len(packed)]=packed
   def word(name,value,plus=0):at=labels[name]+plus;m[at:at+2]=value.to_bytes(2,'little')
   word('PpLzLoad',start,1);word('PpLzStore',dest,1);word('PpLzRemain',len(data))
   before=bytes(m);m.cursor=0;m.unread=addresses;m.watch=True
   c=NesMPU(memory=m,pc=labels['PpLzDecode']);c.sp=224;c.stPushWord(0x5ffe);minimum=224
   for steps in range(500000):
    if c.pc==0x5fff:break
    minimum=min(minimum,c.sp);assert m[c.pc]!=0,hex(c.pc);c.step()
   else:raise AssertionError('Decoder instruction bound')
   assert c.sp==224 and bytes(m[dest:dest+len(data)])==data
   assert m.cursor==len(addresses),(file,m.cursor,len(addresses))
   allowed=set(range(dest,dest+len(data)))|set(range(0xc000,0xc000+len(code)))|set(range(0x101+minimum,0x200))
   assert all(before[i]==m[i]for i in range(65536)if i not in allowed)
   rows.append(dict(input=file,source_bytes=len(data),compressed_bytes=len(packed),inplace=inplace,source_half_open=[start,start+len(packed)],temporary_source_tail_half_open=[0xc200,0xc200+len(tail)]if fragmented else None,destination_half_open=[dest,dest+len(data)],CPU=c.processorCycles,minimum_SP=minimum,unread_input_never_overwritten=True,output_SHA256=hashlib.sha256(data).hexdigest()))
  (O/(file+'.lzss')).write_bytes(packed)
 total=31072+sum(r['compressed_bytes']for r in rows if not r['inplace'])+len(code)
 q=dict(passed=True,private_codec_cost_only=True,host_ROM_created=False,common_loader_codec_supported=False,decoder_bytes=len(code),decoder_cold_temporary_half_open=[0xc000,0xc000+len(code)],rows=rows,physical_bytes_with_uncompressed31KBart_and_decoder=total,spare_in_granted42page_pool=43008-total,remaining=['No common bootstrap/router/cold-loader codec integration is claimed.','Current source core still has fixture environment callbacks; new host leaves change compression and must be measured again.','Decoder temporarily executes in original-state C000.. before source initialization; it must return before that state is initialized.','Actual copied-source data, authentication, mapper/cold protocol and ISR cuts need separate current-host proof.'],bindings={str(p.relative_to(R)):A.sha(p)for p in[Path(__file__),src,O/'prince-core.bin',O/'prince-pose-packets.bin']})
 (O/'lossless-storage-cost.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
