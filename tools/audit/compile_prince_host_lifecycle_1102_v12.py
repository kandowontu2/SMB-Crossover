"""Private runtime fit for source world, projection and actual native exports."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import recover_prince_core_1101_v1 as B
import check_hogan_current_bounded_v1 as N
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from private_build_outputs_v1 import validate
P,O=B.P,B.O
BASE=R/'build/wwf-death-1102-v2/candidate.nes'
PIN='1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'


def main():
 assert hashlib.sha256(BASE.read_bytes()).hexdigest()==PIN;b=scoped_load(BASE)
 co=P.T.labels(O/'world-coordinates-v7.lbl');point=P.T.labels(O/'contact-point.lbl');core=P.T.labels(O/'contact-core.lbl');render=P.T.labels(O/'host-render-v11.lbl')
 bindings=dict(SourceWorldContext=co['PpWorldContext'],SourceWorldColumn=co['PpWorldColumn'],SourceWorldPrivateMap=co['PpWorldPrivateMap'])
 bindings.update({n:point[n]for n in ['PpQueryX','PpQueryY','PpHostReadPoint']})
 bindings.update({n:core[n]for n in ['PpAdvanceActor','PpControls','PpFall','PpTerrainContact']})
 bindings.update({n:render[n]for n in ['PpHostProject','PpRenderX','PpRenderY']})
 for n in ['GameEngineSubroutine','Player_Y_Position','Player_Y_HighPos','Player_X_Position','Player_PageLoc','SavedJoypad1Bits','Player_X_Scroll','Player_X_Speed','Player_State','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_Pos_ForScroll']:bindings[n]=address(b,n)
 world=R/'tools/reference/prince_host_world_1102_v8.s';life=R/'tools/reference/prince_host_lifecycle_1102_v12.s'
 text=''.join(f'{n}=${v:04x}\n'for n,v in bindings.items())+world.read_text()+life.read_text()
 asm=O/'host-life-v12.s';asm.write_text(text);cfg=O/'host-life-v12.cfg'
 renderend=json.loads((O/'host-render-v11-CPU.json').read_text())['code_half_open'][1]
 materialend=renderend+449
 slots={'WORLD_EXTRA':(co['PpWorldCoordinateEnd'],0xc360-co['PpWorldCoordinateEnd']),'WORLD_GEOMETRY':(0xc4ff,0x110),'WORLD_MATERIAL':(renderend,449),'WORLD_ALIGN':(0xc40b,0xa6),'WORLD_LANDING':(0xc362,0x21),'LIFE_INIT':(0xc0b0,0x50),'LIFE_PHASE':(0xb36e,0x92),'LIFE_EXPORT':(0xc383,0x7e),'LIFE_COLD':(materialend,0xbfe0-materialend)}
 cfg.write_text('MEMORY{'+''.join(f'M{i}:start=${a:04x},size=${size:x},file=%O;'for i,(a,size)in enumerate(slots.values()))+'}SEGMENTS{'+''.join(f'{n}:load=M{i},type=ro,define=yes;'for i,n in enumerate(slots))+'}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'host-life-v12.o'],[cc/'ld65.exe','-C',cfg,O/'host-life-v12.o','-o',O/'host-life-v12.bin','-Ln',O/'host-life-v12.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 labels=P.T.labels(O/'host-life-v12.lbl');offset=0;regions=[]
 for n,(a,size)in slots.items():
  used=labels[f'__{n}_SIZE__'];regions.append(dict(segment=n,half_open=[a,a+used],source_file_offset=offset,bytes=used,remaining=size-used));offset+=used
 q=dict(measured=True,qualified=False,private_proposal_only=True,host_ROM_created=False,base_ROM_SHA256=PIN,code_bytes=offset,regions=regions,owned_geometry_fields_half_open=[0xc078,0xc0a9],constructor_original_bank2_ABBF_hex='80a0008000db96ff000000000000',normal_gameplay_only=True,sword_component_in_live_image=False,sword_component_preserved_separately=True,remaining=['Actual owner/cold/auth/scene epoch admission is not implemented or assumed.','Original audio/scene/trap/potion/sword callbacks remain explicit fixture boundaries.','Update executes original0advance+projection/1empty/3controls/4fall+terrain in separate native epochs; no all-roots60Hz approximation.','RAM2 executable slots are proposed only within existing exclusive grant, pending complete constructor/clock/reader/writer closure.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),world,life,O/'host-life-v12.bin',O/'world-coordinates-v7.bin',O/'host-render-v11.bin',R/'docs/qa/allocations/roster-rebase-1102-v4.json']})
 (O/'host-life-layout-v12.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','remaining']}))


if __name__=='__main__':main()
