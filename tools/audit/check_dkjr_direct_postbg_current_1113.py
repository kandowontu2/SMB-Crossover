"""Exact source rebase/inverse/control/foreign-byte gates; stdout only."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
from time import monotonic

import compose_dkjr_direct_postbg_current_1113 as M


def reject(fn,value):
    try:fn(value)
    except AssertionError:return
    raise AssertionError('Unknown/corrupted image was accepted')


def main():
    started=monotonic()
    def progress(phase):
        print('DKJR_POSTBG_GATE_PROGRESS '+json.dumps(dict(phase=phase,elapsed_seconds=round(monotonic()-started,3))),flush=True)
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    parent=nightly.read_bytes();image,info=M.proposal(parent)
    progress('forward')
    assert sha256(image).hexdigest()==M.PIN
    assert M.inverse(image)==parent
    progress('inverse')
    private=M.private_image(image)
    own={i for at,size in M.Old.dk_envelopes()for i in range(at,at+size)}
    assert all(image[i]==private[i]for i in own)
    progress('canonical-carrier')
    bad_cases=0
    for at in(0,next(iter(own)),M.Mirror.EDITS[0][0],len(parent)-1):
        for raw,fn in((parent,M.proposal),(image,M.inverse)):
            bad=bytearray(raw);bad[at]^=1;reject(fn,bytes(bad));bad_cases+=1
    historical=M.previous_merge(image)
    for other in(parent,historical,private):reject(M.inverse,other);bad_cases+=1
    progress('typed-and-corruption-rejection')
    hashes={}
    for name,full in(('first',False),('full',True)):
        text=M.controller(image,full=full)
        original=M.Turn.donor_ground_controller(private)if full else M.DK.controller(private)
        assert text.replace(M.PIN,M.DK.PIN,1)==original
        hashes[name]=sha256(text.encode()).hexdigest()
    progress('frozen-controller-ROM-only-adapters')
    # A fresh process gets only the candidate on stdin. No parent image,
    # prior proposal cache or Downloads read can furnish inverse old bytes.
    code='''import pathlib,sys,hashlib,json
original=pathlib.Path.read_bytes
def read(self):
 if str(self.resolve()).replace(chr(92),'/').casefold()=='c:/users/kando/downloads/smb-crossover-latest-wip-mmc5.nes':
  raise AssertionError('Independent inverse attempted a Downloads read')
 return original(self)
pathlib.Path.read_bytes=read
import compose_dkjr_direct_postbg_current_1113 as M
candidate=sys.stdin.buffer.read()
parent=M.inverse(candidate)
assert hashlib.sha256(parent).hexdigest()==M.PARENT
assert hashlib.sha256(M.private_image(candidate)).hexdigest()==M.DK.PIN
print(json.dumps(dict(parent_SHA256=hashlib.sha256(parent).hexdigest(),private_SHA256=M.DK.PIN,Downloads_reads=0)),flush=True)
'''
    result=subprocess.run([sys.executable,'-B','-c',code],input=image,capture_output=True,
        cwd=Path(__file__).resolve().parent,timeout=240)
    assert result.returncode==0,(result.returncode,result.stdout.decode(),result.stderr.decode())
    isolated=json.loads(result.stdout)
    assert isolated['parent_SHA256']==M.PARENT and isolated['Downloads_reads']==0
    print('DKJR_POSTBG_CURRENT_GATES '+json.dumps(dict(**info,
        independent_process_inverse=isolated,rejected_images=bad_cases,
        controller_Lua_SHA256=hashes,controller_ROM_identity_only_rebind=True,
        all_complete_DK_envelope_bytes_equal_frozen769=True,
        inverse_roundtrip=True,frozen8623_and769_unchanged=True),separators=(',',':')),flush=True)


if __name__=='__main__':main()
