"""Exercise the production Win32 scanner with raised-cap and retained boundary fixtures."""
from pathlib import Path
import ctypes
import hashlib
import json
import os
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'build/verification/capture-budget-guard-proposal'
OUT=ROOT/'build/verification/root49-capture-raised-cap-ax/native-controls-az'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PRODUCTION=ROOT/'tools/playthroughs/capture_segments.c'
assert sha(BASE/'host_driver.c')=='cc9daadf90837a2d7f66b3e630ed5667110db5f30b377b93e56396f39f6a147f'
OUT.mkdir(exist_ok=False)
shutil.copyfile(PRODUCTION,OUT/'capture_segments.proposed.c')
shutil.copyfile(BASE/'host_driver.c',OUT/'host_driver.c')
build=subprocess.run(['gcc','-O2','-Wall','-Wextra','-Wno-cast-function-type','-o',str(OUT/'host_driver.exe'),str(OUT/'host_driver.c')],capture_output=True,text=True)
(OUT/'compile.log').write_text(build.stdout+build.stderr)
assert build.returncode==0,build.stderr
R=262144+8192+536870912
assert R==537141248
report=dict(result='running',driver_sha256=sha(OUT/'host_driver.exe'),production_c_sha256=sha(PRODUCTION),cases=[],limitations=['No available UNC test share; no public-recorder Unicode-path claim. Host API stubs only, not emulation/capture evidence.'])
rp=OUT/'report.json'
def save():rp.write_text(json.dumps(report,indent=2)+'\n')
save()
guard=('SMB_CAPTURE_WORKSPACE','SMB_CAPTURE_CAP_BYTES','SMB_CAPTURE_SEGMENT_FRAMES','SMB_CAPTURE_FRAME_LIMIT')

def case(tag,setup=None,values=None,expect='allow',used=None,reason=None,action='start',disabled=False):
    folder=OUT/'fixtures'/tag;root=folder/'workspace';dest=root/'segments'
    dest.mkdir(parents=True)
    env={k:v for k,v in os.environ.items()if not k.startswith(('SMB_CAPTURE_','HOST_CAPTURE_'))}
    env.update(SMB_CAPTURE_SEGMENT_DIR=str(dest))
    if not disabled:env.update(SMB_CAPTURE_WORKSPACE=str(root),SMB_CAPTURE_CAP_BYTES=str(R+10000),SMB_CAPTURE_SEGMENT_FRAMES='1',SMB_CAPTURE_FRAME_LIMIT='1')
    cleanup=setup(root,dest,env)if setup else None
    for k,v in (values or {}).items():
        if v is None:env.pop(k,None)
        else:env[k]=str(v)
    protected={p:sha(p)for p in folder.rglob('*')if p.is_file()and p.name!='capture-budget-stop.json'}
    try:run=subprocess.run([str(OUT/'host_driver.exe'),action],env=env,capture_output=True)
    finally:
        if cleanup:cleanup()
    (folder/'stdout.bin').write_bytes(run.stdout);(folder/'stderr.bin').write_bytes(run.stderr)
    stderr=run.stderr.decode(errors='replace')
    marker=Path(env['SMB_CAPTURE_SEGMENT_DIR'])/'capture-budget-stop.json'
    payload=json.loads(run.stdout)if run.stdout else None
    if expect=='abort':
        assert run.returncode==86 and b'HOST AviStop'in run.stderr and b'HOST WaveStop'in run.stderr and b'HOST AviRecord'not in run.stderr,(tag,run.returncode,stderr)
    elif expect=='deny':
        assert run.returncode==0 and payload['recordCalls']==0 and payload['blocked']==1 and payload['waveStops']==1,(tag,payload,stderr)
        assert marker.is_file(),tag
        info=json.loads(marker.read_text())
        if used is not None:assert info['usedBytes']==used,(tag,info,used)
        if reason:assert info['reason']==reason,(tag,info)
    else:
        assert run.returncode==0 and payload['recordCalls']==1 and payload['blocked']==0 and not marker.exists(),(tag,payload,stderr)
        if disabled:assert payload['findFirstCalls']==0 and payload['aviStops']==0
    for p,h in protected.items():
        if 'stop-growth'not in str(p):assert sha(p)==h,(tag,p)
    report['cases'].append(dict(tag=tag,expect=expect,exit=run.returncode,counters=payload,
        marker=marker.read_text()if marker.is_file()else None,stdout_sha256=sha(folder/'stdout.bin'),stderr_sha256=sha(folder/'stderr.bin')))
    save()

case('disabled',disabled=True)
case('disabled-faults',disabled=True,values={'HOST_CAPTURE_SCAN_ERROR':'1','HOST_CAPTURE_MARKER_ERROR':'1'})
case('empty-exact',values={'SMB_CAPTURE_CAP_BYTES':R})
case('three-exact',setup=lambda r,d,e:(r/'retained.avi').write_bytes(b'abc')and None,values={'SMB_CAPTURE_CAP_BYTES':R+3})
case('three-denied',setup=lambda r,d,e:(r/'retained.avi').write_bytes(b'abc')and None,values={'SMB_CAPTURE_CAP_BYTES':R+2},expect='deny',used=3,reason='over-budget')
def retained(r,d,e):
    (r/'nested').mkdir()
    for name,n in (('nested/old.avi',3),('nested/native.wav',5),('old-master.mkv',7),('.trace.csv',11)):(r/name).write_bytes(b'x'*n)
case('retained-all-types',setup=retained,values={'SMB_CAPTURE_CAP_BYTES':R+25},expect='deny',used=26,reason='over-budget')
case('legacy30-still-valid',values={'SMB_CAPTURE_CAP_BYTES':30_000_000_000,'SMB_CAPTURE_SEGMENT_FRAMES':1024,'SMB_CAPTURE_FRAME_LIMIT':100000})
case('raised50-valid',values={'SMB_CAPTURE_CAP_BYTES':50_000_000_000,'SMB_CAPTURE_SEGMENT_FRAMES':1024,'SMB_CAPTURE_FRAME_LIMIT':100000})
case('uint64-largest-valid',values={'SMB_CAPTURE_CAP_BYTES':18_446_744_073_709_551_615})
for i,key in enumerate(guard):case('missing-'+str(i),values={key:None},expect='deny',reason='configuration')
for i,key in enumerate(guard[1:]):
    for j,value in enumerate(('', '0','-1','+1',' 1','1 ','0x1','abc','99999999999999999999999999999999999999999999')):
        case(f'numeric-{i}-{j}',values={key:value},expect='deny',reason='configuration')
case('cap-uint64-overflow',values={'SMB_CAPTURE_CAP_BYTES':18_446_744_073_709_551_616},expect='deny',reason='configuration')
case('segment-too-large',values={'SMB_CAPTURE_SEGMENT_FRAMES':1025},expect='deny')
case('limit-too-large',values={'SMB_CAPTURE_FRAME_LIMIT':100001},expect='deny')
case('scan-first-fault',values={'HOST_CAPTURE_SCAN_ERROR':'1'},expect='deny',reason='scan-error')
case('scan-next-fault',values={'HOST_CAPTURE_NEXT_ERROR':'1'},expect='deny',reason='scan-error')
case('marker-write-fatal',values={'HOST_CAPTURE_MARKER_ERROR':'1','SMB_CAPTURE_CAP_BYTES':R-1},expect='abort')
case('sticky-block',values={'SMB_CAPTURE_CAP_BYTES':R-1},expect='deny',used=0,action='repeat')
def grow(r,d,e):
    p=r/'stop-growth.bin';p.touch();e.update(HOST_CAPTURE_STOP_FILE=str(p),HOST_CAPTURE_STOP_BYTES='101')
case('stop-flush-counted',setup=grow,values={'SMB_CAPTURE_CAP_BYTES':R+100},expect='deny',used=101,reason='over-budget',action='next')
def outside(r,d,e):
    p=r.parent/'workspace-other';p.mkdir();e['SMB_CAPTURE_SEGMENT_DIR']=str(p)
case('prefix-sibling-target',setup=outside,expect='deny',reason='segment-outside-workspace')
def locked(r,d,e):
    p=r/'locked';p.mkdir()
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateFileW.restype=ctypes.c_void_p
    k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p]
    k.CloseHandle.argtypes=[ctypes.c_void_p]
    h=k.CreateFileW(str(p),1,0,None,3,0x02200000,None)
    assert h not in (None,ctypes.c_void_p(-1).value)
    return lambda:k.CloseHandle(h)
case('real-sharing-denial',setup=locked,expect='deny',reason='scan-error')
def junction(r,d,e):
    outside=r.parent/'outside';outside.mkdir();(outside/'protected.bin').write_bytes(b'outside bytes remain unchanged')
    link=r/'link'
    command="New-Item -ItemType Junction -Path '"+str(link).replace("'","''")+"' -Target '"+str(outside).replace("'","''")+"' | Out-Null"
    run=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True)
    assert run.returncode==0,run.stderr
case('descendant-junction-skipped',setup=junction,values={'SMB_CAPTURE_CAP_BYTES':R})
def long_unicode(r,d,e):
    p=r
    for i in range(7):p=p/('long-directory-'+str(i)+'x'*25);p.mkdir()
    p=p/'accent-é-Ω';p.mkdir();(p/'kept.bin').write_bytes(b'1234567')
    e['SMB_CAPTURE_SEGMENT_DIR']=str(p)
case('long-unicode-guard',setup=long_unicode,values={'SMB_CAPTURE_CAP_BYTES':R+6},expect='deny',used=7,reason='over-budget')
report.update(result='passed-host-budget-controls',case_count=len(report['cases']),
    coverage='Actual Win32 scanner/arithmetic/retained growth/sharing/junction/longUnicode/abort/default no-op; no native recorder or emulated changes')
save();print('PASS',len(report['cases']),'host budget cases',flush=True)
