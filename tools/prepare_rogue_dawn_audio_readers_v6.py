"""Private measured raw-reader specialization on immutable1241; no native."""
from pathlib import Path
import difflib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/rogue-dawn-backdrop-v1';S=R/'build/rogue-dawn-scheduler-v5'
O=R/'build/rogue-dawn-audio-readers-v6'

def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z)

def main():
 assert not(O/'build.json').exists(),'Frozen candidate'
 h=json.loads((P/'handoff.json').read_text())
 for z in h['bindings']:assert ref.binding(z['path'])==z,z['path']
 b=scoped_load(P/'candidate.nes')
 assert ref.digest(b['raw'])=='1241df0735eaf81a1c9db607c9a956b68add1bbad0416352d28c894c390df80c'
 driver=(R/'src/rogue_dawn_audio_scheduler_v5.s').read_text()
 native=(R/'src/rogue_dawn_audio_scheduled_native_v5.inc').read_text()
 original=driver
 start=driver.index('.proc RdaReadAbsoluteY');end=driver.index('.macro RdaIndirectReader',start)
 fixed='''; Actual four source LDA absolute,Y sites, all immutable80xx operands.
; IncomingA andNZ are overwritten by originalLDA. C/V/D/I survive the
; constant-offset LDA and are captured before any address arithmetic.
'''
 for low in [2,3,0x1a,0x4c]:
  fixed+=f'.proc RdaRead80{low:02X}Y\n lda #${low:02x}\n bne RdaReadFixedCommon\n.endproc\n'
 fixed+='''RdaReadFixedCommon:
 sta RdaPtr
 RdaReadSave
 tya
 clc
 adc RdaPtr
 sta RdaPtr
 lda #$80
 adc #0
 sta RdaPtr+1
 jsr RdaReadRomValue
 jmp RdaReadReturn
'''
 driver=driver[:start]+fixed+driver[end:]
 driver=once(driver,' jsr RdaReadRom\n jmp RdaReadReturn',' jsr RdaReadRomValue\n jmp RdaReadReturn')
 driver=once(driver,'RdaReadReturn:\n sta RdaReadValue','RdaReadReturn:')
 # Exported RdaReadRom retains actual value/NZ/X/Y/CV/DI return semantics.
 # Only true source helpers call the internal no-A-reload endpoint.
 driver=once(driver,'.proc RdaReadRom\n lda RdaPtr+1','.proc RdaReadRom\n jsr RdaReadRomValue\n lda RdaReadValue\n rts\n.endproc\n.proc RdaReadRomValue\n lda RdaPtr+1')
 driver=once(driver,' sta $5115\n lda RdaReadValue\n rts\nUpper:',' sta $5115\n rts\nUpper:')
 driver=once(driver,'.include "rogue_dawn_audio_scheduled_native_v5.inc"','.include "rogue_dawn_audio_reader_native_v6.inc"')
 sites={0xba5c:2,0xba61:3,0xbb2b:0x1a,0xbf2c:0x4c}
 for pc,low in sites.items():
  old=f' jsr RdaReadAbsoluteY ;49:{pc:04X} b9{low:02x}80'
  native=once(native,old,f' jsr RdaRead80{low:02X}Y ;49:{pc:04X} b9{low:02x}80')
 assert 'RdaReadAbsolute' not in driver and 'RdaReadAbsolute' not in native
 leaf=R/'src/rogue_dawn_audio_reader_v6.s';nl=R/'src/rogue_dawn_audio_reader_native_v6.inc'
 leaf.write_text(driver);nl.write_text(native)
 O.mkdir(exist_ok=True)
 for n in ['main.c','entrypoint.s','private.cfg']:(O/n).write_bytes((P/n).read_bytes())
 # Only the source A62/C97 object changes. All true caller inputs resolve
 # against frozen1241 first, then its frozenf467/890 parents.
 base=json.loads((S/'build.json').read_text())
 asm=[z.replace(str(S),str(O))for z in base['commands'][0]]
 asm=[str(leaf)if z==str(R/'src/rogue_dawn_audio_scheduler_v5.s')else z for z in asm]
 asm[1:1]=['-I',str(P),'-I',str(S)]
 pb=json.loads((P/'build.json').read_text());cmd=[z.replace(str(P),str(O))for z in pb['commands'][3]]
 for i,z in enumerate(cmd):
  if z==str(S/'audio0.o'):cmd[i]=str(O/'audio0.o')
  if z==str(O/'backdrop.o'):cmd[i]=str(P/'backdrop.o')
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(P)]
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(O)]
 for args,name in [(asm,'audio.log'),(cmd,'build.log')]:
  log=O/name
  if log.exists() and 'Error:'in log.read_text()and not(O/('first-'+name)).exists():(O/('first-'+name)).write_bytes(log.read_bytes())
  z=subprocess.run(args,cwd=R,capture_output=True,text=True);log.write_text(z.stdout+z.stderr)
  assert z.returncode==0,(name,(z.stdout+z.stderr)[-5000:])
 prepare(R,O/'candidate.nes');n=scoped_load(O/'candidate.nes')
 assert address(n,'RdaAdapterEnd')<=0xc000 and address(n,'RdaUpperStart')==0xc480
 assert address(n,'RdBackdropStart')==0xbf00 and address(n,'RdBackdropEnd')==0xbf5f
 assert n['raw'][16+1048576:]==b['raw'][16+1048576:]
 # Audio rawviews and source/header/CHR data remain byteexact.
 layout=json.loads((S/'layout.json').read_text())
 for z in layout['immutable_raw_data_views']:
  lo,size=z['file_offset'],z['bytes'];assert n['raw'][lo:lo+size]==b['raw'][lo:lo+size]
 delta={}
 for i,(a,z)in enumerate(zip(b['raw'],n['raw'])):
  if a!=z:delta[str((i-16)//8192)]=delta.get(str((i-16)//8192),0)+1
 # Genuine common farcall operands follow the moved A62 frame entry.
 common=16+63*8192
 common_changes=[]
 for i in range(8192):
  if b['raw'][common+i]==n['raw'][common+i]:continue
  at=common+i
  assert b['raw'][at-1]==n['raw'][at-1]==0xa9
  matched=False
  for k in [1,2]:
   target=address(b,'FarcallJmpTarget_SMC')+k
   if b['raw'][at+1:at+4]==bytes([0x8d,target&255,target>>8]):
    shift=8*(k-1)
    assert b['raw'][at]==(address(b,'RdsAudioFrame')>>shift)&255
    assert n['raw'][at]==(address(n,'RdsAudioFrame')>>shift)&255
    matched=True;common_changes.append(dict(offset=i,kind='actual frame farcall target operand',byte=k))
  assert matched,hex(at)
 assert set(delta)<=set(map(str,[62,63,97,95])),delta
 patch=''.join(difflib.unified_diff(original.splitlines(True),driver.splitlines(True),fromfile='f467-driver',tofile='reader-v6'))
 patch+=''.join(difflib.unified_diff((R/'src/rogue_dawn_audio_scheduled_native_v5.inc').read_text().splitlines(True),native.splitlines(True),fromfile='f467-native',tofile='reader-v6-native'))
 (O/'source.patch').write_text(patch)
 deps=list(dict.fromkeys(dependencies(O/'assembler-full.dep')+dependencies(O/'audio0.dep')))
 out=dict(passed=True,source_build_only=True,native_run=False,qualified=False,ROM=ref.binding(O/'candidate.nes'),parent=ref.binding(P/'candidate.nes'),
  commands=base['commands'][:3]+[cmd],executed_commands=[asm,cmd],A62_end=hex(address(n,'RdaAdapterEnd')),
  prefix_used=address(n,'RdaOriginalRng')+24-address(n,'RdaDriverStart'),actual_ASM_incbin_inputs=len(deps),
  per_bank_delta=delta,common_target_relocations=common_changes,source_sites={hex(k):hex(0x8000+v)for k,v in sites.items()},
  bindings=[ref.binding(p)for p in dict.fromkeys(deps+[Path(__file__),leaf,nl,P/'handoff.json',O/'private.cfg',O/'source.patch',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'candidate.map',P/'backdrop.o',S/'audio1.o',S/'audio2.o'])])
 (O/'build.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in ['ROM','A62_end','prefix_used','per_bank_delta']},indent=2))
if __name__=='__main__':main()
