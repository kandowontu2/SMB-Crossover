"""Private source-faithful downward floor successor on frozen69a; no native."""
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
O=R/'build/rogue-dawn-floor-v1'
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
 new=once(old,'Down:\n lda Rh3\n clc\n adc RdRadiusY\n clc\n adc #1\n sta Rh3',
  '; Original E4A3/E7AD tests CURRENT aligned bottom, before the next pixel.\n; Testing bottom+1 prevents the final alignment pixel and repeatedly rearms\n; gravity before the source running handler can reach its jump/idle checks.\nDown:\n lda Rh3\n clc\n adc RdRadiusY\n sta Rh3')
 # Original E4E9/E4EC commits one downward pixel then decrements the signed
 # jump-distance accumulator, the inverse of genuine E49B/E49E upward motion.
 new=once(new,'MoveDown:\n inc RdY\n bne Clear\n inc Player_Y_HighPos\nClear:',
  'MoveDown:\n inc RdY\n bne :+\n inc Player_Y_HighPos\n:\n dec RdJumpDistance\nClear:')
 leaf=R/'src/rogue_dawn_host_floor_v1.s';leaf.write_text(new)
 O.mkdir(exist_ok=True)
 for n in ['main.c','private.cfg']:(O/n).write_bytes((P/n).read_bytes())
 entry=once((P/'entrypoint.s').read_text(),'.include "services-include.s"',
  '.include "rogue_dawn_host_floor_v1.s"')
 (O/'entrypoint.s').write_text(entry)
 patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
  fromfile='69a/services-include.s',tofile='floor-v1/rogue_dawn_host_floor_v1.s'))
 (O/'source.patch').write_text(patch)
 previous=json.loads((P/'build.json').read_text())
 cmd=[z.replace(str(P),str(O))for z in previous['executed_commands'][-1]]
 for i,z in enumerate(cmd):
  if z==str(O/'audio0.o'):cmd[i]=str(P/'audio0.o')
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(P)]
 k=cmd.index('--asm-include-dir');cmd[k:k]=['--asm-include-dir',str(O)]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
 (O/'build.log').write_text(z.stdout+z.stderr)
 assert z.returncode==0,(z.stdout+z.stderr)[-6000:]
 prepare(R,O/'candidate.nes');n=scoped_load(O/'candidate.nes')
 assert address(n,'RdHsServicesEnd')==address(b,'RdHsServicesEnd')
 assert address(n,'RdCueGateEnd')==address(b,'RdCueGateEnd')
 assert n['raw'][16+1048576:]==b['raw'][16+1048576:]
 changes={}
 for i,(a,z)in enumerate(zip(b['raw'],n['raw'])):
  if a!=z:changes[str((i-16)//8192)]=changes.get(str((i-16)//8192),0)+1
 assert set(changes)=={'95'},changes
 deps=dependencies(O/'assembler-full.dep')
 out=dict(passed=True,source_build_only=True,native_run=False,qualified=False,
  ROM=ref.binding(O/'candidate.nes'),parent=ref.binding(P/'candidate.nes'),
  executed_commands=[cmd],actual_ASM_incbin_inputs=len(deps),per_bank_delta=changes,
  A95_end=hex(address(n,'RdCueGateEnd')),new_RAM_or_leases=False,
  exact_preserved='All original compiled public endpoints outside the interior geometry path; whole CHR, source driver/readers/depot, fixed deathBF00, world block transaction/native guards exact.',
  bindings=[ref.binding(p)for p in dict.fromkeys(deps+[Path(__file__),leaf,P/'handoff.json',
   O/'private.cfg',O/'source.patch',P/'audio0.o',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'candidate.map'])])
 (O/'build.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in ['ROM','per_bank_delta','A95_end','actual_ASM_incbin_inputs']},indent=2))
if __name__=='__main__':main()
