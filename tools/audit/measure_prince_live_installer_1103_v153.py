"""Corrected C2 installer after finalizer return; retains149-152 negative."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_strike_manifest_1103_v130 as C
O=C.O;A=C.M.A


def assemble(name,text,cfg):
 data,labels=A.assemble(name,text,cfg)
 for suffix in ['o','cfg','lbl']:(O/(name+'.'+suffix)).unlink()
 return data,labels


def main():
 installer='''.setcpu "6502"
.segment "INSTALL"
.export PpInstallLive,PpInstallLiveEnd
PpInstallLive:
 ldy #52
Copy:
 lda $c200,y
 sta $bfa3,y
 cmp $bfa3,y
 bne Failed
 lda #0
 sta $c200,y
 dey
 bpl Copy
 sec
 rts
Failed:
 clc
 rts
PpInstallLiveEnd:
'''
 install,ilab=assemble('native-installer-v153',installer,'MEMORY{M:start=$c766,size=$1b,file=%O;}SEGMENTS{INSTALL:load=M,type=ro;}');assert len(install)==25
 final='''PpNativeResetTail=$dee7
.setcpu "6502"
.segment "FINAL"
.export PpStageLive,PpStageInstaller,PpStageLiveEnd
PpStageLive:
 ldy #52
Copy:
 lda $c6f9,y
 sta $c200,y
 dey
 bpl Copy
PpStageInstaller:
 ldy #24
CopyInstaller:
 lda $c72e,y
 sta $c766,y
 dey
 bpl CopyInstaller
 txa
 jmp PpNativeResetTail
PpStageLiveEnd:
 .res 27-(*-PpStageLive),$ea
'''
 fbytes,flab=assemble('native-final-v153',final,'MEMORY{M:start=$bfc4,size=$1b,file=%O;}SEGMENTS{FINAL:load=M,type=ro;}');assert len(fbytes)==27
 runtime=bytearray((O/'native-runtime-v149.bin').read_bytes());runtime[0x1fc4:0x1fdf]=fbytes
 state=(O/'native-state-v149.bin').read_bytes()+install;assert len(state)==1607
 lab=json.loads((O/'native-labels-v149.json').read_text());lab.update(ilab);lab.update(flab)
 for name,data in [('runtime',runtime),('state',state)]:(O/f'native-{name}-v153.bin').write_bytes(data)
 (O/'native-labels-v153.json').write_text(json.dumps(lab,indent=2)+'\n')
 owner=(O/'post-owner-v149.s').read_text();start=owner.index(' jsr PrTypedWorker\n');end=owner.index(' bcc CoFailed\n',start)
 owner=owner[:start]+' jsr PrTypedWorker\n .res 15,$ea\n'+owner[end:]
 owner=owner.replace('PrCopyLive=$a7dc','PrCopyLive=$a7dc')
 cfg=(O/'post-owner-v130.cfg').read_text().replace('post-owner-extra-v130.bin','post-owner-extra-v153.bin')
 obin,olab=assemble('post-owner-v153',owner,cfg);extra=(O/'post-owner-extra-v153.bin').read_bytes();assert (len(obin),len(extra))==(531,98)
 selector=(O/'post-selector-v130.s').read_text()+'''
PrCopyLive:
 sta $016a
 lda #<$c766
 sta $016c
 lda #>$c766
 sta $016d
 lda #3
 jsr $015a
 rts
'''
 sbin,slab=assemble('post-selector-v153',selector,(O/'post-selector-v130.cfg').read_text());assert len(sbin)==175 and slab['PrCopyLive']==0xa7dc
 oldlabels=C.M.A.L.P.T.labels(O/'post-owner-v130.lbl')
 assert all(olab[n]==oldlabels[n]for n in ['CoCold','CoRetire','CoCheckCode','CoCheckHeaders','CoOwnerEnd'])
 q=dict(measured=True,qualified=False,ROM_written=False,shared_files_mutated=False,root_grant_required=True,negative_superseded='live-cold-negative-v152.json: resident A65 cannot write RAM3 through A-window. Now genuine FarCall executes installer in C2 with A3; never maps out executing resident code.',runtime_bytes=len(runtime),metadata_bytes=6092,state_bytes=len(state),live_half_open=[0xbfa3,0xbfd8],installer_half_open=[0xc766,0xc77f],installer_staged_half_open=[0xc72e,0xc747],cold_packet_half_open=[0xc200,0xc235],finalizer_bytes_used=flab['PpStageLiveEnd']-flab['PpStageLive'],manager_bytes=len(obin),manager_padding_unchanged=True,extra_bytes=len(extra),selector_bytes=len(sbin),selector_spare=178-len(sbin),required='Actual new backing/fullcold copy-before-overwrite/unwind/readback/clear-before-publish; finite original/private executable reader/write closure; foreign/cold/Fresh/retire/IRQ proof and root shared/lifetime amendment. DK alternative remains separate/ungranted.',shared_labels=dict(olab,**slab),bindings={p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),O/'live-policies-measurement-v149.json',O/'live-cold-negative-v152.json',O/'native-metadata-v149.bin',O/'native-state-v149.bin',O/'native-live-v149.bin',*[O/f'native-{n}-v153.bin'for n in ['runtime','state','installer','final']],O/'post-owner-v153.s',O/'post-owner-v153.bin',O/'post-owner-extra-v153.bin',O/'post-selector-v153.s',O/'post-selector-v153.bin']})
 (O/'live-installer-measurement-v153.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','shared_labels']}))


if __name__=='__main__':main()
