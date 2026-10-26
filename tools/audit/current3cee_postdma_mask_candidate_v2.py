"""One literal immediate-post-DMA mask relocation; private source builds only."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
ROOT = Path(__file__).resolve().parents[2]
BASE = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, z): Path(p).write_text(json.dumps(z, indent=2)+'\n', encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 assert sha(a.parent/'candidate.nes')==BASE and not a.output.resolve().is_relative_to(ROOT)
 pin=json.loads((a.parent/'source-manifest.json').read_text(encoding='utf-8'));assert all(sha(a.parent/'source'/f)==h for f,h in pin.items())
 a.output.mkdir(parents=True,exist_ok=False);src=a.output/'source';shutil.copytree(a.parent/'source',src)
 before={str(f.relative_to(src)).replace('\\','/'):sha(f)for f in src.rglob('*')if f.is_file()};commands=[]
 def build(stem,flag=None):
  cmd=[sys.executable,'-B',str(src/'tools/build_mmc5_expanded.py'),'--workspace',str(src),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/(stem+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  commands.append(cmd)
  with(a.output/(stem+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=src,stdout=log,stderr=subprocess.STDOUT)
  assert r.returncode==0,(a.output/(stem+'.host.log')).read_text(encoding='utf-8')[-5000:]
  return sha(a.output/(stem+'.nes'))
 assert build('baseline')==BASE
 ordinary={m:build('ordinary-before-'+m,m)for m in ['mmc3','mmc5']}
 reset=src/'src/reset.s';s=reset.read_text(encoding='utf-8')
 pair='  lda Mirror_PPUMASK       ;copy mirror of $2001 to register\n  sta PPUMASK\n'
 assert s.count(pair)==1
 s=s.replace(pair,'.if !(::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5)\n'+pair+'.endif\n')
 insert=''' .if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
  ; Keep rendering disabled until all256 DMA writes finish. The next input
  ; load kills A/NZ; the pair preserves C/V and the controller GET/PUT parity.
::PostDmaMaskEnable:
  lda Mirror_PPUMASK
  sta PPUMASK
 .endif
'''
 normal='  sta OAM_DMA          ; ------ OAM DMA ------\n'
 mouse='  STA OAM_DMA\n'
 assert s.count(normal)==s.count(mouse)==1
 s=s.replace(normal,normal+insert).replace(mouse,mouse+insert)
 reset.write_text(s,encoding='utf-8')
 cfg=src/'smb1base-mmc5-expanded.cfg';s=cfg.read_text(encoding='utf-8')
 assert s.count('ALIGN:  start = $e000,  size = $60,')==1 and s.count('PRGFix: start = $e060,  size = $2000 - $60,')==1
 s=s.replace('ALIGN:  start = $e000,  size = $60,','ALIGN:  start = $e000,  size = $66,').replace('PRGFix: start = $e060,  size = $2000 - $60,','PRGFix: start = $e066,  size = $2000 - $66,')
 cfg.write_text(s,encoding='utf-8');candidate=build('candidate')
 old,new=[scoped_load(a.output/(n+'.nes'))for n in ['baseline','candidate']]
 assert old['raw'][:16]==new['raw'][:16] and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 moved=[]
 for name,sym in old['syms'].items():
  assert name in new['syms'],name
  x,y=int(sym['val'],0),int(new['syms'][name]['val'],0)
  if x!=y:moved.append(dict(symbol=name,before=x,after=y,delta=y-x))
 assert all(r['delta']==6 for r in moved),moved[:15]
 assert address(new,'OAMandReadJoypad')==0xe000 and address(new,'PostDmaMaskEnable')==0xe005
 assert address(new,'NonMaskableInterrupt')==address(old,'NonMaskableInterrupt')+6
 assert address(new,'NonMaskableInterrupt::InitBuffer')==address(old,'NonMaskableInterrupt::InitBuffer')
 at=location(new,'OAMandReadJoypad');assert new['raw'][at:at+13]==bytes.fromhex('a9028d1440ad7a078d0120a201')
 # Protect entire DPCM/crouch payloads; named symbol movement is genuine.
 protected=[]
 for name in ['BASS_DPCM','SAMUS_CROUCH_BODY','SAMUS_CROUCH_WATER','SAMUS_FREEZE_STORE']:
  os=next(z for z in old['segs'].values()if z['name']=='"'+name+'"');ns=next(z for z in new['segs'].values()if z['name']=='"'+name+'"')
  x,y,size=int(os['ooffs'],0),int(ns['ooffs'],0),int(os['size'],0)
  assert x==y and size==int(ns['size'],0) and old['raw'][x:x+size]==new['raw'][y:y+size],name
  protected.append(dict(segment=name,offset=x,size=size))
 diff=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y];banks={}
 for i in diff:banks[(i-16)//8192]=banks.get((i-16)//8192,0)+1
 after={str(f.relative_to(src)).replace('\\','/'):sha(f)for f in src.rglob('*')if f.is_file()}
 changed=sorted(f for f in before if before[f]!=after[f]);assert before.keys()==after.keys() and changed==['smb1base-mmc5-expanded.cfg','src/reset.s']
 overlay=a.output/'overlay';patch=''
 for rel in changed:
  target=overlay/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/rel,target)
  patch+=''.join(difflib.unified_diff((a.parent/'source'/rel).read_text(encoding='utf-8').splitlines(keepends=True),(src/rel).read_text(encoding='utf-8').splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
 (a.output/'sourcepatch.patch').write_text(patch,encoding='utf-8')
 for m in ['mmc3','mmc5']:assert build('ordinary-after-'+m,m)==ordinary[m]
 put(a.output/'source-manifest.json',after);put(a.output/'moved-symbols.json',moved)
 put(a.output/'layout.json',dict(differing_ROM_bytes=len(diff),different_banks=banks,moved_symbols=len(moved),all_moves_genuine_plus6=True,protected_payloads=protected,header_CHR_exact=True))
 put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,adopted=False,baseline_ROM_sha256=BASE,candidate_ROM_sha256=candidate,fresh_baseline_exact=True,source_changes=changed,ordinary_flagoff_exact=ordinary,different_ROM_bytes=len(diff),different_banks=banks,genuine_old_symbol_moves=len(moved),all_moves_plus6=True,PostDmaMaskEnable=0xe005,input_after_enable_LDX=0xe00b,post_LDX_actual_hook=0xe00d,CHR_DPCM_crouch_payloads_exact=True,commands=commands,layout_sha256=sha(a.output/'layout.json'),moved_symbols_sha256=sha(a.output/'moved-symbols.json'),source_manifest_sha256=sha(a.output/'source-manifest.json'),tool_sha256=sha(__file__),limits='Build/layout only. Complete NMI/input/interrupt and branch-page costs require separate actual assembled controls. No native launch, universal late-NMI or adoption claim.'))
 print(json.dumps(dict(passed=True,candidate_ROM_sha256=candidate,different_banks=banks,moved_symbols=len(moved),proof_sha256=sha(a.output/'proof.json')),indent=2))
if __name__=='__main__':main()
