"""Bounded ROM-backed Bubble Bobble source discovery, with no host allocation."""
from pathlib import Path
import argparse,hashlib,json,re,sys,urllib.request,zlib
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
R=Path(__file__).resolve().parents[2];O=R/'build/bubble-bobble-source-1101-v1'
ROM=Path('C:/NES/Bubble Bobble (USA).nes')
PIN='e34901acf6917495890ef79ddb33e4641ea309a803d777a27a198e8802c9b4a0'
REPO='Junior-Jones/Bubble-Bobble-NES-Static-Recomp'
UPSTREAM_PIN='5980e1a5f1731181ced5d195d85f9551d5ac7f28'
sha=lambda data:hashlib.sha256(data).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SMB-Crossover-source-audit'}),timeout=30)as r:return r.read()


def image(bank):
 raw=ROM.read_bytes();assert sha(raw)==PIN
 m=MPU();m.memory[0x8000:0xc000]=raw[16+bank*16384:16+(bank+1)*16384];m.memory[0xc000:]=raw[16+7*16384:16+8*16384]
 return m


def fetch():
 O.mkdir(exist_ok=True);raw=ROM.read_bytes();assert sha(raw)==PIN
 commit=UPSTREAM_PIN;rows=[];sources=[]
 for bank in [4,5,6,7]:
  path=f'generated/direct_c/bb_generated_bank{bank:02d}.c';url=f'https://raw.githubusercontent.com/{REPO}/{commit}/{path}';data=get(url);text=data.decode()
  count=0
  for match in re.finditer(r'BBGeneratedStep\)\{(\d+),0x([0-9A-F]+),0x([0-9A-F]+),(\d+),[^}]+\}',text):
   b,pc,op,n=int(match[1]),int(match[2],16),int(match[3],16),int(match[4]);assert b==bank
   at=16+b*16384+(pc-(0xc000 if bank==7 else 0x8000));code=raw[at:at+n]
   assert len(code)==n and code[0]==op,(bank,hex(pc),op,code.hex())
   rows.append([bank,pc,list(code)]);count+=1
  assert count;sources.append(dict(url=url,bytes=len(data),sha256=sha(data),verified_instruction_entries=count))
 notice_url=f'https://raw.githubusercontent.com/{REPO}/{commit}/THIRD-PARTY-NOTICES.txt';notice=get(notice_url)
 (O/'upstream-notices.txt').write_bytes(notice)
 save(O/'instruction-index.json',dict(ROM_sha256=PIN,upstream_commit=commit,upstream_role='Instruction boundary discovery only; every opcode/operand is recovered from and checked against local original ROM.',sources=sources,rows=rows))
 prg=raw[16:16+131072];chrdata=raw[16+131072:]
 save(O/'discovery.json',dict(ROM=str(ROM),ROM_sha256=PIN,bytes=len(raw),header=raw[:16].hex(),PRG_bytes=len(prg),CHR_bytes=len(chrdata),PRG_crc32=f'{zlib.crc32(prg):08x}',CHR_crc32=f'{zlib.crc32(chrdata):08x}',mapper=1,mapper_name='MMC1',PRG_16k_banks=8,CHR_8k_banks=4,WRAM_in_donor_header=0,vectors={name:prg[-6+i]+256*prg[-5+i]for name,i in [('NMI',0),('reset',2),('IRQ',4)]},existing_workspace_source_components_found=False,legacy_archive_source_matches=0,upstream=REPO,upstream_commit=commit,upstream_boundary_entries=len(rows),manual_url='https://www.nesfiles.com/NES/Bubble_Bobble/Bubble_Bobble.pdf',original_credit='Taito; US original manual credits Taito America, Inc. copyright1988. Specific NES staff names have not been authenticated from this donor.',original_mechanics_manual='Bub usescontroller1, Bobcontroller2; A jump,B bubbles; trapped-enemy popping and held-A bubble riding are required mechanics, separate from ordinary projectile damage.',host_allocated=False,menu_admitted=False,native_emulator=False,installed=False))
 print(json.dumps(dict(passed=True,ROM_sha256=PIN,upstream_commit=commit,boundaries=len(rows),ROM_copied=False,host_allocation=False)))


def listing(bank,start,end):
 idx=json.loads((O/'instruction-index.json').read_text());m=image(bank);d=Disassembler(m)
 out=[]
 for b,pc,code in idx['rows']:
  if b!=bank or not start<=pc<end:continue
  n,text=d.instruction_at(pc);assert bytes(code)==bytes(m.memory[pc:pc+n])
  out.append(f'{bank:02X}:{pc:04X} '+bytes(code).hex(' ').upper().ljust(9)+' '+text)
 return '\n'.join(out)


if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');ap.add_argument('--list',nargs=3);a=ap.parse_args()
 if a.fetch:fetch()
 if a.list:print(listing(int(a.list[0],0),int(a.list[1],0),int(a.list[2],0)))
