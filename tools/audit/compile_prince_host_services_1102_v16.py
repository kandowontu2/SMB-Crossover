"""Measure actual native admission/clock/pit lifecycle in the owned tail."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
O=L.O


def main():
 grant=R/'docs/qa/allocations/prince-executable-state-1102-v15.json';g=json.loads(grant.read_text());assert g['granted']
 b=scoped_load(L.BASE);assert hashlib.sha256(b['raw']).hexdigest()==L.PIN
 names=['SelectedCharacter','OperMode','GameEngineSubroutine','GamePauseStatus','FrameCounter','Player_Y_Position','Player_Y_HighPos','R0','SafecallA_SMC','FarcallJmpTarget_SMC','NextBank_SMC','SafereturnA_SMC','FarCallCommon','KillPlayer']
 bindings={n:address(b,n)for n in names};life=L.P.T.labels(O/'host-life-v12.lbl')
 bindings.update({n:life[n]for n in ['PpHostInit','PpHostUpdate']});bindings['Bank_KillPlayer']=((location(b,'KillPlayer')-16)//8192)|128
 src=R/'tools/reference/prince_host_services_1102_v16.s';asm=O/'host-services-v16.s';asm.write_text(''.join(f'{n}=${a:04x}\n'for n,a in bindings.items())+src.read_text())
 cfg=O/'host-services-v16.cfg';cfg.write_text('MEMORY{M:start=$db9a,size=$198,file=%O;}SEGMENTS{SERVICES:load=M,type=ro,define=yes;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'host-services-v16.o'],[cc/'ld65.exe','-C',cfg,O/'host-services-v16.o','-o',O/'host-services-v16.bin','-Ln',O/'host-services-v16.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
 labels=L.P.T.labels(O/'host-services-v16.lbl');end=labels['PpNativeServicesEnd']
 q=dict(measured=True,base_ROM_SHA256=L.PIN,code_half_open=[0xdb9a,end],code_bytes=end-0xdb9a,remaining_tail_bytes=0xdd32-end,field_half_open=[0xc0a9,0xc0ad],native_emulator=False,host_ROM_created=False,auth_contract='Resident caller authenticates both full headers before code entry; private leaves additionally check raw38/ready/normal gameplay/pause/epoch.',unimplemented=['Original audio/special material/scene callbacks.','Native header/owner/resident cold descriptor and menu routing.','Native enemy damage/health/earned sword contacts.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),src,grant,O/'host-services-v16.bin',O/'host-life-v12.bin',L.BASE]})
 (O/'host-services-layout-v16.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
