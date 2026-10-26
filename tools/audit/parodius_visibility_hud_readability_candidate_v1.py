"""Compile only the frozen v4 Parodius font/table overlay on exact current6c69."""
from pathlib import Path
import argparse,collections,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,location,address,Memory
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
BASE='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
FONT='d278c3e3f04aa95504099d6f4b6d4ffc932e745c2c8045b7227763b493fba2d0'
TABLE='17e11b188dfed3acea7b0c646d4f8ae9bbb7b4bfa0d2643310b65ba08b03cd0f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def inventory(p):return {str(f.relative_to(p)).replace('\\','/'):sha(f)for f in sorted(p.rglob('*'))if f.is_file()}
def execute(b,variant,meter,phase):
 m=Memory(b);m.page(1,77);m.page(2,116)
 tag=variant*2+1
 seed=dict(CurrentBank=77|128,CurrentBankC=116|128,VvVariant=variant,VvMeter=meter,InvHudActive=0 if phase=='first'else tag,
  X5HudChrUpper=0 if phase=='first'else 1,InvHudPhysical=0 if phase=='first'else 139+variant,PnInitialized=0x50,PnBombPaletteReady=1,
  VvHudDirty=0 if phase=='clean'else 1,VRAM_Buffer1_Offset=0,ReloadCHRBank=0)
 for name,value in seed.items():m[address(b,name)]=value
 m.writes=[];c=NesMPU(memory=m,pc=address(b,'PnHudQueue'));c.a=0x55;c.x=0x35;c.y=0x41;c.p=0x71;c.sp=0xfd;c.stPushWord(0x5aff)
 for _ in range(20000):
  if c.pc==0x5b00:break
  c.step()
 else:raise AssertionError(('queue timeout',phase,variant,meter,hex(c.pc)))
 return c,m
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['parent','proposal','source-ready','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--compiler',type=Path,default=ROOT/'tools/Windows/cc65/bin/cl65.exe');a=p.parse_args();assert not a.output.resolve().is_relative_to(ROOT)
 assert sha(a.parent/'candidate.nes')==BASE and sha(a.proposal/'proposal-parodius-hud.chr')==FONT and sha(a.proposal/'proposal-parodius_hud.inc')==TABLE
 ready=json.loads((a.source_ready/'proof.json').read_text());assert ready['ROM_sha256']==BASE and ready['source_only']and not ready['native_run']
 for f,h in json.loads((a.source_ready/'manifest.json').read_text()).items():assert sha(f)==h
 pin=json.loads((a.parent/'source-manifest.json').read_text())
 for f,h in pin.items():assert sha(a.parent/'source'/f)==h,('parent source changed',f)
 a.output.mkdir(parents=True,exist_ok=False);src=a.output/'source';shutil.copytree(a.parent/'source',src)
 before=inventory(src);put(a.output/'source-before-manifest.json',before)
 commands=[]
 def build(name):
  command=[sys.executable,'-B',str(src/'tools/build_mmc5_expanded.py'),'--workspace',str(src),'--compiler',str(a.compiler),'--output',str(a.output/(name+'.nes'))]
  commands.append(command)
  with(a.output/(name+'.host.log')).open('w')as log:r=subprocess.run(command,cwd=src,stdout=log,stderr=subprocess.STDOUT)
  assert r.returncode==0,(a.output/(name+'.host.log')).read_text()[-5000:]
 build('baseline');assert sha(a.output/'baseline.nes')==BASE,'Fresh frozen source must reproduce current6c69 before overlay'
 changed=['chr/characters/parodius-hud.chr','src/parodius_hud.inc']
 for rel,name in zip(changed,['proposal-parodius-hud.chr','proposal-parodius_hud.inc']):shutil.copyfile(a.proposal/name,src/rel)
 build('candidate');after=inventory(src);assert before.keys()==after.keys()
 delta=[f for f in before if before[f]!=after[f]];assert sorted(delta)==sorted(changed),delta
 put(a.output/'source-manifest.json',after)
 overlay=a.output/'overlay';(overlay/'chr/characters').mkdir(parents=True);(overlay/'src').mkdir()
 for f in changed:shutil.copyfile(src/f,overlay/f)
 patch=''.join(difflib.unified_diff((a.parent/'source/src/parodius_hud.inc').read_text().splitlines(keepends=True),(src/'src/parodius_hud.inc').read_text().splitlines(keepends=True),fromfile='a/src/parodius_hud.inc',tofile='b/src/parodius_hud.inc'))
 (a.output/'sourcepatch.patch').write_text(patch,encoding='utf-8')
 b=load(a.output/'baseline.nes');n=load(a.output/'candidate.nes');old=b['raw'];new=n['raw'];assert len(old)==len(new)
 assert qualified(a.output/'baseline.nes')==qualified(a.output/'candidate.nes')
 assert (a.output/'baseline.lbl').read_bytes()==(a.output/'candidate.lbl').read_bytes()
 table=location(b,'PnHudCells');assert location(n,'PnHudCells')==table
 # The symbol is the84-byte data array after GraphicalOffsets, not instructions.
 import re
 parse=lambda f:bytes(int(z,16)for z in re.findall(r'\$([0-9a-fA-F]{2})',Path(f).read_text()))
 assert old[table:table+84]==parse(a.parent/'source/src/parodius_hud.inc') and new[table:table+84]==parse(src/'src/parodius_hud.inc')
 gs=[z for z in b['segs'].values()if z['name']=='"PN_HUD_CHR"'];assert len(gs)==1
 font=int(gs[0]['ooffs'],0);assert int(gs[0]['size'],0)==3072 and old[font:font+3072]==(a.parent/'source/chr/characters/parodius-hud.chr').read_bytes()
 assert new[font:font+3072]==(src/'chr/characters/parodius-hud.chr').read_bytes()
 diffs=[i for i,(x,y)in enumerate(zip(old,new))if x!=y];assert all(table<=i<table+84 or font<=i<font+3072 for i in diffs)
 header=old[:16]==new[:16];assert header
 keep=set(range(10))|{ord(c)-ord('A')+10 for c in set('OCTOPUSTWINBEEPENTAROUWORLDTIMESCOREHP')}|{0x24,0x28,0x29,0x2e};assert len(keep)==31
 for v in range(3):
  for t in keep:
   start=font+v*1024+t*16;assert old[start:start+16]==new[start:start+16]
 queue=address(b,'VRAM_Buffer1');cases=[]
 for variant in range(1,4):
  for meter in range(128):
   for phase in ['first','attributes','clean']:
    oc,om=execute(b,variant,meter,phase);nc,nm=execute(n,variant,meter,phase)
    assert (oc.a,oc.x,oc.y,oc.p,oc.sp,oc.processorCycles)==(nc.a,nc.x,nc.y,nc.p,nc.sp,nc.processorCycles),(variant,meter,phase)
    excluded=set(range(queue+3,queue+31))if phase=='first'else set()
    assert all(om[i]==nm[i]for i in range(0x8000)if i not in excluded),(variant,meter,phase,'RAM')
    assert [i for i,v in om.writes]==[i for i,v in nm.writes]
    assert [(i,v)for i,v in om.writes if i not in excluded]==[(i,v)for i,v in nm.writes if i not in excluded]
    assert om.banks==nm.banks
    cases.append(dict(variant=variant,meter=meter,phase=phase,cycles=nc.processorCycles,registers_SP_flags_mapper_exact=True,all_RAM_and_ordered_writes_exact_except_intended28cell_data=True))
 put(a.output/'queue-cases.json',cases)
 q=dict(passed=True,source_only=True,native_run=False,production_changes=False,adopted=False,parent_ROM_sha256=BASE,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
  fresh_baseline_compile_exact=True,commands=commands,source_files=len(before),parent_pinned_source_files=len(pin),source_changes=delta,
  source_overlay={f:dict(before_sha256=before[f],after_sha256=after[f])for f in changed},all_other_source_bytes_exact=True,
  all_qualified_addresses_RAM_exact=len(qualified(a.output/'baseline.nes')),label_file_byte_exact=True,header_exact=header,
  intended_data_ranges=dict(table=dict(offset=table,length=84,bank=(table-16)//8192,CPU_address=address(b,'PnHudCells')),font=dict(offset=font,length=3072,physical_pages=[396,397,398])),
  different_ROM_bytes=len(diffs),different_table_bytes=sum(table<=i<table+84 for i in diffs),different_CHR_bytes=sum(font<=i<font+3072 for i in diffs),
  every_other_ROM_byte_exact=True,all_runtime_instruction_bytes_exact=True,all_audio_ROM_and_source_bytes_exact=True,standard_glyph_tiles_exact=31*3,
  same_all21_source_word_masks_from_frozen_proposal=True,layout_and_first42_dirty11byte_lengths_exact=True,
  actual_linked_queue_CPU_cases=len(cases),all128meters_threevariants_threepaths=True,full_register_flags_SP_RAM_orderedwrites_mapper_and_cycles_exact_except_intended_cells=True,added_CPU_cycles=0,
  compiler_sha256=sha(a.compiler),build_tool_sha256=sha(src/'tools/build_mmc5_expanded.py'),source_ready_sha256=sha(a.source_ready/'proof.json'),
  source_manifest_sha256=sha(a.output/'source-manifest.json'),queue_cases_sha256=sha(a.output/'queue-cases.json'),tool_sha256=sha(Path(__file__)),
  limits='Private canonical source builds and exact data confinement/1152actualCPU queue cases only. No native run, user readability validation, palette/color/transition/physical acquisition/fullcampaign/roster/audio performance/adoption verdict. Existing font remains tiny; original areaFALSE/naturalBuffer2overlap and bodyvisibility findings unchanged.')
 put(a.output/'proof.json',q);print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))
if __name__=='__main__':main()
