"""Reproduce current Mac audio source and identify its three declared pads.

Read-only grant proposal. Empty bytes alone never establish a resource.
"""
from pathlib import Path
import hashlib,json,re,subprocess
import audit_prince_pool_1102_v1 as A
from private_build_outputs_v1 import validate
R,O=A.R,A.O


def main():
 assert A.sha(A.ROM)==A.SHA;b=A.scoped_load(A.ROM)
 src=R/'src/mac_native_music.s';source=src.read_text();clauses=[
  '.res $1000-(*-LmNativeBankStart),$ff',
  '.res $200-(*-LmNativeMusicUpdate),$ff',
  '.res $1fa0-(*-LmNativeBankStart),$ff']
 for i,clause in enumerate(clauses):
  assert source.count(clause)==1
  source=source.replace(clause,f'::PrincePad{i}Begin:\n'+clause+f'\n::PrincePad{i}End:\n.export PrincePad{i}Begin,PrincePad{i}End')
 bare=re.sub(r';[^\n]*','',source)
 declared=set(re.findall(r'(?m)^[ \t]*(?:::)?([A-Za-z]\w*)[ \t]*[:=]',bare))
 declared.update(re.findall(r'\.proc\s+(\w+)',bare))
 declared.update(re.findall(r'(?m)^LmNativeWriter (\w+),',bare))
 used=set(re.findall(r'\b[A-Za-z]\w*\b',bare))
 defs=''.join(f'{n}=${A.address(b,n):04x}\n'for n in sorted((used&set(b['syms']))-declared))
 asm=O/'resident-padding.s';asm.write_text('.setcpu "6502"\n.macpack longbranch\n'+defs+source)
 pc=A.address(b,'LmNativeBankStart');at=A.location(b,'LmNativeBankStart');bank=(at-16)//8192
 cfg=O/'resident-padding.cfg';cfg.write_text(f'MEMORY{{M:start=${pc:04x},size=$2000,file=%O;}}SEGMENTS{{MAC_NATIVE_AUDIO:load=M,type=ro;}}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',asm,'-o',O/'resident-padding.o'],[cc/'ld65.exe','-C',cfg,O/'resident-padding.o','-o',O/'resident-padding.bin','-Ln',O/'resident-padding.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 code=(O/'resident-padding.bin').read_bytes();assert len(code)==8192 and code==b['raw'][at:at+8192],'Current bank differs from named source; no pad lease'
 labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'resident-padding.lbl').read_text(),re.M)}
 rows=[]
 for i in range(3):
  lo,hi=[labels[f'PrincePad{i}{suffix}']for suffix in ['Begin','End']]
  assert code[lo-pc:hi-pc]==bytes([255])*(hi-lo)
  interior=[]
  for n,s in b['syms'].items():
   if s.get('type')!='lab' or s.get('seg')!=b['syms']['LmNativeBankStart'].get('seg'):continue
   if lo<=A.address(b,n)<hi and not(n=='LmNativeAdapterEnd'and A.address(b,n)==lo):interior.append(n)
  assert not interior,interior
  rows.append(dict(physical_PRG_bank=bank,CPU_half_open=[lo,hi],bytes=hi-lo,source_res_directive=clauses[i],preimage_SHA256=hashlib.sha256(code[lo-pc:hi-pc]).hexdigest(),interior_symbols=interior))
 q=dict(passed=True,proposal_only=True,resource_granted=False,ROM_SHA256=A.SHA,whole_source_bank_exact=dict(bank=bank,bytes=len(code),sha256=hashlib.sha256(code).hexdigest()),declared_pads=rows,total_bytes=sum(v['bytes']for v in rows),consumer_closure_complete=False,remaining=['Close source audio indexed reads and all indirect playback paths before granting source-declared padding.','No loader/router has been assembled into these spans; split spans and exact fit remain unproven.','No Prince owner is added to Excitebike shared dispatch.'],bindings={str(p.relative_to(R)):A.sha(p)for p in[Path(__file__),A.ROM,src]})
 (O/'resident-padding-proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
