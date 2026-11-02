"""Place the existing source component and loader into owned cartridge ranges."""
import json,re,subprocess
from pathlib import Path
import prepare_shinobi_owning_graft_1101_v1 as S
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
R=S.R;BASE=R/'build/metal-storm-decline-1101-v40';O=R/'build/shinobi-cartridge-1101-v2'

def main():
 O.mkdir(exist_ok=True);b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 assert S.sha(BASE/'candidate.nes')=='128915e97e78891a585aa8f9fd904c166ca64dcd6dd1ee395fc68fd505c1e72c'
 # This is authored padding, not an inference solely from FF bytes.
 source=(R/'src/protoman.s').read_text();assert '.res $1108-(*-ProtoArtBegin), $ff' in source
 assert address(b,'ProtoArtEnd')==0xc738
 poses=address(b,'ProtoPoseRightHi')-address(b,'ProtoPoseRightLo');assert poses==27
 for face in ['Left','Right']:
  for i in range(poses):
   p=raw[location(b,'ProtoPose'+face+'Lo')+i]+256*raw[location(b,'ProtoPose'+face+'Hi')+i]
   assert 0xc000<=p<address(b,'ProtoArtEnd')
   n=raw[16+65*8192+p-0xc000];assert p+n+1<=address(b,'ProtoArtEnd')
 start=16+65*8192+0x800;capacity=1536
 assert raw[start:start+capacity]==bytes([255])*capacity
 labels_in_range=[]
 for name,s in b['syms'].items():
  if 'seg' not in s or 'ooffs' not in b['segs'][s['seg']]:continue
  at=location(b,name)
  if start<=at<start+capacity:labels_in_range.append(name)
 assert not labels_in_range,labels_in_range
 # Reuse the current component only after checking every declared host address.
 constants=0
 for file in ['component.s','resident.s']:
  for name,value in re.findall(r'^(\w+)=\$([0-9a-fA-F]+)$',(S.O/file).read_text(),re.M):
   if name in b['syms']:assert address(b,name)==int(value,16),(name,'host address changed');constants+=1
 for n in ['MetaspriteRenderLoop','GetEnemyBoundBox','X5PublishChr']:
  source=(S.O/('resident.s' if n=='X5PublishChr' else 'component.s')).read_text()
  v=int(re.search('Bank_'+n+r'=\$([0-9a-fA-F]+)',source)[1],16)
  assert v==((location(b,n)-16)//8192)|128
 (O/'shinobi-cookie.bin').write_bytes((S.O/'shinobi-cookie.bin').read_bytes())
 (O/'resident.s').write_bytes((S.O/'resident.s').read_bytes())
 (O/'resident.cfg').write_text('MEMORY{R:start=$a800,size=$0600,file=%O;}SEGMENTS{SHINOBI_RESIDENT:load=R,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g','-I',R/'tools/reference','--bin-include-dir',O,O/'resident.s','-o',O/'resident.o'],[cc/'ld65.exe','-C',O/'resident.cfg',O/'resident.o','-o',O/'resident.bin','-Ln',O/'resident.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr
 resident=(O/'resident.bin').read_bytes();assert len(resident)<=capacity
 raw[start:start+len(resident)]=resident
 pages=[506,507,508,509,510,513,515,516,517,503,504,505]
 payload=(S.O/'kernel.bin').read_bytes()[:7168]+(S.O/'metadata.bin').read_bytes()[:2048]+(S.O/'native-art.chr').read_bytes()
 ancestor=S.BASE.read_bytes()
 for i,page in enumerate(pages):
  at=16+1048576+page*1024
  assert raw[at:at+1024]==ancestor[at:at+1024],('CHR ownership changed',page)
  raw[at:at+1024]=payload[i*1024:(i+1)*1024]
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 q=dict(assembled=True,installed=False,menu_unlocked=False,ROM_sha256=S.sha(O/'candidate.nes'),resident_bytes=len(resident),PRG=dict(bank=65,start=0xa800,end=0xae00,source_padding=[0xc738,0xd108],descriptor_cases=54,existing_symbols=labels_in_range),CHR_pages=pages,host_constant_checks=constants,scope='Actual cartridge placement only. Existing menu/dispatch unchanged. Cold-loader/retirement tests and full native admission still required.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
