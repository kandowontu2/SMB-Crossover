"""Link genuine Thomas source and bounded real-native host boundary APIs."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
import thomas_original_cpu_1031_v1 as T
P=R/'build/thomas-host-scratch-1031-v1';J=R/'build/contra-force-world-roles-1031-v2/joint'
O=R/'build/thomas-host-boundary-1031-v2';A=R/'tools/reference/thomas_host_boundary_1031_v1.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();(O/'source').mkdir(parents=True)
 stage=json.loads((P/'source-stage.json').read_text())
 for p,h in stage['bindings'].items():assert sha(p)==h,p
 b=qualified(J/'candidate.nes')
 for n in ['component','dependencies']:
  shutil.copyfile(P/f'source/{n}.s',O/f'source/{n}.s')
 shutil.copyfile(A,O/'source/host.s');shutil.copyfile(P/'source/component.cfg',O/'source/component.cfg')
 imports={};src=(O/'source/host.s').read_text()
 for kind,names in re.findall(r'\.(importzp|import) ([^\n;]+)',src):
  for name in names.split(','):
   name=name.strip()
   if name.startswith('Bank_'):
    target=name[5:];imports[name]=dict(value=((location(b,target)-16)//8192)|128,kind='import',target=target)
   elif name in T.labels(P/'component.lbl')or name.startswith('ThHost'):continue
   else:imports[name]=dict(value=address(b,name),kind=kind)
 for i in range(8):imports['R'+str(i)]=dict(value=address(b,'R'+str(i)),kind='importzp')
 text='; Exact current host imported binding object for isolated source/CPU arena.\n'
 for name,v in sorted(imports.items()):text+=f'.export'+('zp'if v['kind']=='importzp'else'')+f' {name}\n{name}=${v["value"]:04X}\n'
 (O/'source/host-imports.s').write_text(text,encoding='utf-8');dump(O/'host-imports.json',imports)
 cc=R/'tools/Windows/cc65/bin';commands=[]
 def run(cmd):
  g=validate(cmd,O,cwd=O);p=subprocess.run(list(map(str,cmd)),cwd=O,capture_output=True,text=True)
  commands.append(dict(command=list(map(str,cmd)),guard=g,returncode=p.returncode,stderr=p.stderr));assert not p.returncode,p.stderr
 names=['component','dependencies','host','host-imports']
 for n in names:run([cc/'ca65.exe',O/f'source/{n}.s','-g','-o',O/f'{n}.o','-l',O/f'{n}.lst','--create-full-dep',O/f'{n}.dep'])
 run([cc/'ld65.exe','-C',O/'source/component.cfg',*[O/f'{n}.o'for n in names],'-o',O/'component.bin','--dbgfile',O/'component.dbg','-Ln',O/'component.lbl','-m',O/'component.map'])
 dump(O/'build-commands.json',commands);s=T.labels(O/'component.lbl');n=s['ThomasHostBoundaryEnd']-0xa000
 assert(P/'component.bin').read_bytes()[:3986]==(O/'component.bin').read_bytes()[:3986]
 dump(O/'source-stage.json',dict(result='SOURCE_LINKED_NATIVE_BOUNDARY_NOT_HOOKED',native=False,host_ROM_unchanged=True,parent_source=sha(P/'source-stage.json'),
  code_origin=0xa000,emitted_bytes=n,original_corrected_kernel_3986_bytes_exact=True,host_boundary_bytes=n-3986,
  selected_state_bytes=0x838,physical_scratch=list(range(3,11)),
  terrain_contract='Original integrator -> HostFrame exports -> genuine native terrain phase -> AfterTerrain rebases plane. Native query leaves retain real outputABI; Queries only records metatiles and does not claim support or progression.',
  progression='Weapons uses real original C65B and C0F3 inclusive AABB then native HandleEnemyFBallCol once. Damage sourceX6 exact; Pickup true native MarioSourcePowerupCollision.',
  deferred=['Full natural current-host row/hook/lifecycle integration','Fall/ceiling/source-air reconciliation and legal pose/body collision profile','Physical sparse loader/fullcookie/epoch authentication and selected-owner retirement','Real CHR/OAM/palette publisher and original audio NMI ownership'],
  bindings={str(p):sha(p)for p in [Path(__file__),A,P/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',R/'tools/audit/private_build_outputs_v1.py']+[p for p in O.rglob('*')if p.is_file()]}))
 print(json.dumps(dict(result='SOURCE_LINKED',bytes=n,boundary_bytes=n-3986,stage_sha256=sha(O/'source-stage.json'))))
if __name__=='__main__':main()
