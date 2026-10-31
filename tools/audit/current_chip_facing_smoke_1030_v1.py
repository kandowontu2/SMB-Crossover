"""Bounded native facing/menu smoke, expressly not a 1-1 clear attempt."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import current_character_route_1030_v4 as D
C=D.C


def source():
    old=(R/'tools/audit/current_ice_sparse_11_1030_v1.lua').read_text()
    s=old.replace('local nextMenuPoll=0','local nextMenuPoll=0\nlocal facingMenuReadyAt')
    needle="  identity();return pulse('start')"
    assert s.count(needle)==1
    s=s.replace(needle,"""  if not facingMenuReadyAt then facingMenuReadyAt=frame;return{}end
  if frame-facingMenuReadyAt<12 then return{}end
  identity();return pulse('start')""")
    needle='local endpoint=entered and c.world==0 and c.level==1 and scope()and control12>=25 and c.x>first12X+5'
    assert s.count(needle)==1
    s=s.replace(needle,"local endpoint=entered and scope()and loops>=220 and markers['facing-right']~=nil and markers['facing-left']~=nil")
    needle=""" if entered and(c.level==0 or endpoint or failure)then
  want('first-active',frame==menuReadyAt)
  want('corner-332',c.x>=332 and c.x<345)
  want('corner-345',c.x>=345 and c.x<360)
  want('corner-360',c.x>=360 and c.x<380)
  want('power-change',lastPower~=nil and c.status~=lastPower)
  want('flagpole',c.level==0 and c.x>=3120)
  want('endpoint',endpoint)
  want('failure',failure~=nil or frame>=C.limit)
 end"""
    assert s.count(needle)==1
    s=s.replace(needle,""" if not entered and facingMenuReadyAt and frame-facingMenuReadyAt>=8 then want('menu',true)end
 if entered then
  want('first-active',frame==menuReadyAt)
  want('facing-right',r('PlayerFacingDir')==1 and c.vx>0 and c.vx<128 and c.x>=100 and c.x<125)
  want('facing-left',r('PlayerFacingDir')==2 and c.vx>=128 and c.x>=124 and c.x<=140)
  want('endpoint',endpoint)
  want('failure',failure~=nil or frame>=C.limit)
 end""")
    s=s.replace("'cleared 1-1 and controlled 1-2'","'220 controlled updates; both sustained directions and actual menu captured'")
    s=s.replace("scope='Controller-only current1-1 to controlled1-2 with every original native state/OAM/CHR/interrupt check retained. At most8 selected PPU screens, not an every-frame pixel recording; no exhaustive items/abilities/source-fidelity/FPS claim.'",
        "scope='Controller-only menu and220 active updates in1-1; sustained right/left review captures. All original source/physical OAM, CHR, NMI/IRQ and zero-death assertions retained. NOT a1-1clear or all-abilities claim.'")
    return old,s


def prepare(a):
    old,new=source()
    script=R/'build/current-chip-facing-smoke-1030-v1.lua'
    if script.exists():assert script.read_text()==new
    else:script.write_text(new)
    C.navigation=D.navigation
    C.SCRIPT=script
    C.MARKERS=['menu','first-active','facing-right','facing-left','endpoint','failure']
    a.replay=None;a.frames=1200
    a.policy=R/'tools/playthroughs/current_chip_facing_1030_v2.lua'
    C.prepare(a)
    q=a.output.resolve()/'ready.json'
    ready=json.loads(q.read_text())
    ready.update(explicit_endpoint='220 actual GameLoop updates, both sustained-direction PPU captures and actual cold menu; no1-1clear requirement or claim.',
        current_policy_status='Bounded facing smoke; full route failure retained independently.')
    q.write_text(json.dumps(ready,indent=2)+'\n')
    h=dict(prepared=True,native=False,ROM=str(a.rom.resolve()),ROM_sha256=a.expected_sha256,
        ready=str(q),ready_sha256=D.sha(q),script=str(q.parent/'run.lua'),
        emulator='C:/Mesen2/Mesen.exe',emulator_timeout_seconds=45,process_timeout_seconds=60,
        maximum_emulated_frames=1200,maximum_selected_frames=6,capture_bytes=536870912,capture_files=64,
        scope=ready['explicit_endpoint'],
        settings=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros',
                  '--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'],
        bindings=ready['bindings']|{str(Path(__file__).resolve()):D.sha(__file__)},
        observer_changes='Menu12-frame input hold+menu screen; sustained direction capture thresholds;220-update endpoint/scope. All native state/OAM/CHR/interrupt assertions preserved.')
    p=q.with_name('native-facing-smoke-packet.json');assert not p.exists()
    p.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps(dict(packet=str(p),sha256=D.sha(p))))


def run(a):
    p=a.packet.resolve();h=json.loads(p.read_text())
    assert h['prepared'] and not h['native'] and h['emulator_timeout_seconds']==45 and h['process_timeout_seconds']==60
    assert D.sha(h['ROM'])==h['ROM_sha256'] and D.sha(h['ready'])==h['ready_sha256']
    assert all(D.sha(f)==v for f,v in h['bindings'].items())
    assert not (p.parent/'native-launch.json').exists(),'One root-granted run; no automatic retry'
    active=subprocess.run(['powershell','-NoProfile','-Command',
        'Get-CimInstance Win32_Process -Filter "Name=\'Mesen.exe\'" | Select-Object -ExpandProperty ProcessId'],capture_output=True,text=True,check=True).stdout.strip()
    assert not active,'Existing Mesen is live'
    import audit.capture_budget as B
    import run_mesen as M
    assert M.run.__globals__['run_capped'] is B.run_capped
    B.RUN_BYTES=h['capture_bytes'];B.PAYLOAD_BYTES=B.RUN_BYTES-1000000
    old=B.preflight;B.preflight=lambda output:old(output,reserved_bytes=B.RUN_BYTES,reserved_files=64)
    os.environ['SMB_RUN_OUTPUT']=str(p.parent)
    (p.parent/'native-launch.json').write_text(json.dumps(dict(packet_sha256=D.sha(p),automatic_retries=False,no_existing_Mesen=True),indent=2)+'\n')
    return M.run(Path(h['script']),Path(h['ROM']),h['emulator'],45,emulator_options=h['settings'])


def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='action',required=True)
    p=sub.add_parser('prepare')
    p.add_argument('--identity',choices=['chip','dale'],required=True)
    p.add_argument('--mode',choices=['easy','hard'],default='easy')
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('run');p.add_argument('--packet',type=Path,required=True)
    a=ap.parse_args();return prepare(a) if a.action=='prepare' else run(a)


if __name__=='__main__':raise SystemExit(main())
