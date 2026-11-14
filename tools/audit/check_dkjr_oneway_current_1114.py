"""Strict421 composition and isolated source inverse; stdout/pipe only."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import compose_dkjr_oneway_current_1114 as M


def reject(fn,raw):
    try:fn(raw)
    except AssertionError:return
    raise AssertionError('Unknown/corrupt input accepted')


def main():
    current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    raw,info=M.proposal(current);assert sha256(raw).hexdigest()==M.PIN
    assert M.inverse(raw)==current
    own=M.ownership();protected=M.Current.protected_envelopes()
    assert all(raw[i]==current[i]for i in range(len(raw))if i not in own)
    assert all(raw[at:at+size]==current[at:at+size]for at,size in protected)
    cases=0
    for image,fn in((current,M.proposal),(raw,M.inverse)):
        for at in(0,M.S.P.B.COOKIE_AT,M.S.file_at(8928),protected[0][0],len(raw)-1):
            bad=bytearray(image);bad[at]^=1;reject(fn,bytes(bad));cases+=1
    reject(M.inverse,current);cases+=1
    text=M.controller(raw)
    print('DKJR_ONEWAY_CURRENT_FORWARD '+json.dumps(dict(passed=True,SHA256=M.PIN,
        protected_envelope_bytes=sum(size for _,size in protected),current_fix_bytes=176,
        corruption_rejections=cases,controller_SHA256=sha256(text.encode()).hexdigest())),flush=True)
    code='''from pathlib import Path
import sys,json,hashlib
read=Path.read_bytes
blocked=('c:/users/kando/downloads/smb-crossover-latest-wip-mmc5.nes',
 'c:/users/kando/documents/chatgpt/smb crossover/build/metal-flower-native-1112/candidate.nes')
def guarded(self):
 if str(self.resolve()).replace(chr(92),'/').casefold()in blocked:
  raise AssertionError('Independent inverse attempted mutable/retained ROM read')
 return read(self)
Path.read_bytes=guarded
import compose_dkjr_oneway_current_1114 as M
raw=sys.stdin.buffer.read();parent=M.inverse(raw)
assert hashlib.sha256(parent).hexdigest()==M.PARENT
assert hashlib.sha256(M.private_image(raw)).hexdigest()==M.S.PIN
assert M.proposal(parent)[0]==raw
print(json.dumps(dict(passed=True,parent_SHA256=M.PARENT,private_SHA256=M.S.PIN,
 Downloads_reads=0,retained_private_ROM_reads=0)),flush=True)
'''
    result=subprocess.run([sys.executable,'-B','-c',code],input=raw,capture_output=True,
        cwd=Path(__file__).resolve().parent,timeout=450)
    assert result.returncode==0,(result.returncode,result.stdout.decode(),result.stderr.decode())
    isolated=json.loads(result.stdout)
    print('DKJR_ONEWAY_ISOLATED_INVERSE '+json.dumps(isolated,separators=(',',':')),flush=True)
    print('DKJR_ONEWAY_CURRENT_GATES '+json.dumps(dict(info,passed=True,
        exact_protected_envelope_bytes=sum(size for _,size in protected),strict_inverse=True,
        isolated_inverse=isolated,corruption_rejections=cases,outputs_written=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
