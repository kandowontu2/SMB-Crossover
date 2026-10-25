"""Exact resident/mirror/sample and accepted Mac ownership bindings."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address,location
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=[load(a.prepared/(n+'.nes'))for n in('baseline','candidate')];ob,nb=old['raw'],new['raw']
 assert digest(ob)=='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
 def bank(raw,n):return raw[16+n*8192:16+(n+1)*8192]
 assert bank(ob,123)==bank(nb,123);assert ob[:16]==nb[:16]and ob[1048592:]==nb[1048592:]
 gate=location(old,'LmNativeMusicGate');assert gate==location(new,'LmNativeMusicGate')and ob[gate:gate+18]==nb[gate:gate+18]
 assert address(new,'Cv3DmcEndedGate')==0x9a10
 assert all(x==y or 0x1a10<=i<0x1a29 for i,(x,y)in enumerate(zip(bank(ob,126),bank(nb,126))))
 assert bank(nb,126)[0x1a29]==bank(ob,126)[0x1a29]==0xea
 ended=address(new,'DmcEnded')-0xe000;old127,new127=bank(ob,127),bank(nb,127)
 allowed=[(ended,ended+8),(0x1e15,0x1e40),(0x1ee1,0x1f00)]
 assert all(x==y or any(a<=i<b for a,b in allowed)for i,(x,y)in enumerate(zip(old127,new127)))
 samples={}
 for n in('BassWaterDpcm','AvDmcLinkTakeDamage','AvDmcSimonTakeDamage'):
  lo,hi=location(old,n),location(old,n+'End');assert lo==location(new,n)and hi==location(new,n+'End')and ob[lo:hi]==nb[lo:hi];samples[n]=dict(address=address(new,n),length=hi-lo,sha256=digest(nb[lo:hi]))
 mirror=bank(nb,125);manager_lo=address(new,'Cv3DmcManagerStart')-0xc000;manager_hi=address(new,'Cv3DmcManagerEnd')-0xc000;overlays=[(0x1140,0x1581),(0x15c0,0x1681),(manager_lo,manager_hi)]
 assert all(x==y or any(a<=i<b for a,b in overlays)for i,(x,y)in enumerate(zip(new127,mirror)))
 assert mirror[0x1ffa:]==new127[0x1ffa:]
 blank=[n for n in range(128)if bank(nb,n)==b'\xff'*8192]
 result=dict(passed=True,baseline_ROM_sha256=digest(ob),ROM_sha256=digest(nb),Mac_bank123_sha256=digest(bank(nb,123)),Mac_bank123_all8192_bytes_exact=True,Mac_gate18_bytes_exact=True,LOWCODE_only_changes_25_approved_tail_bytes=[0x9a10,0x9a29],final_tail_NOP_preserved=0x9a29,original127_only_changes_declared_hook_and_padding=allowed,original_samples_exact=samples,mirror_overlays=overlays,mirror_every_other_byte_including_code_vectors_exact=True,remaining_wholly_blank_banks=blank,future_shared_TMNT_cold_C=[0xd700,0xdaf7],new_RAM_allocation_bytes=0,scope='Exact linked ROM byte layout, no native hardware execution or waveform claim.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
