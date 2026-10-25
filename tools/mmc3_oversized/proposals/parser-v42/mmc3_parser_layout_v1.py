from pathlib import Path
import argparse, hashlib, json, sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address,location
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);ap.add_argument('--baseline');ap.add_argument('--out',default='layout-v1');args=ap.parse_args()
 V=D/args.candidate;O=V/args.out;O.mkdir(exist_ok=False);p=Path(args.baseline)if args.baseline else D/'mmc3-static-call-v39/candidate.nes'
 old=load(p);new=load(V/'candidate.nes')
 def seg(b,n):return next(z for z in b['segs'].values()if z['name']=='"'+n+'"')
 ram=[]
 for n,s in old['syms'].items():
  g=old['segs'].get(s.get('seg'));v=int(s['val'],0)
  if s.get('type')=='lab'and g and g.get('type')=='rw'and g.get('name')!='"SMCCODE"'and v<0x8000:
   assert n in new['syms']and address(new,n)==v,(n,hex(v),new['syms'].get(n));ram.append(n)
 assert address(new,'SMCCODE')==0x155
 expected=dict(NextBank_SMC=0x13e,SafecallA_SMC=0x155,FarcallJmpTarget_SMC=0x157,SafereturnA_SMC=0x159)
 assert all(address(new,n)==v for n,v in expected.items())
 assert int(seg(new,'SMCCODE')['size'],0)==6
 exact=[]
 for n in ['VIC_NATIVE_AUDIO','M3_RAW_CHR']:
  a=seg(old,n);b=seg(new,n)
  assert all(a[k]==b[k]for k in ['start','size','ooffs'])
  pos,size=int(a['ooffs'],0),int(a['size'],0);assert old['raw'][pos:pos+size]==new['raw'][pos:pos+size];exact.append(dict(segment=n,bytes=size))
 assert all(old['raw'][16+k*8192:16+(k+1)*8192]==new['raw'][16+k*8192:16+(k+1)*8192]for k in range(0xe7,0xf7))
 assert (location(new,'FarCallCommon')-16)//8192==254
 assert (location(new,'M3ReadWarpCold')-16)//8192==253
 assert address(new,'FarCallCommon')==address(old,'BillNativeReadWarp')
 assert location(new,'M3ReadWarpCold')==int(seg(new,'VIC_NATIVE_AUDIO')['ooffs'],0)+int(seg(new,'VIC_NATIVE_AUDIO')['size'],0)
 assert old['raw'][location(old,'WarpZoneNumbers'):location(old,'WarpZoneNumbers')+256]==new['raw'][location(new,'M3WarpIndexedWindow'):location(new,'M3WarpIndexedWindow')+256]
 for f in ['src/zelda2_link_state.inc','chr/characters/oversized-raw.chr']:
  baseline_source=p.parent/'source'/f;assert baseline_source.read_bytes()==(V/'source'/f).read_bytes()
 q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),existing_RAM_labels_checked=len(ram),all_checked_RAM_addresses_exact=True,original_ZeldaII_alias_source_exact=True,exact_native_segments=exact,packed_music_banks_E7_F6_exact=True,all256_warp_indexed_bytes_exact=True,named_operand_aliases=expected,tiny_run=[0x155,0x15b],stack_guard_floor=0x5b,FarCallCommon=address(new,'FarCallCommon'),BillNativeReadWarp=address(new,'BillNativeReadWarp'),M3ReadWarpCold=address(new,'M3ReadWarpCold'),scope='Read-only complete linked RAM-label/SMC layout, raw CHR, packed music and exact5925-byte native Gradius segment comparisons. FD use begins strictly after native audio. No board RAM allocation, persistent Zelda overlap, source adoption, native timing or hardware claim.')
 (O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
if __name__=='__main__':main()
