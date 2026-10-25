"""Freeze current ae97 and privately reuse the exact Grant/Alucard hurt sample."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 base=out/'baseline-source';base.mkdir()
 for n in('src','inc','chr','audio'):shutil.copytree(ROOT/n,base/n)
 shutil.copytree(ROOT/'build/generated',base/'build/generated')
 for q in[ROOT/'build_options.ini',*ROOT.glob('*.cfg')]:shutil.copyfile(q,base/q.name)
 frozen={str(q.relative_to(base)):sha(q)for q in base.rglob('*')if q.is_file()};(out/'frozen-inputs.json').write_text(json.dumps(frozen,indent=2)+'\n')
 def build(stage,name):
  with(out/(name+'.host.log')).open('w')as log:r=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))],cwd=stage,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(out/(name+'.host.log')).read_text()[-4000:]
 build(base,'baseline');assert sha(out/'baseline.nes')==sha(a.parent),'Root snapshot drift'
 stage=out/'source';shutil.copytree(base,stage)
 def change(name,before,after):
  f=stage/name;raw=f.read_bytes();s=raw.decode().replace('\r\n','\n');assert s.count(before)==1,(name,before);s=s.replace(before,after)
  original=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True,check=True).stdout
  eol='\r\n'if b'\r\n'in original else'\n';f.write_bytes(s.replace('\n',eol).encode())
 change('src/remaining_audio.s','''  lda #15                       ; Exact NTSC source rate, no IRQ or loop.
  sta $4010
''','''.if ::ENABLE_MMC5_EXPANDED
  jsr Cv3DmcInjuryRate
  .res 2,$ea                   ; old five-byte rate/store span
.else
  lda #15                       ; Exact NTSC source rate, no IRQ or loop.
  sta $4010
.endif
''')
 change('src/bass_source_sfx.s','''BassWaterDpcmEnd:
.segment "XG_BASS_GFX"
''','''BassWaterDpcmEnd:
.if ::ENABLE_MMC5_EXPANDED
; Four bytes of the existing47-byte alignment gap. All sample addresses,
; lengths and original payload bytes stay fixed.
Cv3DmcInjuryRates: .byte 15,14,15,13
.assert Cv3DmcInjuryRates=$fe11,lderror,"Pinned unused sample alignment gap"
.endif
.segment "XG_BASS_GFX"
''')
 change('src/cv3_pickups.s','''Recoil:sta Cv3VxHi
 lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
''','''Recoil:sta Cv3VxHi
 jsr Cv3DmcInjuryQueue
 .res 2,$ea ; same five-byte injury cue span
''')
 helper='''; Source-original Grant74/Alucard76 injury reuses exact existing Simon
;193-byte payload, with source rates14/13. Sypha remains unchanged pending
;its distinct payload. No primary72 sample/priority implementation is claimed.
.pushseg
.segment "CV3_GRIP"
.proc Cv3DmcInjuryQueue
 lda Cv3Variant
 cmp #2
 beq Generic
 lda #AV_SFX_SIMONTAKEDAMAGE
 sta AvAudioRequest
 lda #0
 sta Square1SoundQueue
 lda #Sfx_PipeDown_Injury
 rts
Generic:lda #Sfx_PipeDown_Injury
 sta Square1SoundQueue
 rts
.endproc
.segment "SOPHIA_LAND_AUDIO"
.proc Cv3DmcInjuryRate
 tya
 pha
 lda #15
 cpx #1 ; typed22 only; typed21 retains its exact original rate
 bne Store
 ldy SelectedCharacter
 cpy #CHARACTER_SIMON
 bne Store
 ldy Cv3Variant
 lda Cv3DmcInjuryRates,y
Store:sta $4010
 pla
 tay
 sec ; valid request21/22 preceding SEC/SBC always leaves carry set
 rts ; caller immediately executes its original LDA#0, restoring A/NZ
.endproc
.assert Cv3DmcInjuryRate=$bfe3,lderror,"Last bank7 padding begins here"
.assert *=$bfff,lderror,"Leave bank7's final byte free"
.popseg
'''
 (stage/'src/cv3_dmc_injury.s').write_bytes(helper.encode())
 name='src/entrypoint.s';f=stage/name;original=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True,check=True).stdout;eol=b'\r\n'if b'\r\n'in original else b'\n';raw=f.read_bytes();f.write_bytes(raw+eol+b'.if ::ENABLE_MMC5_EXPANDED'+eol+b'.include "cv3_dmc_injury.s"'+eol+b'.endif'+eol)
 build(stage,'candidate');old,new=load(out/'baseline.nes'),load(out/'candidate.nes')
 ol={q[2]:q[1]for line in(out/'baseline.lbl').read_text().splitlines()if len(q:=line.split())==3};nl={q[2]:q[1]for line in(out/'candidate.lbl').read_text().splitlines()if len(q:=line.split())==3};assert all(nl.get(n)==v for n,v in ol.items())
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][1048592:]==new['raw'][1048592:]
 samples={}
 for n in('BassWaterDpcm','AvDmcLinkTakeDamage','AvDmcSimonTakeDamage'):
  lo,hi=location(old,n),location(old,n+'End');assert location(new,n)==lo and location(new,n+'End')==hi and old['raw'][lo:hi]==new['raw'][lo:hi];samples[n]=dict(address=address(new,n),length=hi-lo,sha256=hashlib.sha256(new['raw'][lo:hi]).hexdigest())
 names=['src/entrypoint.s','src/remaining_audio.s','src/bass_source_sfx.s','src/cv3_pickups.s','src/cv3_dmc_injury.s'];patch=''
 for n in names:
  before=(base/n).read_text()if(base/n).exists()else'';after=(stage/n).read_text();patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+n if before else'/dev/null',tofile='b/'+n))
 (out/'implementation.patch').write_text(patch);diff=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
 result=dict(prepared=True,accepted=False,baseline_ROM_sha256=sha(out/'baseline.nes'),candidate_ROM_sha256=sha(out/'candidate.nes'),changed_bytes=len(diff),changed_banks=sorted({(i-16)//8192 for i in diff}),old_exported_PC_RAM_CHR_exact=True,new_RAM_bytes=0,sample_bytes_locations_lengths_exact=samples,rate_table_in_old_padding=[0xfe11,0xfe15],helper_in_old_bank7_tail=[0xbfe3,0xbfff],source_files={n:sha(stage/n)for n in names},original_EOLS_from_git_HEAD=True,scope='Private source/build only; original CPU/public ABI/owner and native qualification still required; missing attack72 and Sypha payload/priority not implemented.')
 (out/'prepare.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
