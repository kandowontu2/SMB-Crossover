"""Capture the actual first-freeze state while retaining the failing expectation."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-current-f-samus-passives-bc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=H/'probe-c-result.json';assert not out.exists();src=H/'probe-c';src.mkdir()
    s=(H/'source-b/passives.lua').read_text();needle="   assert(timer>=350 and timer<=360"
    assert s.count(needle)==1
    injected="""   local record={frame=frame,timer=timer,hpLo=r('MmEnemyHealthLo'),hpHi=r('MmEnemyHealthHi'),flag=r('Enemy_Flag'),id=r('Enemy_ID'),estate=r('Enemy_State'),behavior=r('CrossoverBehaviorVersion'),selected=r('SelectedCharacter'),owned=r('InvOwnedLo',2)}
   local d=assert(io.open(OUTPUT..'first-freeze.json','w'));d:write('{');local comma='';for k,v in pairs(record)do d:write(comma..string.format('%q',k)..':'..v);comma=','end;d:write('}\\n');d:close()
   local raw={};for a=0,2047 do raw[#raw+1]=string.char(emu.read(a,emu.memType.nesDebug))end;for a=0x6000,0x7fff do raw[#raw+1]=string.char(emu.read(a,emu.memType.nesDebug))end
   local d=assert(io.open(OUTPUT..'first-freeze.ram','wb'));d:write(table.concat(raw));d:close()
"""
    body=src/'passives.lua';body.write_text(s.replace(needle,injected+needle))
    wrapper=src/'run.lua';wrapper.write_text('dofile('+json.dumps((R/'tests/menu-bootstrap.lua').as_posix())+')\ndofile('+json.dumps(body.as_posix())+')\n')
    o=H/'probe-c-mmc3';o.mkdir();rom=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/smb-crossover-mmc3.nes'
    q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(o),str(wrapper),str(rom),'--timeout','60'],cwd=R,capture_output=True,text=True)
    log=H/'probe-c-host.log';log.write_text(q.stdout+q.stderr)
    r=dict(exit=q.returncode,script_sha256=sha(__file__),body_sha256=sha(body),host_log_sha256=sha(log),observation=json.loads((o/'first-freeze.json').read_text())if(o/'first-freeze.json').exists()else None,
      files={p.name:sha(p)for p in o.iterdir()if p.is_file()},scope='Exact source-B expectations retained; passive observation only before the failing assertion. No shared fixture/runtime modification.',goal_complete=False)
    out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
