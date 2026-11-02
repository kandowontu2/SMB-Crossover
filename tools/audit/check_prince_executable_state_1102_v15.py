"""Nonzero code-state + real renderer/IRQ source-reader amendment proof."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import compile_prince_host_lifecycle_1102_v12 as L
O=L.O


def main():
 core=json.loads((O/'contact-recovery.json').read_text())['instructions'];coords=json.loads((O/'world-coordinate-recovery-v7.json').read_text())['instructions'];graph={**core,**coords}
 slots=[(0xb0,0xf8),(0x100,0x200),(0x235,0x352),(0x362,0x3ff),(0x40b,0x491),(0x4ff,0x606)];fields=(0x78,0xb0);operands=[];indirect=[]
 for at,v in graph.items():
  mode=v['mode'];value=v['value'];mn=v['mn']
  if mn in ['JSR','JMP']and mode!='ind':continue
  if mode in ['abs','zpg','abx','aby','zpx','zpy']and value<2048:
   high=value+(256 if mode in ['abx','aby','zpx','zpy']else 1)
   assert not any(value<end and high>start for start,end in slots+[fields]),(at,v)
   operands.append([at,mn,value,high])
  if mode in ['iny','inx','ind']:
   assert(mn,mode,value)in [('LDA','iny',0x21),('JMP','ind',0x23)]
   indirect.append([at,mn,mode,value])
 p=R/'tools/audit/check_prince_host_render_1102_v1.py';text=p.read_text()
 changes={"ROM=R/'build/excitebike-pose-1101-v3/current4.nes'":"ROM=R/'build/wwf-death-1102-v2/candidate.nes'","SHA='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'":"SHA='"+L.PIN+"'","src=R/'tools/reference/prince_host_render_1102_v1.s'":"src=O/'host-render-compact-v11.s'","'host-render":"'state-render-v15","prince-pose-packets.bin":"prince-pose-packets-v11.bin","geometry={0x4bc,0x4c3,0x6f1,0x70f}":"geometry={0x88,0x4bc,0x4c3,0x6f1,0x70f}","g=pose['source_projection_geometry'];assert":"g=pose['source_projection_geometry'];assert m[0xc088]==g['native_06F1_minus_anchor_y'];assert","m=M.fork(seed);m.ram[3]":"m=M.fork(seed);runtime=(O/'host-runtime-v12.bin').read_bytes();statecode=(O/'host-state-code-v12.bin').read_bytes();m.ram[3][:len(runtime)]=runtime;m.ram[2][0xb0:0xb0+len(statecode)]=statecode;m.ram[3]","GuestOamRotationActive=int(bool(rotation)),":"SelectedCharacter=38,GuestOamRotationActive=int(bool(rotation)),","injected=True;regs=":"injected=True;ram_write_start=len(m.ram_writes);regs=","assert regs==(c.a,c.x,c.y,c.p,c.sp,c.pc)":"assert not any(bank in [2,3]for bank,at,value in m.ram_writes[ram_write_start:]),('ISR wrote source/code even if value unchanged',interrupt)\n    assert regs==(c.a,c.x,c.y,c.p,c.sp,c.pc)"}
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 text=text.replace('state-render-v15-compact-v11.s','host-render-compact-v11.s')
 env=dict(__file__=str(p),__name__='prince_nonzero_executable_state');exec(compile(text,str(p),'exec'),env);env['main']()
 render=O/'state-render-v15-CPU.json';proof=json.loads(render.read_text());assert proof['passed']
 q=dict(passed=True,private_proposal_only=True,state_amendment_granted=False,ROM_written=False,base_ROM_SHA256=L.PIN,proposed_original_state_code_half_open=[[0xc000+a,0xc000+z]for a,z in slots],owned_geometry_fields_half_open=[0xc078,0xc0b0],native_packet_half_open=[0xc200,0xc235],source_instruction_boundaries=len(graph),all_source_direct_indexed_reader_writer_domains=len(operands),indexed_operands_expand_all256_values=True,indirect_operands=indirect,indirect_closure='LDA(21),Y is translated by the private script reader to the immutable authenticated original-script section; JMP(23) contains translated command entrypoints. Original actor/script closure and all15commands were independently donor-qualified. Native rendering reads only bounded408pose packets, now C800..DB9A; no packet can read DB9A..DD32.',original_source_cannot_read_or_write_proposed_slots_or_fields=True,metadata_bytes=5018,metadata_half_open=[0xc800,0xdb9a],possible_owned_metadata_tail_half_open=[0xdb9a,0xdd32],possible_metadata_tail_bytes=408,tail_execution_not_yet_granted=True,actual_nonzero_runtime_and_state_code_present_during_ISR=True,actual_native_render_pose_pairs=proof['source_facing_poses'],actual_native_edge_cases=proof['edge_capacity_alignment_cases'],actual_IRQ_lagNMI_cuts=proof['actual_IRQ_lagNMI_instruction_SP_cuts'],no_IRQ_or_lagNMI_writes_to_RAM2_or_RAM3_even_same_value=True,cold_constructor='Actual60B RAM3 finalizer copies C100..C65F down to C0B0..C60F, zeros C000..C0B0 and C60F..C800, then calls original14B actor template/native spawn constructor. Thus every genuine source byte is zero or explicitly initialized before live actor/auth; executable source-dead slots are already installed.',clock_contract='Current private v12 root requires one call per native Main epoch. Actual native game.s increments FrameCounter once before OperModeExecutionTree, and freezes it while paused. A separate owned admission shim checking OperMode1/engine8/pause/FrameCounter duplicate is still required before native binding; no shared DFD0..DFD2 changes.',remaining=['Root review/amendment of the exact source-dead executable state slots and conditional geometry fields.','Clock/scene/owner admission shim and remaining audio/endScene/material callbacks remain separate; no native ROM execution is authorized by this receipt alone.'],bindings={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [Path(__file__),L.BASE,O/'contact-recovery.json',O/'world-coordinate-recovery-v7.json',O/'host-life-CPU-v12.json',O/'host-storage-v12.json',render,O/'host-runtime-v12.bin',O/'host-state-code-v12.bin',R/'src/game.s']})
 (O/'executable-state-proposal-v15.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','indirect_operands','actual_IRQ_lagNMI_cuts']}))


if __name__=='__main__':main()
