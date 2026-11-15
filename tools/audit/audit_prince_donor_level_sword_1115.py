"""Exact original progression/password sword rules; explicit primitives only."""
from hashlib import sha256
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as Original


def run():
    raw=Original.donor()
    def block(bank,pc,expected):
        code=bytes.fromhex(expected);at=16+bank*16384+pc-(0xc000 if bank==7 else 0x8000)
        assert raw[at:at+len(code)]==code
        return dict(bank=bank,PC=pc,bytes=code.hex(),SHA256=sha256(code).hexdigest())
    progression=block(5,0x86f8,'a570186901c90e9002a9008570')
    password=block(2,0xbb9b,'0d6d078570f005a9018dee06')
    reset=block(5,0x85d7,'a570d005a9008dee06adee06c902d00bceee064cf285')
    progression_cases=[]
    for old in range(14):
        c=Original.machine();c.memory.switch(5);c.memory[0x70]=old;c.pc=0x86f8
        Original.until(c,0x8705,limit=50)
        assert c.memory[0x70]==(old+1)%14
        progression_cases.append([old,c.memory[0x70]])
    password_cases=[]
    for restored in range(14):
        c=Original.machine();c.memory.switch(2)
        # The preceding password decode has supplied two disjoint bit
        # groups. Start at their OR/store to isolate its exact sword rule.
        c.a=restored&3;c.memory[0x76d]=restored&12;c.memory[0x6ee]=0;c.pc=0xbb9b
        Original.until(c,0xbba7,limit=50)
        assert c.memory[0x70]==restored and c.memory[0x6ee]==int(restored!=0)
        password_cases.append(dict(restored_selector=restored,sword=c.memory[0x6ee]))
    q=dict(passed=True,donor_SHA256=Original.SHA,actual_progression=progression,
        actual_password_restore=password,actual_sword_reset_normalization=reset,
        progression_primitive_cases=progression_cases,password_primitive_cases=password_cases,
        interpretation='Original progression selector70 advances modulo14; password-restored nonzero progression supplies Sword1, while85D7 clears Sword only at selector0 and otherwise normalizes drawn2 to sheathed1',
        scope='Authenticated original instruction blocks and explicit primitive inputs, not an original full-level controller replay or current-port placement grant',
        outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':print(json.dumps(run(),separators=(',',':')),flush=True)
