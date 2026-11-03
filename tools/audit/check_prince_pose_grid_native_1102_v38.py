"""Actual613b CHR/emitter/IRQ proof for the lossless grid successor."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
import prepare_prince_successor_manifest_1102_v26 as PM
O=A.O


def main():
 proof=json.loads((O/'pose-grid-CPU-v37.json').read_text());assert proof['passed'];base,_,_,_=PM.bundle()
 original=R/'tools/audit/check_prince_host_render_1102_v1.py';text=original.read_text()
 # Extra private exports establish every mutable helper byte without
 # changing its code, metadata, renderer, or public labels.
 hs=(O/'pose-grid-helper-v37.s').read_text()+'\n.export IndexLo,IndexHi\n';blob,hl=A.assemble('grid-helper-labels-v38',hs,(O/'pose-grid-helper-v37.cfg').read_text());assert blob==(O/'pose-grid-helper-v37.bin').read_bytes()
 mutable=[hl[n]for n in ['PpGridFlag','PpGridBaseX','PpGridBaseY','PpGridCell']]+[hl[n]+2 for n in ['IndexLo','IndexHi']]
 start=proof['proposed_reclaimed_metadata_helper_half_open'][0]
 begin=text.index(" src=R/'tools/reference/prince_host_render_1102_v1.s'");end=text.index(' costs=[]',begin)
 text=text[:begin]+''' src=R/'tools/audit/prepare_prince_pose_grid_1102_v37.py'
 blob=(O/'grid-render-v37.bin').read_bytes();lab=GRID_LABELS;relaxed=[]
 art=json.loads((O/'source-art.json').read_text());meta=(O/'prince-pose-grid-v37.bin').read_bytes()
'''+text[end:]
 changes={
  "assert A.sha(ROM)==SHA;b=A.scoped_load(ROM);seed=M.fresh(b)":"assert A.sha(ROM)==SHA;b=PROVIDED_BASE;seed=M.fresh(b)",
  "ROM=R/'build/excitebike-pose-1101-v3/current4.nes'":"ROM=R/'build/bub-menu-candidate-1102-v2/combined-event.nes'",
  "SHA='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'":"SHA='"+PM.A.PIN+"'",
  'm.ram[2][0x800:0x800+len(meta)]=meta':'m.ram[2][0x800:0x800+len(meta)]=meta;m.ram[2][GRID_START-0xc000:GRID_START-0xc000+len(GRID_HELPER)]=GRID_HELPER',
  'GuestOamRotationActive=int(bool(rotation)),':'SelectedCharacter=38,GuestOamRotationActive=int(bool(rotation)),',
  'geometry={0x4bc,0x4c3,0x6f1,0x70f}':'geometry={0x88,0x4bc,0x4c3,0x6f1,0x70f}|{at-0xc000 for at in GRID_MUTABLE}',
  "g=pose['source_projection_geometry'];assert":"g=pose['source_projection_geometry'];assert m[0xc088]==g['native_06F1_minus_anchor_y'];assert",
  'injected=True;regs=':'injected=True;writes_before=len(m.ram_writes);regs=',
  'assert regs==(c.a,c.x,c.y,c.p,c.sp,c.pc)':"assert not any(bank in [2,3]for bank,at,value in m.ram_writes[writes_before:]),('Grid ISR private write',interrupt)\n    assert regs==(c.a,c.x,c.y,c.p,c.sp,c.pc)",
  "O/'host-render-CPU.json'":"O/'pose-grid-native-CPU-v38.json'",
  'distinct_reached_instruction_SP_cuts=len(cuts)':'distinct_reached_instruction_SP_cuts=len(all_format_cuts),format_cut_counts=format_cut_counts',
 }
 for a,z in changes.items():assert a in text,a;text=text.replace(a,z)
 # Retain the full original emitter/edge assertions. Exercise real ISR
 # cuts for both formats, including their different helper return paths.
 old=""" m,c,cuts=draw(widest);ISRcases=0;by={}
 for kind in ['IRQ','lagNMI']:
  for cut in sorted(cuts):draw(widest,interrupt=(kind,cut));ISRcases+=1;by[kind]=by.get(kind,0)+1
"""
 new=""" formats=[]
 for packed in [False,True]:
  poses=[p for p in art['poses']if bool(int.from_bytes(meta[p['source_frame']*2:p['source_frame']*2+2],'little')&32768)==packed]
  formats.append(max(poses,key=lambda p:(len({v['pattern_pair']//32 for v in p['parts_8x16']}),len(p['parts_8x16']))))
 ISRcases=0;by={};all_format_cuts=set();format_cut_counts=[]
 for pose in formats:
  m,c,cuts=draw(pose)
  all_format_cuts.update(cuts);format_cut_counts.append(dict(frame=pose['source_frame'],cuts=len(cuts)))
  for kind in ['IRQ','lagNMI']:
   for cut in sorted(cuts):draw(pose,interrupt=(kind,cut));ISRcases+=1;by[kind]=by.get(kind,0)+1
 m,c,cuts=draw(widest)
"""
 assert old in text;text=text.replace(old,new)
 env=dict(__file__=str(original),__name__='prince_grid_actual_native_fixture',PROVIDED_BASE=base,GRID_LABELS=A.L.P.T.labels(O/'grid-render-labels-v37.lbl'),GRID_START=start,GRID_HELPER=blob,GRID_MUTABLE=mutable)
 exec(compile(text,str(original),'exec'),env)
 with contextlib.redirect_stdout(io.StringIO()):env['main']()
 file=O/'pose-grid-native-CPU-v38.json';q=json.loads(file.read_text());assert q['passed']
 # The original independent-renderer fixture's geometric tail is already
 # occupied by world/material/finalizer in the actual full image.
 q['geometric_bytes_after_renderer']=q.pop('remaining_before_BFE0')
 q['actual_full_RAM3_spare']=1;q['renderer_plus_grid_helper_bytes']=545+len(blob)
 q.update(proposal_only=True,new_executable_metadata_grant=False,all_private_code_public_addresses_unchanged=True,old_renderer_length=545,new_renderer_length=545,grid_helper_half_open=[start,start+len(blob)],grid_helper_mutable_absolute_bytes=mutable,metadata_saved=681,helper_bytes=len(blob),net_reclaimed_live_bytes=681-len(blob),source_original_all2578parts_and_geometry_exact=True,real_ISR_formats=['raw irregular sword','8px body grid'],qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),scope='Exact613b native CHR setters and metasprite emitter,408sourcefaceposes, edge/OAMcapacity/wrap cases and real IRQ/lagNMI cuts across BOTH raw/grid formats. Full owned state/context preserved; zero ISR private writes including same-value. 681B original coordinate redundancy reclaimed with114B decoder; no art/geometry/publiccodeaddress change. New metadata executable interval still requires root amendment, no ROM/menu/install/native gameplay qualification.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'pose-grid-CPU-v37.json',O/'grid-render-v37.bin',O/'pose-grid-helper-v37.bin',O/'prince-pose-grid-v37.bin',PM.A.BASE]})
 file.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','source_facing_poses','edge_capacity_alignment_cases','actual_IRQ_lagNMI_instruction_SP_cuts','metadata_saved','helper_bytes','net_reclaimed_live_bytes','CPU','minimum_SP']}))


if __name__=='__main__':main()
