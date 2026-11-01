"""Prepare a small controller-only Hogan packet, reusing current read-only inputs."""
from pathlib import Path
import argparse,hashlib,json,sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint',type=Path,required=True)
    ap.add_argument('--expected',required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--frontend-only',action='store_true',help='Short diagnostic only; does not qualify the playable route.')
    args=ap.parse_args();j=args.joint.resolve();o=args.output.resolve()
    assert o.is_relative_to(R/'build')
    if o.exists():assert {p.name for p in o.iterdir()}<={'controller.lua','run.py','ready.json'},'Only an unrun preparation can be refreshed'
    assert sha(j/'candidate.nes')==args.expected
    b=scoped_load(j/'candidate.nes')
    template=R/'tools/reference/hogan_native_bounded_v1.lua'
    text=template.read_text(encoding='utf-8')
    point=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1
    assert b['raw'][location(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1]==0x60
    at=location(b,'WfIdleRecord');size=b['raw'][at]
    assert size>0 and size<=64 and size%4==0
    idle=[list(b['raw'][at+1+i:at+5+i])for i in range(0,size,4)]
    for row in idle:
        row[2]=row[2]-256 if row[2]>=128 else row[2]
        row[3]=row[3]-256 if row[3]>=128 else row[3]
    artpath=j/'hogan-body.chr'
    if not artpath.exists():artpath=R/'build/wwf-hogan-natural-source-v15/joint/hogan-body.chr'
    art=artpath.read_bytes()
    assert len(art)==17*1024
    assert b['raw'][1048592+546*1024:1048592+563*1024]==art
    args_lua=dict(sha256=args.expected,main_return=point,idle=idle,chr=list(art),frontend_only=args.frontend_only)
    names=['WfTagDone','WfHostReady','WfRenderBuffer','WfState','WfProxyValid','WfRawProxyCommit']
    prefix=''.join(f'L[{json.dumps(n)}]={address(b,n)}\n'for n in names)
    text='HOGAN_ARGS='+lua(args_lua)+'\n'+prefix+text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(text)
    assert ok,error
    o.mkdir(exist_ok=True)
    (o/'controller.lua').write_text(text,encoding='utf-8',newline='\n')
    (o/'run.py').write_text('''from pathlib import Path
import hashlib,json,os,subprocess,sys
O=Path(__file__).resolve().parent;R=next(p for p in O.parents if(p/'AGENTS.md').is_file())
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from run_mesen import run
q=json.loads((O/'ready.json').read_text())
for p,h in q['bindings'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
active=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \\\"Name like '%Mesen%'\\\" | Select-Object ProcessId,Name | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True).stdout.strip()
if active:print('Existing Mesen left alone: '+active);raise SystemExit(3)
os.environ['SMB_RUN_OUTPUT']=str(O/'capture')
result=run(O/'controller.lua',Path(q['ROM']),timeout=90,emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
for p,h in q['bindings'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
(O/'capture/binding.json').write_text(json.dumps(dict(ROM_sha256=q['ROM_sha256'],ready_sha256=hashlib.sha256((O/'ready.json').read_bytes()).hexdigest(),exit_code=result),indent=2)+'\\n')
raise SystemExit(result)
''',encoding='utf-8',newline='\n')
    refs=[Path(__file__),template,j/'candidate.nes',j/'candidate.lbl',j/'candidate.dbg',artpath,
          o/'controller.lua',o/'run.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',
          R/'tools/audit/build_storage_guard_v1.py',R/'tools/audit/run_bounded_build_v1.py']
    q=dict(prepared=True,native=False,frontend_only=args.frontend_only,ROM=str(j/'candidate.nes'),ROM_sha256=args.expected,
           run_byte_cap=128_000_000,max_files=64,max_PNGs=4,emulated_writes=False,
           bindings={str(p):sha(p)for p in refs})
    (o/'ready.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(prepared=True,ready=str(o/'ready.json'),bytes=sum(p.stat().st_size for p in o.iterdir()))))


if __name__=='__main__':main()
