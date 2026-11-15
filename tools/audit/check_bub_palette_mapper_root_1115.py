"""Independent exact-image and 6502 component review; no natural-play claim."""
from hashlib import sha256
from pathlib import Path
import json
from py65.devices.mpu6502 import MPU

R=Path(__file__).resolve().parents[2]
GRANT=R/'docs/qa/allocations/bub-native-palette-current-source-1115.json'
LEASE='0daf2ece6fb9511132716478580ac61ba3c9c248f919f440a5a0f083bbdcb59c'
PARENT='40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e'
CANDIDATE='174fa29cf05ce1d14526ea3778c74b33a3858301c81da49b982e0ca2200ab0b4'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
H=lambda b:sha256(b).hexdigest()

class Memory(list):
    recording=False
    def __setitem__(self,at,value):
        if self.recording:self.writes.append(at)
        return super().__setitem__(at,value)

def main():
    data=GRANT.read_bytes();assert H(data)==LEASE
    grant=json.loads(data);assert grant['source_in_memory_composition_and_mounts_authorized']
    original=ROM.read_bytes();assert H(original)==PARENT
    image=bytearray(original);owned=set()
    for row in grant['logical_envelopes']:
        at=row['file'];before=bytes.fromhex(row['before']);after=bytes.fromhex(row['after'])
        assert original[at:at+len(before)]==before and len(before)==len(after)
        assert not owned.intersection(range(at,at+len(before)))
        image[at:at+len(after)]=after;owned.update(range(at,at+len(after)))
    pages=(301,305,337,362,363,440,819,666);start=1048592
    private=b''.join(image[start+p*1024:start+(p+1)*1024]for p in pages)
    art=image[start+441*1024:start+442*1024]
    cookie=bytes.fromhex('a72702')+sha256(private+art).digest()[:13]
    row=grant['cookie_envelope'];at=row['file'];old_cookie=bytes.fromhex(row['before'])
    assert at==536570 and original[at:at+16]==old_cookie
    image[at:at+16]=cookie;owned.update(range(at,at+16));image=bytes(image)
    changed={i for i,(a,b)in enumerate(zip(original,image,strict=True))if a!=b}
    assert H(image)==CANDIDATE and len(owned)==52 and len(changed)==49 and changed<=owned
    inverse=bytearray(image)
    for row in grant['logical_envelopes']:
        at=row['file'];before=bytes.fromhex(row['before']);inverse[at:at+len(before)]=before
    inverse[536570:536586]=old_cookie
    assert bytes(inverse)==original
    mapper=image[1499208:1499208+29]
    assert mapper==private[0xb438-0xa000:0xb455-0xa000]
    memory=Memory([0]*65536);memory[0xb438:0xb455]=mapper
    cpu=MPU(memory=memory);cases=0;smallest=255;cycles=set()
    for identity in(0,1,255):
      memory[0xc300]=identity
      for pc,source in((0xb438,0xc106),(0xb43e,0xc102)):
       for x,y in((0,0),(173,248)):
        for attr in range(256):
         memory[source+y]=attr
         expect=attr&252 if identity==0 and attr&3==3 else attr
         for status in range(256):
          if not status&32:continue
          cpu.pc=pc;cpu.sp=236;cpu.a=85;cpu.x=x;cpu.y=y;cpu.p=status
          memory.recording=False;cpu.stPushWord(0x5aff)
          memory.writes=[];memory.recording=True;cpu.processorCycles=0
          for _ in range(32):
           if(cpu.pc,cpu.sp)==(0x5b00,236):break
           assert memory[cpu.pc],('Unexpected mapper BRK',identity,attr,status,pc,cpu.pc)
           cpu.step();smallest=min(smallest,cpu.sp)
          else:raise AssertionError(('Unbounded component',identity,attr,status,pc))
          memory.recording=False
          flags=(status&~130)|(128 if expect&128 else 0)|(2 if expect==0 else 0)
          assert(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)==(expect,x,y,flags,236)
          assert memory[source+y]==attr and memory[0xc300]==identity
          assert all(0x100<=a<0x200 for a in memory.writes)
          cycles.add(cpu.processorCycles);cases+=1
    q=dict(passed=True,parent_SHA256=PARENT,candidate_SHA256=CANDIDATE,
        independently_composed_owned_bytes=52,changed_bytes=49,portable_inverse_exact=True,
        cookie=cookie.hex(),actual_mapper_6502_cases=cases,identities=[0,1,255],
        all256_attrs_all128_valid_statuses_two_entries_two_XY=True,minimum_SP=smallest,
        component_cycles=sorted(cycles),only_stack_writes=True,original_private_attr_unchanged=True,
        returned_A_and_NZ_match_mapping_XY_CVID_preserved=True,
        source_primitive_only=True,full_Pair_and_natural_play_NOT_claimed=True,
        outputs=0,Mesen=False)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)

if __name__=='__main__':main()
