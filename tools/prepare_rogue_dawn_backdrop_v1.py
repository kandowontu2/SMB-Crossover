"""Sparse real-linked native-backdrop successor on immutable f467; no native."""
from pathlib import Path
import difflib
import json
import subprocess
import sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/rogue-dawn-scheduler-v5'
U=R/'build/rogue-dawn-host-ui-v1'
O=R/'build/rogue-dawn-backdrop-v1'

def main():
 assert not(O/'build.json').exists(),'Frozen successor'
 h=json.loads((P/'handoff.json').read_text())
 for z in h['bindings']:assert ref.binding(z['path'])==z,z['path']
 b=scoped_load(P/'candidate.nes');assert ref.digest(b['raw'])=='f4677c91c642c2720770b5f20e8590664d81ee5f6bcd7bcdae6994b739fb2fdb'
 a=16+121*8192+0x1f00;e=a+112
 owners=[]
 for g in b['segs'].values():
  if 'ooffs'not in g:continue
  lo,size=int(g['ooffs'],0),int(g['size'],0)
  if lo<e and lo+size>a:owners.append(g['name'])
 assert not owners and b['raw'][a:e]==b'\xff'*112,owners
 layout=json.loads((P/'layout.json').read_text())
 for z in layout['immutable_raw_data_views']:
  lo,size=z['file_offset'],z['bytes'];assert not(lo<e and lo+size>a),z['name']
 c=location(b,'X5LegacyGetPlayerColors::BackgroundColors')
 native=b['raw'][c:c+8];assert native==bytes.fromhex('22220f0f0f220f0f')
 O.mkdir(exist_ok=True)
 for n in ['main.c','private.cfg']:(O/n).write_bytes((P/n).read_bytes())
 entry=(P/'entrypoint.s').read_text()
 entry+='\n.if ::ENABLE_MMC5_EXPANDED\n.import RdBackdropQueue\n.export AreaType,BackgroundColorCtrl\n.endif\n'
 (O/'entrypoint.s').write_text(entry)
 body=(U/'body-source.s').read_text();start=body.index('.proc RdBodyQueuePalette');end=body.index('.endproc',start)+len('.endproc')
 old=body[start:end];new='.proc RdBodyQueuePalette\n farcall RdBackdropQueue,jmp\n.endproc'
 body=body[:start]+new+body[end:];(O/'body-source.s').write_text(body)
 patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='f467/body-source.s',tofile='backdrop/body-source.s'))
 # This is an explicit successor to the exact prior body-tail assertion;
 # all later A95 targets are genuinely relocated, never old DBG aliases.
 shift=int(b['syms']['RdBodyQueuePalette']['size'],0)-18
 life=(P/'lifecycle-source.s').read_text();pre=f'.assert RdLifeStart=${address(b,"RdBodyEnd"):04x},error,"Frozen body tail"'
 assert life.count(pre)==1
 successor=life.replace(pre,f'.assert RdLifeStart=${address(b,"RdBodyEnd")-shift:04x},error,"Qualified backdrop successor body tail"')
 (O/'lifecycle-source.s').write_text(successor)
 patch+=''.join(difflib.unified_diff(life.splitlines(True),successor.splitlines(True),fromfile='f467/lifecycle-source.s',tofile='backdrop/lifecycle-source.s'))
 (O/'source.patch').write_text(patch)
 helper=R/'src/rogue_dawn_host_backdrop_v1.s'
 helpercmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(R),
            '--create-full-dep',str(O/'backdrop.dep'),str(helper),'-o',str(O/'backdrop.o')]
 oldbuild=json.loads((P/'build.json').read_text())
 cmd=[z.replace(str(P),str(O))for z in oldbuild['commands'][3]]
 for i,z in enumerate(cmd):
  if z in [str(O/f'audio{k}.o')for k in range(3)]:cmd[i]=str(P/Path(z).name)
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(P)]
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(O)]
 cmd.append(str(O/'backdrop.o'))
 for args,name in [(helpercmd,'helper.log'),(cmd,'build.log')]:
  log=O/name
  if log.exists() and 'Error:'in log.read_text() and not(O/('first-'+name)).exists():
   (O/('first-'+name)).write_bytes(log.read_bytes())
  z=subprocess.run(args,cwd=R,capture_output=True,text=True)
  (O/name).write_text(z.stdout+z.stderr)
  assert z.returncode==0,(name,(z.stdout+z.stderr)[-6000:])
 prepare(R,O/'candidate.nes');n=scoped_load(O/'candidate.nes')
 assert address(n,'RdBackdropStart')==0xbf00 and address(n,'RdBackdropEnd')<=0xbf70
 assert address(n,'RdCueGateEnd')<=0xbf00
 assert n['raw'][16+121*8192+0x1e00:16+121*8192+0x1efe]==b['raw'][16+121*8192+0x1e00:16+121*8192+0x1efe]
 assert n['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32]==b['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32]
 assert n['raw'][16+1048576:]==b['raw'][16+1048576:]
 changes={}
 for i,(x,y)in enumerate(zip(b['raw'],n['raw'])):
  if x!=y:changes[str((i-16)//8192)]=changes.get(str((i-16)//8192),0)+1
 assert set(changes)<=set(map(str,[0,1,2,3,4,66,95,121,124,125,126,127])),changes
 deps=list(dict.fromkeys(dependencies(O/'assembler-full.dep')+dependencies(O/'backdrop.dep')))
 reused=[P/f'audio{k}.o'for k in range(3)]+[U/'weapon-object.o']
 receipt=dict(passed=True,source_build_only=True,native_run=False,qualified=False,
  ROM=ref.binding(O/'candidate.nes'),parent=ref.binding(P/'candidate.nes'),
  commands=oldbuild['commands'][:3]+[cmd],executed_commands=[helpercmd,cmd],
  reused_audio_assembly_commands_not_reexecuted=oldbuild['commands'][:3],
  actual_ASM_incbin_inputs=len(deps),A95_end=hex(address(n,'RdCueGateEnd')),
  palette_helper=dict(bank=121,start=hex(address(n,'RdBackdropStart')),end=hex(address(n,'RdBackdropEnd')),
                      bytes=address(n,'RdBackdropEnd')-address(n,'RdBackdropStart'),ROOT_approved_cap=112),
  native_BG_provenance=dict(symbol='X5LegacyGetPlayerColors::BackgroundColors',file_offset=c,bytes=native.hex()),
  reserved_item_tail='Original BE00..BFFF512B owned tail is now subdivided: BE00..BEFD descriptors exact, BF00..<BF70 palette code approved, remainder not consumed.',
  per_bank_delta=changes,
  bindings=[ref.binding(p)for p in dict.fromkeys(deps+[Path(__file__),helper,O/'private.cfg',O/'source.patch',P/'handoff.json',
      *reused,O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'candidate.map'])])
 (O/'build.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({k:receipt[k]for k in ['ROM','palette_helper','A95_end','actual_ASM_incbin_inputs','per_bank_delta']},indent=2))
if __name__=='__main__':main()
