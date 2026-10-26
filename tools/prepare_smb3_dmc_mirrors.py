"""Generate SMB3 source DPCM clones from the FINAL linked resident bank."""
from pathlib import Path
import argparse,hashlib,json
PAYLOAD_SHA='d54ae38d695f5787915b47534de768a32116007929181888237b80c14f347b45'
SPANS={70:[(0x3980,0x4281,0x1140),(0x3000,0x3241,0x1a80),(0x6b40,0x6b81,0x1d00)],97:[(0x8800,0x8b41,0x1140)]}
def prepare(source,rom):
 source,rom=Path(source),Path(rom);raw=bytearray(rom.read_bytes());assert len(raw)==2097168
 labels={r[2].lstrip('.'):int(r[1],16)for line in rom.with_suffix('.lbl').read_text().splitlines()if len(r:=line.split())==3}
 assert 'B3CoreStart'in labels and labels['B3CoreStart']==0xcbe8
 payload=(source/'audio/smb3-native/source-payload.bin').read_bytes();assert len(payload)==36864 and hashlib.sha256(payload).hexdigest()==PAYLOAD_SHA
 fixed=bytes(raw[16+127*8192:16+128*8192]);clones=[]
 for bank,spans in SPANS.items():
  image=bytearray(fixed);declared=[]
  for lo,hi,dest in spans:image[dest:dest+hi-lo]=payload[lo:hi];declared.append([dest,dest+hi-lo])
  assert all(x==y or any(lo<=i<hi for lo,hi in declared)for i,(x,y)in enumerate(zip(fixed,image)))
  # Current fixed helper code lies INSIDE the broad Bass-data segment too.
  for lo,hi in [(0x1e15,0x1e40),(0x1ee1,0x1f00),(0x1fc1,8192)]:assert image[lo:hi]==fixed[lo:hi]
  raw[16+bank*8192:16+(bank+1)*8192]=image;clones.append(dict(bank=bank,sha256=hashlib.sha256(image).hexdigest(),declared_sample_spans=declared,all_other_final_resident_bytes_exact=True))
 rom.write_bytes(raw);receipt=dict(ROM_sha256=hashlib.sha256(raw).hexdigest(),final127_sha256=hashlib.sha256(fixed).hexdigest(),payload_sha256=PAYLOAD_SHA,clones=clones,no_old_clone_code_used=True)
 rom.with_suffix('.smb3-mirrors.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.source,a.rom),indent=2))
