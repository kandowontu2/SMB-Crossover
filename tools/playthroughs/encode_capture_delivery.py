"""Create a bounded-size MP4 preview; keep the verified lossless master."""
from pathlib import Path
import argparse
import json
import math
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import sha,workspace_bytes,recording_metadata
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--master',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--emulator-frames',type=int,required=True)
p.add_argument('--workspace-cap-bytes',type=int,default=30_000_000_000)
a=p.parse_args()
# The caller supplies the user's current storage allowance.  Reserve checks
# below apply equally when retained lossless recordings require a higher cap.
assert a.workspace_cap_bytes>0
master,output=a.master.resolve(),a.output.resolve()
assert master.is_relative_to(ROOT)and output.is_relative_to(ROOT)and not output.exists()
proof=master.with_suffix('.verification')/'report.json'
source=json.loads(proof.read_text())
assert source['result']=='passed-exact-rgb-and-pcm' and source['output']['sha256']==sha(master)
assert source['total_frames']==a.emulator_frames-1
# VBV rate plus buffer/container allowance. -fs is a second hard output bound;
# the additional64MiB workspace margin covers its final packet/index flush.
bound=math.ceil(source['video_seconds']*(4_000_000+192_000)/8)+8_000_000//8+source['total_frames']*512+1048576
used=workspace_bytes(ROOT)
assert used+bound+64*1024*1024<a.workspace_cap_bytes
run=subprocess.run(['ffmpeg','-n','-hide_banner','-loglevel','warning','-i',str(master),
    '-c:v','libx264','-preset','fast','-crf','16','-maxrate','4M','-bufsize','8M','-pix_fmt','yuv420p',
    '-c:a','aac','-b:a','192k','-fps_mode','passthrough','-fs',str(bound),'-movflags','+faststart',str(output)],capture_output=True,text=True)
output.with_suffix('.encode.log').write_text(run.stdout+run.stderr)
metadata=recording_metadata(output,a.emulator_frames)if output.exists()else dict(passed=False)
report=dict(classification='Lossy delivery copy; lossless master remains the frame/PCM proof',encode_exit=run.returncode,
    master_sha256=sha(master),lossless_proof_sha256=sha(proof),workspace_bytes_before=used,
    workspace_cap_bytes=a.workspace_cap_bytes,output_limit_bytes=bound,
    metadata=metadata,passed=run.returncode==0 and metadata['passed'])
output.with_suffix('.delivery.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS delivery'if report['passed']else'FAIL delivery preserved',flush=True)
raise SystemExit(0 if report['passed']else 1)
