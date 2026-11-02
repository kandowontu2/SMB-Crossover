"""Measure an isolated common copy/verify body; allocate no resident bytes."""
import hashlib,json,subprocess
from pathlib import Path
import prepare_bubble_bobble_component_1101_v2 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
R=P.R;O=P.O;ROM=R/'build/excitebike-pose-1101-v3/current4.nes';PIN='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
sha=lambda b:hashlib.sha256(b).hexdigest()


def assemble(stem,source,cfg,includes=()):
 (O/(stem+'.s')).write_text(source);(O/(stem+'.cfg')).write_text(cfg)
 cc=R/'tools/Windows/cc65/bin'
 command=[cc/'ca65.exe','-I',R/'tools/reference','--bin-include-dir',O]
 for folder in includes:command+=['-I',folder]
 command += [O/(stem+'.s'),'-o',O/(stem+'.o')]
 for cmd in[command,[cc/'ld65.exe','-C',O/(stem+'.cfg'),O/(stem+'.o'),'-o',O/(stem+'.bin'),'-Ln',O/(stem+'.lbl')]]:
  r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert r.returncode==0,'\n'.join(r.stderr.splitlines()[:10])
 return P.labels(O/(stem+'.lbl'))


def main():
 b=scoped_load(ROM);assert sha(b['raw'])==PIN
 names=['R0','R1','R2','R3','R4','R5','R6','R7','CurrentBankC','OperMode','FamilyMainCommit','DisableScreenFlag','Mirror_PPUMASK','Mirror_PPUCTRL','NmiDisable']
 source='.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in names)+'.include "bubble_bobble_common_cold_1102_v4.inc"\n'
 lab=assemble('common-cold',source,'MEMORY{P:start=$a000,size=$1000,file=%O;}SEGMENTS{BB_COLD_PROPOSAL:load=P,type=ro;}');blob=(O/'common-cold.bin').read_bytes()
 q=dict(passed=True,proposal_only=True,resident_granted=False,shared_bytes_written=False,ROM_SHA256=PIN,prototype_SHA256=sha(blob),worker_bytes=lab['BbColdWorkerEnd']-lab['BbColdWorker'],descriptors_bytes=lab['BbColdProposalEnd']-lab['BbColdDescriptors'],total_bytes=len(blob),labels=lab,API='R3/R4 immutable resident descriptor; R0..7 clobbered,Csuccess; caller already savedAXYP/ZP/SMC/maps,invalidatedbothheaders,SEI andownsforcedblank. Caller commits bothheaders afterC1 and restoresPPU/maps. No owner admission/authentication or rawID assumed.',descriptors=dict(Sh=dict(rows=9,code_rows=7,zero_pages=32,source=[506,507,508,509,510,513,515,516,517]),Ex=dict(rows=8,code_rows=6,zero_pages=32,source=list(range(728,736))),BB=dict(rows=8,code_rows=8,zero_pages=4,source=[301,305,337,362,363,440,819,666])),remaining=['Measure exact replaced current Sh/Ex instruction spans and caller descriptor setup before funding claim.','CPU differential copy/readback/PPU/map/ISR tests against current owner workers.','A common copy/verify worker alone is insufficient new owner loader/router/retirement funding.'])
 # No shared file is patched. Measure exact split source-backed ROM pads.
 definitions=source[:source.index('.include')]
 flags='BB_COLD_TRUSTED_CALLER=1\nBB_COLD_FIXED_META_D0=1\nBB_COLD_SPLIT_MAP=1\nBB_COLD_EX_BB_ONLY=1\n'
 cfg='MEMORY{P:start=$af40,size=$c0,file=%O;M:start=$b9d6,size=$2a,file="'+(O/'common-split-map.bin').as_posix()+'";}SEGMENTS{BB_COLD_PROPOSAL:load=P,type=ro;BB_COLD_MAP:load=M,type=ro;}'
 split=assemble('common-split',definitions+flags+'.include "bubble_bobble_common_cold_1102_v4.inc"\n',cfg)
 splitbody=(O/'common-split.bin').read_bytes();splitmap=(O/'common-split-map.bin').read_bytes()
 # Measure the exact current source-owned Ex frame with its data/ABI retained.
 # Only its cold zero/copy/verify body and row mapper are factored out.
 exroot=R/'build/excitebike-pose-1101-v3';original=(exroot/'owner-loader.inc').read_text()
 originalbytes=(exroot/'owner-loader.bin').read_bytes();assert len(originalbytes)==556
 current=b['raw'][16+65*8192+0xe00:16+65*8192+0xe00+556]
 cookieoff=0xb016-0xae00;assert current[:cookieoff]==originalbytes[:cookieoff]and current[cookieoff+16:]==originalbytes[cookieoff+16:]
 payload=b''.join(b['raw'][1048592+p*1024:1048592+(p+1)*1024]for p in range(728,739))
 expected_cookie=bytes([0xa7,37,1])+hashlib.sha256(payload).digest()[:13]
 assert current[cookieoff:cookieoff+16]==expected_cookie,'Actualcf Ex recovery payload must authenticate under the actual current cookie'
 (O/'common-current-Ex-cookie.bin').write_bytes(current[cookieoff:cookieoff+16])
 ex=original.replace('"excitebike-cookie.bin"','"common-current-Ex-cookie.bin"')
 start=ex.index(' ; Clear and read back');end=ex.index(' ldx #3\n ldy #1\nExPublishBank:',start)
 setup=f' lda #<${split["BbColdExDescriptor"]:04x}\n sta R3\n lda #>${split["BbColdExDescriptor"]:04x}\n sta R4\n ExRomFar ${split["BbColdWorker"]:04x},$fb\n jcc ExLoadFailed\n'
 ex=ex[:start]+setup+ex[end:]
 start=ex.index('ExMapRow:\n');end=ex.index('ExRestorePpu:\n',start);ex=ex[:start]+ex[end:]
 ex=ex.replace('ExSavedSmcOffsets:','.segment "EX_FIXED_ABI"\nExSavedSmcOffsets:')
 prefix=(exroot/'owner-loader.s').read_text().split('.include "owner-loader.inc"')[0]
 prefix+=''.join(f'{n}=${address(b,n):04x}\n'for n in ['R3','R4','R5','R6','R7'])
 excfg='MEMORY{P:start=$ae00,size=$211,file=%O;D:start=$b011,size=$1b,file="'+(O/'common-Ex-fixed-ABI.bin').as_posix()+'";}SEGMENTS{EXCITEBIKE_RESIDENT:load=P,type=ro;EX_FIXED_ABI:load=D,type=ro;}'
 exlab=assemble('common-Ex-frame',prefix+ex+'\n.export ExRetireBoth\nExRetireBoth:\n jsr ExRetire\n jmp $a849\n',excfg)
 exmain=(O/'common-Ex-frame.bin').read_bytes();exfixed=(O/'common-Ex-fixed-ABI.bin').read_bytes()
 assert exfixed==current[0x211:]
 assert all(exlab[n]==v for n,v in [('ExLoad',0xae6a),('ExCheckCode',0xae00),('ExCookie',0xb016),('ExRetireBoth',0xb026)])
 tailflags='BB_COLD_TRUSTED_CALLER=1\nBB_COLD_FIXED_META_D0=1\nBB_COLD_BB_ONLY=1\n'
 tail=assemble('common-BB-tail',definitions+tailflags+'.include "bubble_bobble_common_cold_1102_v4.inc"\n','MEMORY{P:start=$a400,size=$e0,file=%O;}SEGMENTS{BB_COLD_PROPOSAL:load=P,type=ro;}')
 tailbytes=(O/'common-BB-tail.bin').read_bytes()
 q.update(actual_current_Ex_payload_SHA256=sha(payload),actual_current_Ex_cookie=expected_cookie.hex(),current_Ex_cookie_source_closed=True,split_pad_proposal=dict(physical_PRG=123,main_half_open=[0xaf40,0xaf40+len(splitbody)],main_with_two_descriptors=len(splitbody),map_half_open=[0xb9d6,0xb9d6+len(splitmap)],map_bytes=len(splitmap),total_bytes=len(splitbody)+len(splitmap),unused_third_pad=13,labels=split),factored_Ex_frame=dict(original_bytes=556,main_bytes=len(exmain),fixed_ABI_bytes=len(exfixed),total_bytes=len(exmain)+len(exfixed),source_funded_reclaimed_half_open=[0xae00+len(exmain),0xb011],source_funded_reclaimed_bytes=0xb011-0xae00-len(exmain),fixed_ABI_preimage_exact=True,external_entries_preserved=['ExLoad AE6A','ExCheckCode AE00','ExRetireBoth B026','ExCookie B016','savedSMC offsets B011'],labels=exlab),BB_art_tail_alternative=dict(helper_bytes=len(tailbytes),art_tail_available=224,conditional_RAM2_half_open=[0xc400,0xc400+len(tailbytes)],execution_alias=[0xa400,0xa400+len(tailbytes)],labels=tail,granted=False,remaining='Historical unused bootstrap alternative. Actual granted solution uses immutable metadataD000..D400, notC400.'),remaining=['CPU differential full Ex frame and direct Bub worker tests.','General new-owner header/authentication/retirement and scene/service routing still require measured source-funded integration.','Prince packed byte streams need a typed private worker; this full-page kernel does not claim Prince support.'])
 q['descriptors']['BB'].update(rows=9,source=[301,305,337,362,363,440,819,666,441],immutable_metadata_half_open=[0xd000,0xd400])
 q.update(resident_storage_granted=True,shared_routing_granted=False,immutable_helper_row_granted=True)
 (O/'common-cold-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','worker_bytes','descriptors_bytes','total_bytes','resident_granted','shared_bytes_written']}));print(json.dumps(dict(split_kernel_bytes=len(splitbody)+len(splitmap),Ex_reclaimed=q['factored_Ex_frame']['source_funded_reclaimed_bytes'],BB_tail_bytes=len(tailbytes))))


if __name__=='__main__':main()
