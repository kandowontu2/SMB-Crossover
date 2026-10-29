"""Source-floor correction plus stack-safe internal support query; no native."""
from pathlib import Path
import difflib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
P=R/'build/rogue-dawn-audio-readers-v6'
O=R/'build/rogue-dawn-floor-v2'
U=R/'build/rogue-dawn-host-ui-v1'

def once(s,a,z):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,z)

def main():
 assert not (O/'build.json').exists(),'Frozen successor'
 h=json.loads((P/'handoff.json').read_text())
 for z in h['bindings']:assert ref.binding(z['path'])==z,z['path']
 b=scoped_load(P/'candidate.nes')
 assert ref.digest(b['raw'])=='69a4476c6b05903a149a527f0b99b65cc80c7ebad80fde1ce6e71a44a4f41fd5'
 old=(U/'services-include.s').read_text()
 new=(R/'src/rogue_dawn_host_floor_v1.s').read_text()
 new=once(new,' jsr RdHsSupport\n bcs Blocked\nTileClear:',
  '; Geometry already owns the complete saved caller/private scratch image.\n; Only axisRh5 is live across the query; do not nest another ten pushes.\n lda Rh5\n pha\n jsr RdHsSupportQuery\n pla\n sta Rh5\n bcs Blocked\nTileClear:')
 start=new.index('.proc RdHsSupport\n');end=new.index('.endproc',start)+len('.endproc')
 support=new[start:end]
 support=once(support,'.proc RdHsSupport\n RdHsSave\n',
  '.proc RdHsSupport\n RdHsSave\n jsr RdHsSupportQuery\n jmp RdHsRestoreC\n.endproc\n; Private clobbering query: publiccallback or geometry outer save ownsABI.\n.proc RdHsSupportQuery\n')
 assert support.count(' jmp RdHsRestoreC')==3
 # Keep public wrapper tail, replace only both query terminal restores.
 a=support.index('.proc RdHsSupportQuery')
 support=support[:a]+support[a:].replace(' jmp RdHsRestoreC',' rts')
 new=new[:start]+support+new[end:]
 leaf=R/'src/rogue_dawn_host_floor_v2.s';leaf.write_text(new)
 O.mkdir(exist_ok=True)
 for n in ['main.c','private.cfg']:(O/n).write_bytes((P/n).read_bytes())
 B=R/'build/rogue-dawn-backdrop-v1'
 # Ten actual code bytes precede following bodies; retain fixed deathBF00,
 # genuinely relink callers, and make the prior fixed-tail assumptions explicit.
 for name,needle,successor in [
  ('body-source.s','.assert RdBodyStart=$b5d2,error,"Frozen motion unit end"',
   '.assert RdBodyStart=$b5dc,error,"Source-floor internal-query successor end"'),
  ('lifecycle-source.s','.assert RdLifeStart=$b7cc,error,"Qualified backdrop successor body tail"',
   '.assert RdLifeStart=$b7d6,error,"Source-floor successor body tail"')]:
  (O/name).write_text(once((B/name).read_text(),needle,successor))
 entry=once((P/'entrypoint.s').read_text(),'.include "services-include.s"',
  '.include "rogue_dawn_host_floor_v2.s"')
 (O/'entrypoint.s').write_text(entry)
 (O/'source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
  fromfile='69a/services-include.s',tofile='floor-v2/rogue_dawn_host_floor_v2.s')))
 previous=json.loads((P/'build.json').read_text())
 cmd=[z.replace(str(P),str(O))for z in previous['executed_commands'][-1]]
 for i,z in enumerate(cmd):
  if z==str(O/'audio0.o'):cmd[i]=str(P/'audio0.o')
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(P)]
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(O)]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
 if (O/'build.log').exists() and not (O/'first-build.log').exists():
  (O/'first-build.log').write_bytes((O/'build.log').read_bytes())
 (O/'build.log').write_text(z.stdout+z.stderr)
 assert z.returncode==0,(z.stdout+z.stderr)[-6000:]
 prepare(R,O/'candidate.nes');n=scoped_load(O/'candidate.nes')
 assert address(n,'RdCueGateEnd')<=0xbf00
 assert n['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32]==b['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32]
 assert n['raw'][16+1048576:]==b['raw'][16+1048576:]
 changes={}
 for i,(a,z)in enumerate(zip(b['raw'],n['raw'])):
  if a!=z:changes[str((i-16)//8192)]=changes.get(str((i-16)//8192),0)+1
 # Genuine current link relocates followingA95 entries and their actual
 # callers; never reuse oldDBG or hand-patch the cold target operands.
 assert set(changes)<=set(map(str,[0,1,2,3,4,29,62,63,66,94,95,121,124,125,126,127])),changes
 deps=dependencies(O/'assembler-full.dep')
 out=dict(passed=True,source_build_only=True,native_run=False,qualified=False,
  ROM=ref.binding(O/'candidate.nes'),parent=ref.binding(P/'candidate.nes'),
  executed_commands=[cmd],actual_ASM_incbin_inputs=len(deps),per_bank_delta=changes,
  A95_end=hex(address(n,'RdCueGateEnd')),A95_added_bytes=address(n,'RdCueGateEnd')-address(b,'RdCueGateEnd'),new_RAM_or_leases=False,
  preserved_negative=ref.binding(R/'build/rogue-dawn-floor-v1/controls-negative-1.json'),
  bindings=[ref.binding(p)for p in dict.fromkeys(deps+[Path(__file__),leaf,P/'handoff.json',
   O/'private.cfg',O/'source.patch',P/'audio0.o',R/'src/rogue_dawn_host_floor_v1.s',
   O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'candidate.map'])])
 (O/'build.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in ['ROM','per_bank_delta','A95_end','A95_added_bytes','actual_ASM_incbin_inputs']},indent=2))
if __name__=='__main__':main()
