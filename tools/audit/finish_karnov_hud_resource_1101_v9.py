"""Finish compact witnesses from published1c and frozen/private inputs only."""
from pathlib import Path
import hashlib,io,itertools,json,re,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import audit_karnov_hud_resource_1101_v9 as A
from py65.devices.mpu6502 import MPU
from verify_native_relocation import NesMPU
O=A.O
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda n,q:(O/n).write_text(json.dumps(q,indent=2)+'\n')

def main():
 # No live O source, ROM, debug or object is read after releasing the lease.
 rom=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes();assert sha(rom)==A.PIN
 images={Path('kernel'):rom[1048592+399*1024:1048592+407*1024],Path('combat'):rom[1048592+1019*1024:1048592+1019*1024+1280],Path('options'):rom[1048592+1021*1024:1048592+1023*1024]}
 b=dict(segs={str(i):dict(name='"'+name+'"',start=str(start),ooffs='0',oname='"'+image+'"')for i,(name,start,image)in enumerate([('KR_KERNEL',0xa000,'kernel'),('KR_COMBAT_ROM',0xc900,'combat'),('KR_OPTIONS_ROM',0xd600,'options')])})
 q=json.loads((O/'resource-grant.json').read_text());q['cache']=A.cache_census(b,'',images,{})
 census=json.loads((O/'cache-compiled-consumers.json').read_text());indirect=census['indirect_sites']
 assert len(indirect)==8,indirect
 domains={
  0xa07a:('Inline dispatch','Nine JSR return bases in A09E..AE37 or D646..DA59; 8-bit index cannot reach C87A..C87F.'),
  0xa07e:('Inline dispatch','Same bounded code-table read as A07A.'),
  0xb06c:('New life state zero','R0/R1 start C000; LDY0/LDX8, exactly C000..C7FF.'),
  0xb3e5:('Terrain probe','R7 is native Block_Buffer_1 high byte; column offset0..31 and row offset0..C0. Native low-RAM block buffer, outside conditional C2.'),
  0xb485:('Metadata source','KrArtImage..KrArtEnd is resident A3 source metadata; exact1345B.'),
  0xb487:('Metadata destination','R0/R1 start D000, exact1345B counter; writes D000..D540.'),
  0xcb2d:('Projectile terrain probe','Native GetBlockBufferAddr output saved into KC_PTR; low-RAM block buffer with valid row0..C0.'),
  0xcb6e:('Projectile terrain mask','KC_PTR translated by MmSolidTerrain-Block_Buffer_1; SRAM terrain flags, outside C2.'),
 }
 assert {s['PC']for s in indirect}==set(domains)
 for row in indirect:row['closed_owner'],row['closed_domain']=domains[row['PC']]
 listing=(O/'kernel.lst').read_text().splitlines();calls=[]
 for line in listing:
  if re.search(r'JSR KrDispatch\b',line):
   offset=int(line[:6],16);calls.append(offset)
 assert len(calls)==9 and all(x<0x1000 for x in calls)
 census['indirect_domains_closed']=True;census['dispatch_JSR_offsets']=calls;census['source_instruction_scope']='Exact reproduced kernel object includes original actor, weapons, clear, terrain/render/health/pickup, combat and options. Eight indirect memory sites classified; cold ROM wholeC2 clear is separate prior-to-cookie owner.'
 save('cache-compiled-consumers.json',census)
 # Independently execute both map leaves for every flag byte and all12 rows.
 # Pure leaf fixture uses a declared test R2 atZP5. No host executable overlay.
 old=bytes.fromhex('a605 a903 e008 b001 4a 8d3051 bd13c0 8d2b51 60')+bytes([143,144,145,146,147,148,149,150,251,252,253,254])
 new=bytes.fromhex('a605 a901 e008 9002 a903 8d3051 8a 9002 6963 698f 8d2b51 60')
 assert len(old)==31 and len(new)==24
 differences=set();cases=0
 for row,flags in itertools.product(range(12),range(256)):
  results=[]
  for code in[old,new]:
   mem=[0]*65536;mem[0xc000:0xc000+len(code)]=code;mem[5]=row
   cpu=NesMPU(memory=mem,pc=0xc000);cpu.a=85;cpu.x=7;cpu.y=91;cpu.p=flags;cpu.sp=224;cpu.stPushWord(0x5aff)
   for _ in range(24):
    if cpu.pc==0x5b00:break
    cpu.step()
   assert cpu.pc==0x5b00 and cpu.sp==224
   results.append((cpu.a,cpu.x,cpu.y,cpu.p&~16,mem[0x5130],mem[0x512b]))
  x,y=results;assert x[:3]==y[:3]and x[4:]==y[4:]
  differences.add(x[3]^y[3]);assert(x[3]^y[3])&~0x41==0;cases+=1
 # In actual caller, BIT2002 immediately replaces V; C is dead through
 # copy/verify until SEC before SBC or the row-count CMP. All caller flags
 # remain saved by KrLoad and are restored on exit.
 parent=R/'build/karnov-hud-funding-1101-v9/funding-controls.json';funding=json.loads(parent.read_text());assert funding['passed']and funding['parent_ROM_sha256']==A.PIN
 transform=R/'tools/audit/prepare_karnov_hud_funding_1101_v9.py'
 source=transform.read_text();assert 'cold_map_pairs_shared=7'in source
 q['funding'].update(actual_CurrentBankC=0x7da1,old_map_pair_bytes=6,shared_helper_bytes=7,seven_pairs_net_saved=14,carrier_map_and_table_old_bytes=31,carrier_map_new_bytes=24,carrier_map_saved=7,total_saved=21,cancellation_added=17,prefill_added=4,water_address_preserved='BB8E',leaf_differential_cases=cases,permitted_dead_flag_difference_masks=sorted(differences),dead_V='BIT $2002 immediately after JSR KrCarrierMap, before any V consumer.',dead_C='No carry consumer before SEC/SBC or row-count CMP in actual copy/verify owner.',actual_source_component_pass=True,source_component_receipt_sha256=sha(parent.read_bytes()),source_transform_sha256=sha(transform.read_bytes()),remaining_gate='Actual owning cold Main IRQ/NMI cuts must include new helper JSR entry/mirror-store/hardware-store/RTS stack seams. Extra2B stack depth is not qualified by this leaf test.')
 q['cache']['indirect_domains_closed']=True;q['cache']['indirect_sites']=8
 q['funding_source_model_closed']=True
 q['no_live_O_reads_after_release']=True
 save('resource-grant.json',q)
 # Keep compact indexed witnesses; the full listing/object are disposable.
 members={}
 for name in['pinned.json','kernel-assembly.json','compiled-font-witness.json','cache-compiled-consumers.json','resource-grant.json']:
  members['proof/'+name]=(O/name).read_bytes()
 for path in[Path(A.__file__),Path(__file__)]:members[path.relative_to(R).as_posix()]=path.read_bytes()
 packet=O/'source-and-proof.zip'
 with zipfile.ZipFile(packet,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name,data in sorted(members.items()):
   info=zipfile.ZipInfo(name,(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
 with zipfile.ZipFile(packet)as z:assert z.testzip()is None
 removed=[]
 for name in['kernel.o','kernel.lst']:
  p=O/name;assert p.resolve().parent==O.resolve();removed.append(dict(path=name,bytes=p.stat().st_size,sha256=sha(p.read_bytes())));p.unlink()
 receipt=dict(passed=True,frozen=True,packet=dict(path=packet.relative_to(R).as_posix(),bytes=packet.stat().st_size,sha256=sha(packet.read_bytes()),members=len(members)),grant_sha256=sha((O/'resource-grant.json').read_bytes()),removed_generated=removed,no_full_ROM_debug_copied=True,remaining_gate='Root owning lifecycle/actual-Main/native qualification; old-owner resources and cache granted only under declared conditions.')
 save('freeze.json',receipt);print(json.dumps(receipt))

if __name__=='__main__':main()
