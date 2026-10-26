"""Build the deterministic MMC5 CV3 fixed-E clone after every final link."""
from pathlib import Path
import hashlib,json,re
PAYLOADS={"primary72.dmc":(0x1140,1089,"c1b646c36508ad4d134078c8184fea7bd632f50127c5f2af6550e89097cbda01"),"sypha75.dmc":(0x15c0,193,"137fc604fe0c0cbf8c28733411e2397cc00e72188db755a00eb8ad27da037331")}
def prepare(root,out):
 raw=bytearray(out.read_bytes());assert len(raw)==2097168
 labels={v[2].lstrip('.'):int(v[1],16)for l in out.with_suffix('.lbl').read_text().splitlines()if len(v:=l.split())==3}
 for line in out.with_suffix('.dbg').read_text().splitlines():
  if line.startswith('sym\t'):
   z=dict(part.split('=',1)for part in line[4:].split(',')if'='in part)
   if'val'in z and z.get('name')=='"CvAudioPlay"':labels['CvAudioPlay']=int(z['val'],0)
 assert labels['Cv3DmcManagerStart']==0xdaf7
 assert labels['CvAudioPlay']==0xa443 and raw[16+27*8192+0x443:16+27*8192+0x445]==bytes((0xa5,0xe2)),"Source CV1 input-A/NZ overwrite contract changed"
 end=labels['Cv3DmcManagerEnd'];assert end<=0xde11
 base=16+125*8192;fixed=16+127*8192;linked=bytes(raw[base:base+8192]);mirror=bytearray(raw[fixed:fixed+8192])
 declared=[]
 for name,(offset,n,digest)in PAYLOADS.items():
  b=(root/'audio/cv3'/name).read_bytes();assert len(b)==n and hashlib.sha256(b).hexdigest()==digest
  mirror[offset:offset+n]=b;declared.append([offset,offset+n])
 lo=0x1af7;hi=end-0xc000;mirror[lo:hi]=linked[lo:hi];declared.append([lo,hi])
 # Future TMNT integration must explicitly advertise its relocated cold block.
 if 'SamusAudioCold'in labels:
  assert labels['SamusAudioCold']==0xd700
  assert 'TnAudioAdapterReturn'in labels
  mirror[0x1700:0x1af7]=linked[0x1700:0x1af7];declared.append([0x1700,0x1af7])
 for i,(x,y)in enumerate(zip(mirror,raw[fixed:fixed+8192])):
  assert x==y or any(a<=i<b for a,b in declared)
 raw[base:base+8192]=mirror;out.write_bytes(raw)
 receipt=dict(ROM_sha256=hashlib.sha256(raw).hexdigest(),original_fixed_bank_sha256=hashlib.sha256(raw[fixed:fixed+8192]).hexdigest(),mirror_sha256=hashlib.sha256(mirror).hexdigest(),declared_overlay_offsets=declared,manager_bytes=hi-lo,all_other_fixed_bytes_exact=True)
 out.with_suffix('.cv3-mirror.json').write_text(json.dumps(receipt,indent=2)+'\n')
 return receipt
