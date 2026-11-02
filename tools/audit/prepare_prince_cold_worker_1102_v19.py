"""Measured typed Prince cold worker; no shared source, candidate or install."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from private_build_outputs_v1 import validate
O=L.O


def assemble(name,text,cfg):
 asm=O/f'{name}.s';asm.write_text(text);config=O/f'{name}.cfg';config.write_text(cfg);cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/f'{name}.o'],[cc/'ld65.exe','-C',config,O/f'{name}.o','-o',O/f'{name}.bin','-Ln',O/f'{name}.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 return(O/f'{name}.bin').read_bytes(),L.P.T.labels(O/f'{name}.lbl')


def main():
 b=scoped_load(L.BASE);bindings={n:address(b,n)for n in ['R0','R1','SelectedCharacter','DisableScreenFlag','Mirror_PPUMASK','NmiDisable']};src=R/'tools/reference/prince_lzdict_decoder_1102_v9.s';text=src.read_text()
 changes={'lda #$c2':'lda #$c3','lda PpLdStore+1':'lda R0','lda PpLdStore+2':'lda R1','PpLdStore:sta $ffff':'PpLdStore:sta (R0),y\n cmp (R0),y\n bne PpLdFailed','inc PpLdStore+1':'inc R0','inc PpLdStore+2':'inc R1','BitsLeft:.byte 0':'PpLdFailed:\n pla\n pla\n pla\n pla\n clc\n rts\nBitsLeft:.byte 0'}
 for a,z in changes.items():assert a in text,a;text=text.replace(a,z)
 decoder,lab=assemble('cold-decoder-v19',''.join(f'{n}=${a:04x}\n'for n,a in bindings.items())+text,'MEMORY{M:start=$c000,size=$100,file=%O;}SEGMENTS{DECODER:load=M,type=ro;}')
 life=L.P.T.labels(O/'host-life-v12.lbl');q=json.loads((O/'native-storage-v18.json').read_text());rows={v['name']:v for v in q['decoded_images']};base=dict(bindings,DecoderBytes=len(decoder),PpLdDecode=lab['PpLdDecode'],PpLdLoad=lab['PpLdLoad'],PpLdRemain=lab['PpLdRemain'],PpHostColdFinalize=life['PpHostColdFinalize'])
 for name,prefix in [('runtime','Runtime'),('metadata','Metadata'),('state_code','State')]:
  row=rows[name];base.update({prefix+'Input':row['source_half_open'][0],prefix+'Packed':row['compressed_bytes'],prefix+'Bytes':row['uncompressed_bytes']})
 source=R/'tools/reference/prince_cold_worker_1102_v19.s';cfg=f'MEMORY{{B:start=${0xd160+len(decoder):04x},size=$100,file=%O;W:start=$c100,size=$200,file=%O;}}SEGMENTS{{BOOT:load=B,type=ro;WORKER:load=W,type=ro;}}'
 size=0
 for iteration in range(3):
  physical=31072+len(decoder)+size;base['InitialSourcePage']=physical//1024-30;base['InitialSourceAddress']=0xc00+physical%1024
  # Cold bootstrap decoder begins D160; its successor grows by five bytes.
  data=source.read_text().replace('lda $d160,x','lda $d160,x')
  blob,labels=assemble('cold-worker-v19',''.join(f'{n}=${a:04x}\n'for n,a in base.items())+data,cfg)
  if size==len(blob):break
  size=len(blob)
 else:raise AssertionError('Fixed-size worker source offset did not converge')
 art=(O/'prince-body-8x16.chr').read_bytes();payload=art+decoder+blob+b''.join((O/f'native-{n}-v18.lzdict').read_bytes()for n in ['runtime','metadata','state_code'])
 assert len(payload)<=44032
 (O/'cold-pool-v19.bin').write_bytes(payload)
 result=dict(measured=True,qualified=False,base_ROM_SHA256=L.PIN,host_ROM_created=False,shared_sources_changed=False,decoder_bytes=len(decoder),decoder_half_open=[0xc000,0xc000+len(decoder)],decoder_per_byte_destination_readback=True,decoder_borrows_native_R0_R1=True,boot_half_open=[labels['PpColdBoot'],labels['PpColdBootEnd']],worker_half_open=[0xc100,labels['PpColdWorkerEnd']],worker_storage_bytes=len(blob),bootstrap_CHR_pages=[617,619],common_descriptor_bytes=[2,0,8,0xd0,617&255,617>>8,619&255,619>>8],resident_call='After common boot copy, map RAM2 into C000 and use FarCallCommon to PpColdBoot with A=3 (RAM3 A000). Existing resident outer frame must preserve R0..7/SMC/maps/PPU/AXYP and commit both headers last.',decoded_order=['runtime','metadata','state_code'],cold_worker_overwritten_only_by_last_state_decode=True,pool_bytes=len(payload),pool_capacity=44032,pool_spare=44032-len(payload),physical_source_page_order=[617,619,621,623,625,627,690,691,692,693,695,795,291],initial_compressed_source=dict(page=base['InitialSourcePage'],ppu_address=base['InitialSourceAddress']),required_amendments=['Cold-only execution C100..C300 includes the existing C200..C235 packet interval while both auth headers are invalid and no actor is initialized.','Shared8B bootstrap descriptor plus third-owner manager/retirement/auth/cold dispatch require separate source-funded approval.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),src,source,O/'cold-decoder-v19.bin',O/'cold-worker-v19.bin',O/'cold-pool-v19.bin',O/'native-storage-v18.json']})
 (O/'cold-worker-layout-v19.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
