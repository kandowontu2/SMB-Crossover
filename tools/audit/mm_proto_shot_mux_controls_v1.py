"""Canonical/ordinary builds and exact declared same-bank Mega/Proto hook layout."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'root-chip-hud-composed-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);P=p.parse_args().packet;o=P/'controls-v1';o.mkdir(exist_ok=False)
 old,new=scoped_load(BASE/'candidate.nes'),scoped_load(P/'candidate.nes')
 assert sha(BASE/'candidate.nes')=='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
 assert sha(P/'candidate.nes')=='c5b65d96f6d76d4e9ebc62b5b28ae02e9cdea838414035fb1b2d4e0e4b706e48'
 oq,nq=qualified(BASE/'candidate.nes'),qualified(P/'candidate.nes');assert all(nq.get(n)==v for n,v in oq.items())
 hook=location(old,'ProtoLegacyDrawShotsCold')+21
 # Derive hook from its sole real original LDA age,x instruction, not a PC estimate.
 lo=location(old,'ProtoLegacyDrawShotsCold');hi=location(old,'ProtoShotLeftLo');operand=address(old,'MmBulletAge');literal=bytes([0xbd,operand&255,operand>>8]);hits=[i for i in range(lo,hi-2)if old['raw'][i:i+3]==literal];assert len(hits)==1;hook=hits[0]
 helper=address(new,'MmProtoShotMuxAdmission');assert helper==0xb9a8
 assert new['raw'][hook:hook+3]==bytes([32,helper&255,helper>>8])
 span=417;bankbase=16+66*8192;start=bankbase+0x19a8;assert old['raw'][start:start+span]==b'\xff'*span
 diffs=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
 assert len(diffs)==420 and all(hook<=i<hook+3 or start<=i<start+span for i in diffs)
 assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 manifest=json.loads((BASE/'source-manifest.json').read_text());changes=[n for n,h in manifest.items()if sha(P/'source'/n)!=h];assert set(changes)=={'src/protoman_legacy_shots.inc','smb1base-mmc5-expanded.cfg'}
 builds=[]
 for mode in ['canonical','mmc3','mmc5']:
  dest=o/(mode+'.nes');cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(P/'source'),'--output',str(dest)]
  if mode!='canonical':cmd+=['--flag-off',mode]
  r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(o/(mode+'.launch.json')).write_text(json.dumps(dict(command=cmd,exit=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n');assert r.returncode==0,r.stdout+r.stderr
  expected=sha(P/'candidate.nes')if mode=='canonical'else{'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}[mode];assert sha(dest)==expected
  builds.append(dict(mode=mode,sha256=sha(dest)))
 result=dict(passed=True,source_only=True,native_run=False,adopted=False,ROM_sha256=sha(P/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),old_qualified_symbols_retained=len(oq),new_RAM_bytes=0,changed_source=changes,
  hook=dict(file_offset=hook,bank=66,PC=0xa000+(hook-bankbase),before=old['raw'][hook:hook+3].hex(),after=new['raw'][hook:hook+3].hex()),helper=dict(bank=66,start=helper,end_exclusive=helper+span,bytes=span,previously_fill_FF=True,declared_segment='MM_PROTO_SHOT_MUX'),
  changed_PRG_bytes=420,all_other_PRG_CHR_exact=True,canonical_and_ordinary_builds=builds,checker_sha256=sha(__file__),limits='Source/CPU only. No native timing or visible improvement qualification; lone active shot CPU overhead remains open.')
 (o/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
