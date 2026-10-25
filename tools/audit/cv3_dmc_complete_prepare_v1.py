"""Freeze529 and prepare a private MMC5 source-original CV3 DMC mirror lane."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys, difflib
from check_tmnt_render_oa import load,location
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE='52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
FULL='''; MMC5 expanded only. Original CV3 request priority occupies four previously
; unused bytes after the existing CV1 private image and noise lane.
Cv3DmcPriority=RgAudioZp+32
Cv3DmcPending=RgAudioZp+33
Cv3DmcSavedC=RgAudioZp+34
Cv3DmcEntryA=RgAudioZp+35
.pushseg
.segment "CV3_COMBAT"
.proc Cv3DmcPrimaryQueue
 php
 lda Cv3AttackKind
 cmp #1
 bne Done
 lda Cv3Variant
 cmp #3
 bcs Done
 lda Cv3DmcPending
 cmp #$74
 bcs Done
 lda #$72
 sta Cv3DmcPending
Done:plp
 lda #4
 sta RgSfx
 rts
.endproc
.segment "CV3_GRIP"
.proc Cv3DmcFullInjuryQueue
 php
 lda Cv3Variant
 clc
 adc #$73
 sta Cv3DmcPending
 lda #0
 sta Square1SoundQueue
 plp
 lda Cv3Variant
 cmp #2
 lda #Sfx_PipeDown_Injury
 rts
.endproc
.proc Cv3DmcSceneRequest
 php
 lda #0
 sta Cv3DmcPending
 lda BassDmcActive
 cmp #3
 beq Owned
 lda #0
 sta Cv3DmcPriority
 jmp Done
Owned:lda #0
 jsr Cv3DmcOwnerWrite
Done:
 plp
 lda AvAudioRequest
 rts
.endproc
.segment "CV_WRAP"
.proc Cv3DmcBeforeCv1
 ; CvAudioPlay begins with authenticated LDA $e2, overwriting A/N/Z.
 ; Idle only uses LDA/ORA/branch/JMP, preserving every other input flag.
 lda Cv3DmcPending
 ora Cv3DmcPriority
 bne Work
 jmp CvAudioPlay
Work:php
 lda MmDeathFlag
 bne Cancel
 lda GameEngineSubroutine
 cmp #$0b
 beq Cancel
 lda Cv3DmcPending
 beq Play
 jsr Cv3DmcStartGate
 jmp Play
Cancel:lda #0
 sta Cv3DmcPending
 lda BassDmcActive
 cmp #3
 bne Unowned
 lda #0
 jsr Cv3DmcOwnerWrite
 jmp Play
Unowned:lda #0
 sta Cv3DmcPriority
Play:plp
 jmp CvAudioPlay
.endproc
.segment "X5_AUDIO_MIX"
.proc Cv3DmcResetOwner
 php
 sta Cv3DmcPending ; original two call sites both supply A=0
 lda BassDmcActive
 cmp #3
 beq Owned
 lda #0
 sta Cv3DmcPriority
Owned:lda #0
 jsr Cv3DmcOwnerWrite
 plp
 rts
.endproc
.segment "CV3_DMC_MANAGER"
Cv3DmcManagerStart:
.proc Cv3DmcStart
 php
 pha
 txa
 pha
 tya
 pha
 lda #0
 sta Cv3DmcPending
 lda Cv3DmcEntryA
 cmp #$72
 beq Valid
 cmp #$74
 bcc Done
 cmp #$77
 bcs Done
Valid:lda Cv3DmcPriority
 beq Incoming
 lda $4015
 and #$10
 bne Incoming
 lda #0
 jsr Cv3DmcOwnerWrite ; exact original completion resets source priority
Incoming:lda Cv3DmcEntryA
 sec
 sbc #$6d
 tax
 lda Cv3DmcPriority
 cmp #5
 bcc Start
 txa
 cmp Cv3DmcPriority
 bcc Done
Start:lda GuestCombinedEnable
 and #15
 sta $4015
 lda #0
 sta $4011
 stx Cv3DmcPriority
 lda Cv3DmcEntryA
 sec
 sbc #$72
 tay
 lda Rates,y
 sta $4010
 lda Addresses,y
 sta $4012
 lda Lengths,y
 sta $4013
 lda #$fd
 sta $5117 ; E mirror: identical resident code/vectors, source-only samples
 lda #3
 sta BassDmcActive
 lda GuestCombinedEnable
 ora #$10
 sta GuestCombinedEnable
 sta $4015
Done:pla
 tay
 pla
 tax
 pla
 plp
 rts
Rates:.byte 15,15,14,15,13
Addresses:.byte ($f140-$c000)/64,0,($ff00-$c000)/64,($f5c0-$c000)/64,($ff00-$c000)/64
Lengths:.byte $44,0,$0c,$0c,$0c
.endproc
Cv3DmcManagerEnd:
.assert Cv3DmcManagerStart=$daf7,lderror,"Share bank125 after future TMNT cold adapter"
.assert Cv3DmcManagerEnd<=$de11,lderror,"Do not overwrite copied resident helpers or samples"
.popseg
'''
GATE='''; Executes identically in E127 and its E125 mirror. No shared SMC farcall.
.proc Cv3DmcStartGate
 sta Cv3DmcEntryA
 lda CurrentBankC
 sta Cv3DmcSavedC
 lda #$fd
 sta CurrentBankC
 sta $5116
 lda Cv3DmcEntryA
 jsr Cv3DmcStart
 pha
 php
 lda Cv3DmcSavedC
 sta CurrentBankC
 sta $5116
 plp
 pla
 rts
.endproc
.assert Cv3DmcStartGate=$fe15,lderror,"Existing Bass sample alignment gap"
.assert *<=$fe40,lderror,"Preserve original Link sample start"
'''
OWNER='''; Ordinary ownership stores retain A/X/Y/P. Only an active CV3 source
; lane adds stop/restore writes; all existing samples stay in original E127.
.proc Cv3DmcOwnerWrite
 sta BassDmcActive
 php
 pha
 lda Cv3DmcPriority
 beq Done
 lda GuestCombinedEnable
 and #15
 sta $4015
 lda #$ff
 sta $5117
 lda #0
 sta Cv3DmcPriority
Done:pla
 plp
 rts
.endproc
.assert Cv3DmcOwnerWrite=$fee1,lderror,"Existing Link sample alignment gap"
.assert *=$ff00,lderror,"Preserve original Simon sample start"
'''
COMPLETION='''; Original CV3 clears request priority after DMA fetch completion without
; clearing4011: the last buffered byte must drain and its actual DAC is held.
.proc Cv3DmcEndedGate
 php
 lda BassDmcActive
 cmp #3
 beq SourceCompletion
 lda #0
 jsr Cv3DmcOwnerWrite
 sta $4011 ; exact existing ordinary completion behavior
 plp
 rts
SourceCompletion:lda #0
 jsr Cv3DmcOwnerWrite
 plp
 rts
.endproc
.assert Cv3DmcEndedGate=$9a10,lderror,"After the exact18-byte Mac gate"
.assert *=$9a29,lderror,"Leave the final original tail byte unused"
'''
PRODUCER='''"""Build the deterministic MMC5 CV3 fixed-E clone after every final link."""
from pathlib import Path
import hashlib,json,re
PAYLOADS={"primary72.dmc":(0x1140,1089,"c1b646c36508ad4d134078c8184fea7bd632f50127c5f2af6550e89097cbda01"),"sypha75.dmc":(0x15c0,193,"137fc604fe0c0cbf8c28733411e2397cc00e72188db755a00eb8ad27da037331")}
def prepare(root,out):
 raw=bytearray(out.read_bytes());assert len(raw)==2097168
 labels={v[2].lstrip('.'):int(v[1],16)for l in out.with_suffix('.lbl').read_text().splitlines()if len(v:=l.split())==3}
 for line in out.with_suffix('.dbg').read_text().splitlines():
  if line.startswith('sym\\t'):
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
 out.with_suffix('.cv3-mirror.json').write_text(json.dumps(receipt,indent=2)+'\\n')
 return receipt
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--frozen-root',type=Path);p.add_argument('--baseline-sha',default=BASE);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);source=(a.frozen_root or ROOT).resolve()
 base=out/'baseline-source';base.mkdir()
 for n in('src','inc','chr','audio'):shutil.copytree(source/n,base/n)
 shutil.copytree(source/'build/generated',base/'build/generated');(base/'tools').mkdir()
 shutil.copyfile(source/'tools/build_mmc5_expanded.py'if(source/'tools/build_mmc5_expanded.py').exists()else ROOT/'tools/build_mmc5_expanded.py',base/'tools/build_mmc5_expanded.py')
 for q in[source/'build_options.ini',*source.glob('*.cfg')]:shutil.copyfile(q,base/q.name)
 def build(stage,name):
  with(out/(name+'.host.log')).open('w')as log:r=subprocess.run([sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/(name+'.nes'))],cwd=stage,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(out/(name+'.host.log')).read_text()[-7000:]
 build(base,'baseline');assert sha(out/'baseline.nes')==a.baseline_sha,'Root snapshot drift'
 stage=out/'source';shutil.copytree(base,stage)
 def change(name,before,after,count=1):
  f=stage/name;raw=f.read_bytes();s=raw.decode().replace('\r\n','\n');assert s.count(before)==count,(name,before,s.count(before));s=s.replace(before,after)
  original=subprocess.run(['git','show','HEAD:'+name],cwd=ROOT,capture_output=True,check=True).stdout;eol='\r\n'if b'\r\n'in original else'\n';f.write_bytes(s.replace('\n',eol).encode())
 def append(name,extra):
  f=stage/name;raw=f.read_bytes();eol=b'\r\n'if b'\r\n'in raw else b'\n';f.write_bytes(raw+eol+extra.replace('\n',eol.decode()).encode())
 (stage/'audio/cv3').mkdir(exist_ok=True)
 shutil.copyfile(D/'cv3-primary-sfx-v1/source-cpu-v2/cv3-event72.dmc',stage/'audio/cv3/primary72.dmc')
 shutil.copyfile(D/'cv3-dmc-followup-v1/capacity-source-v1/sypha-injury.dmc',stage/'audio/cv3/sypha75.dmc')
 for name,text in [('src/cv3_dmc_complete.s',FULL),('src/cv3_dmc_gate.inc',GATE),('src/cv3_dmc_owner.inc',OWNER),('src/cv3_dmc_completion.inc',COMPLETION),('tools/prepare_cv3_dmc_mirror.py',PRODUCER)]: (stage/name).write_bytes(text.encode())
 change('src/bass_source_sfx.s','.assert Cv3DmcInjuryRates=$fe11,lderror,"Pinned unused sample alignment gap"','.assert Cv3DmcInjuryRates=$fe11,lderror,"Pinned unused sample alignment gap"\n.if ::MAPPER_MMC5\n.include "cv3_dmc_gate.inc"\n.endif')
 change('audio/remaining-source-sfx.inc','AvDmcLinkTakeDamageEnd:\n','AvDmcLinkTakeDamageEnd:\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n .include "cv3_dmc_owner.inc"\n.endif\n')
 # Durable sample producer: keep the alignment-gap include after regeneration.
 (stage/'tools/reference').mkdir()
 shutil.copyfile(ROOT/'tools/reference/build_remaining_sfx.py',stage/'tools/reference/build_remaining_sfx.py')
 change('tools/reference/build_remaining_sfx.py',"  lines +=['.align $40',f'AvDmc{name}:',' .byte '+','.join(str(v)for v in bytes.fromhex(sample['hex'])),f'AvDmc{name}End:']", "  lines +=['.align $40',f'AvDmc{name}:',' .byte '+','.join(str(v)for v in bytes.fromhex(sample['hex'])),f'AvDmc{name}End:']\n  if name=='LinkTakeDamage': lines +=['.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',' .include \"cv3_dmc_owner.inc\"','.endif']")
 change('tools/reference/build_remaining_sfx.py',"(ROOT/'audio/remaining-source-sfx.inc').write_text('\\n'.join(lines)+'\\n')","(ROOT/'audio/remaining-source-sfx.inc').write_bytes(('\\n'.join(lines)+'\\n').encode())")
 change('src/cv3_dmc_injury.s',' lda Cv3Variant\n cmp #2\n beq Generic','.if ::MAPPER_MMC5\n jmp Cv3DmcFullInjuryQueue\n .res 4,$ea ; exact original seven-byte entry span\n.else\n lda Cv3Variant\n cmp #2\n beq Generic\n.endif')
 change('src/cv3_dmc_injury.s','; Source-original Grant74/Alucard76 injury reuses exact existing Simon\n;193-byte payload, with source rates14/13. Sypha remains unchanged pending\n;its distinct payload. No primary72 sample/priority implementation is claimed.','; Original Grant74/Alucard76 injury sample/rate binding. Expanded MMC5\n;dispatches through the complete source DMC lane; other targets retain the\n;previous shared193-byte payload route without an E-window mirror.')
 change('src/cv3_combat.s','Sound:\n lda #4\n sta RgSfx','Sound:\n.if ::MAPPER_MMC5\n jsr Cv3DmcPrimaryQueue\n .res 2,$ea\n.else\n lda #4\n sta RgSfx\n.endif')
 change('src/cv3_source_audio.s',' php\n lda AvAudioRequest\n cmp #26',' php\n.if ::MAPPER_MMC5\n jsr Cv3DmcSceneRequest\n.else\n lda AvAudioRequest\n.endif\n cmp #26')
 change('src/cv3_source_audio.s',' jsr CvAudioPlay\n lda Cv3NoiseActive','.if ::MAPPER_MMC5\n jsr Cv3DmcBeforeCv1\n.else\n jsr CvAudioPlay\n.endif\n lda Cv3NoiseActive')
 for name in('src/guest_audio.s','src/bass_source_sfx.s','src/remaining_audio.s'):
  f=stage/name;s=f.read_text();count=s.count('  sta BassDmcActive');assert count
  change(name,'  sta BassDmcActive','''.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jsr Cv3DmcOwnerWrite
.else
  sta BassDmcActive
.endif''',count)
 change('src/guest_audio.s','  sta BassAudioLastGround\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr Cv3DmcOwnerWrite','  sta BassAudioLastGround\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr Cv3DmcResetOwner')
 change('src/guest_audio.s','Silent:\n  lda #0\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr Cv3DmcOwnerWrite','Silent:\n  lda #0\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr Cv3DmcResetOwner')
 change('src/guest_audio.s','DmcEnded:\n  lda #0\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr Cv3DmcOwnerWrite\n.else\n  sta BassDmcActive\n.endif\n  sta $4011','DmcEnded:\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr Cv3DmcEndedGate\n  .res 5,$ea ; original eight-byte completion span\n.else\n  lda #0\n  sta BassDmcActive\n  sta $4011\n.endif')
 change('src/collision.s','LmNativeMusicLegacy:\n  jmp ExpandedAudioTick\n  .res 26,$ea','LmNativeMusicLegacy:\n  jmp ExpandedAudioTick\n.if ::MAPPER_MMC5\n.include "cv3_dmc_completion.inc"\n  .res 1,$ea\n.else\n  .res 26,$ea\n.endif')
 change('smb1base-mmc5-expanded.cfg','    X5_NEW_7D: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$7d;','    X5_NEW_7D: start=$c000, size=$1af7, type=ro, file=%O, fill=yes, fillval=$ff, bank=$7d;\n    CV3_DMC_C: start=$daf7,size=$031a,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7d;\n    CV3_DMC_TAIL: start=$de11,size=$01ef,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7d;')
 change('smb1base-mmc5-expanded.cfg','SEGMENTS {','SEGMENTS {\n    CV3_DMC_MANAGER:load=CV3_DMC_C,type=ro;')
 append('src/entrypoint.s','.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "cv3_dmc_complete.s"\n.endif\n')
 change('tools/build_mmc5_expanded.py',' rom=out.read_bytes();actual_mapper='," if flag:\n  from prepare_cv3_dmc_mirror import prepare\n  prepare(root,out)\n rom=out.read_bytes();actual_mapper=")
 build(stage,'candidate');old,new=load(out/'baseline.nes'),load(out/'candidate.nes')
 ol={q[2]:q[1]for l in(out/'baseline.lbl').read_text().splitlines()if len(q:=l.split())==3};nl={q[2]:q[1]for l in(out/'candidate.lbl').read_text().splitlines()if len(q:=l.split())==3};moved=[(n,v,nl.get(n))for n,v in ol.items()if nl.get(n)!=v];assert not moved,moved[:10]
 assert old['raw'][:16]==new['raw'][:16]and old['raw'][1048592:]==new['raw'][1048592:]
 for n in('BassWaterDpcm','AvDmcLinkTakeDamage','AvDmcSimonTakeDamage'):
  lo,hi=location(old,n),location(old,n+'End');assert old['raw'][lo:hi]==new['raw'][lo:hi]
 changes=[];patch=''
 for f in stage.rglob('*'):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(stage);b=base/rel
  if not b.exists()or f.read_bytes()!=b.read_bytes():
   changes.append(dict(path=str(rel).replace('\\','/'),sha256=sha(f)))
   if f.suffix in('.s','.inc','.py','.cfg'):patch+=''.join(difflib.unified_diff(b.read_text().splitlines(True)if b.exists()else[],f.read_text().splitlines(True),fromfile='a/'+str(rel)if b.exists()else'/dev/null',tofile='b/'+str(rel)))
 (out/'implementation.patch').write_text(patch);diff=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
 result=dict(prepared=True,accepted=False,baseline_ROM_sha256=a.baseline_sha,candidate_ROM_sha256=sha(out/'candidate.nes'),changed_bytes=len(diff),changed_banks=sorted({(i-16)//8192 for i in diff}),old_exported_PC_RAM_CHR_exact=True,new_RAM_bytes=0,reused_private_bytes=list(range(32,36)),sources=changes,scope='Private source build only; source priority, owner lifecycle and native execution still require qualification.')
 (out/'prepare.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
