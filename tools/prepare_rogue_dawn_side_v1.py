"""Private half-open side extent successor on immutable df44; no native."""
from pathlib import Path
import difflib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
P=R/'build/rogue-dawn-floor-v4';O=R/'build/rogue-dawn-side-v1'

def once(s,a,z):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,z)

def main():
 assert not(O/'build.json').exists(),'Frozen successor'
 for z in json.loads((P/'handoff.json').read_text())['bindings']:assert ref.binding(z['path'])==z,z['path']
 b=scoped_load(P/'candidate.nes');assert ref.digest(b['raw'])=='df44abd4b9e196aedb3a68fb33c74e83491ce3c8581812808838d86f16af62f3'
 old=(R/'src/rogue_dawn_host_floor_v4.s').read_text()
 new=once(old,'YPlus:\n lda Rh3\n clc\n adc RdRadiusY\n sta Rh3',
  'YPlus:\n lda Rh3\n clc\n adc RdRadiusY\n; Genuine E89F/E8CE scans [center-radius,center+radius), so a\n; resting bottom exactly on the floor never enters the next floor cell.\n sec\n sbc #1\n sta Rh3')
 new=once(new,'; leading edge+one at transverse -radius/0/+radius. Authenticated body radii',
  '; leading edge+one. Horizontal transverse endpoints are -radius/0/+radius-1;\n; vertical head/feet use the separately qualified native first-solid order. Body radii')
 leaf=R/'src/rogue_dawn_host_side_v1.s';leaf.write_text(new);O.mkdir(exist_ok=True)
 for name in['main.c','private.cfg']:(O/name).write_bytes((P/name).read_bytes())
 for name,a,z in [('body-source.s','$b5e3','$b5e6'),('lifecycle-source.s','$b7dd','$b7e0')]:
  (O/name).write_text(once((P/name).read_text(),a,z))
 (O/'entrypoint.s').write_text(once((P/'entrypoint.s').read_text(),'.include "rogue_dawn_host_floor_v4.s"','.include "rogue_dawn_host_side_v1.s"'))
 (O/'source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='df44/rogue_dawn_host_floor_v4.s',tofile='side-v1/rogue_dawn_host_side_v1.s')))
 previous=json.loads((P/'build.json').read_text());cmd=[z.replace(str(P),str(O))for z in previous['executed_commands'][-1]]
 # Main is rebuilt from actual full dependencies; inherited audio/weapon
 # objects retain their previously bound closure instead of cloning trees.
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(P)]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'build.log').write_text(z.stdout+z.stderr)
 assert z.returncode==0,(z.stdout+z.stderr)[-6000:]
 prepare(R,O/'candidate.nes');n=scoped_load(O/'candidate.nes')
 assert address(n,'RdCueGateEnd')==address(b,'RdCueGateEnd')+3<=0xbf00
 assert n['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32]==b['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32]
 assert n['raw'][16+1048576:]==b['raw'][16+1048576:]
 changes={}
 for i,(a,z)in enumerate(zip(b['raw'],n['raw'])):
  if a!=z:changes[str((i-16)//8192)]=changes.get(str((i-16)//8192),0)+1
 deps=dependencies(O/'assembler-full.dep')
 out=dict(passed=True,source_build_only=True,native_run=False,qualified=False,
  ROM=ref.binding(O/'candidate.nes'),parent=ref.binding(P/'candidate.nes'),executed_commands=[cmd],
  actual_ASM_incbin_inputs=len(deps),per_bank_delta=changes,A95_end=hex(address(n,'RdCueGateEnd')),
  A95_added_bytes=3,new_RAM_or_leases=False,
  bindings=[ref.binding(p)for p in dict.fromkeys(deps+[Path(__file__),leaf,P/'handoff.json',O/'private.cfg',O/'source.patch',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'candidate.map'])])
 (O/'build.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['ROM','per_bank_delta','A95_end','actual_ASM_incbin_inputs']},indent=2))
if __name__=='__main__':main()
