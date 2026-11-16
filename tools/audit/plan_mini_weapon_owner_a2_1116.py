"""Detached Mini20 over current Sonic a2: hashes and consumer bindings only."""
from pathlib import Path
from hashlib import sha256
import json
import current_mini_owner_research_a2_1116 as Reader
import compose_mini_weapon_owner_1116 as Mini
import replay_mini_weapon_owner_twoshot_1116 as Shot
import replay_mini_weapon_owner_full11_1116 as Full

R,ROM,H=Mini.R,Mini.ROM,Mini.H
PINS={Mini:'a9bb82ecf9cf67b8b26f03d25c8cdc489183eeca8f2d6dd70d367d07feeb06ae',
      Shot:'9f9b72ef23488f6a72507b281ecaaa1d33db976d33518c796d383496bce89ecd',
      Full:'9332be38ea671d9f998036bf9b840554d59bc4b772c5b7030ca6c9e3bb9855c0'}

def streaming(raw,rows):
    h=sha256();end=0
    for at,old,new in rows:h.update(raw[end:at]);h.update(new);end=at+len(old)
    h.update(raw[end:]);return h.hexdigest()

def plan(actual):
    for module,pin in PINS.items():assert H(Path(module.__file__).read_bytes())==pin
    parent=Reader.reference(actual);assert H(actual)==Reader.PIN and H(parent)==Mini.PARENT
    versioned,versioned_proof=Mini.proposal(parent);assert H(versioned)==Mini.CANDIDATE
    rows=Mini.SPANS;owned={i for at,old,_ in rows for i in range(at,at+len(old))}
    sonic=Reader.Sonic.spans();sonic_owned={i for at,old,_ in sonic for i in range(at,at+len(old))}
    assert len(owned)==20 and len(sonic_owned)==94 and not owned&sonic_owned
    for at,old,new in rows:assert actual[at:at+len(old)]==old
    for at,old,new in sonic:assert actual[at:at+len(new)]==new
    code=Mini.Plan.Previous.Current.CODE_AT;cookie_at=536595
    assert actual[code:code+7168]==parent[code:code+7168]==versioned[code:code+7168]
    assert actual[cookie_at:cookie_at+16]==parent[cookie_at:cookie_at+16]==versioned[cookie_at:cookie_at+16]
    bank79=versioned[16+79*8192:16+80*8192]
    consumers={}
    for name,module,key in(('two_shot',Shot,'flower'),('full11',Full,'full11')):
        text=module.controller(versioned,key);cfg=module.bindings(versioned);hooks=[]
        for symbol,h in cfg['hooks'].items():
            if h['work']:
                assert h['offset']//8192==3;off=h['pc']-0xa000
                assert actual[code+off:code+off+len(h['bytes'])]==bytes(h['bytes'])
                hooks.append(dict(name=symbol,PC=h['pc'],work=True,tag=3,preimage_hex=bytes(h['bytes']).hex(),unchanged=True))
            else:
                at=16+h['offset'];assert not set(range(at,at+len(h['bytes'])))&owned
                assert actual[at:at+len(h['bytes'])]==bytes(h['bytes'])
                bank=h['offset']//8192;old_hash=h['bank_SHA256'];new_hash=H(actual[16+bank*8192:16+(bank+1)*8192])if bank!=79 else H(bank79)
                hooks.append(dict(name=symbol,PC=h['pc'],file=at,work=False,bank=bank,preimage_hex=bytes(h['bytes']).hex(),unchanged=True,
                    versioned_bank_SHA256=old_hash,owning_combined_bank_SHA256=new_hash,bank_pin_refresh_required=old_hash!=new_hash))
        consumers[name]=dict(frozen_factory_SHA256=PINS[module],versioned_Lua_SHA256=H(text.encode()),unchanged_body_SHA256=H(text.split('\n',1)[1].encode()),
            intended_API_key=key,hooks=hooks,body_and_all_assertions_to_preserve=True)
    predicted=streaming(actual,rows)
    q=dict(passed=True,detached_plan=True,actual_parent_SHA256=Reader.PIN,versioned1327_reference_SHA256=Mini.PARENT,
        versioned_e32f_reference_SHA256=Mini.CANDIDATE,predicted_combined_SHA256=predicted,
        spans=[dict(file=at,bytes=len(old),old_hex=old.hex(),new_hex=new.hex())for at,old,new in rows],
        owned_bytes=20,changed_bytes=20,Sonic94_ownership_exact_and_disjoint=True,Sonic91_changed_bytes_preserved=True,
        total_union_owned_over1327=114,total_union_changed_over1327=111,
        Mini5120_code_SHA256=H(actual[code:code+5120]),Mini7168_payload_SHA256=H(actual[code:code+7168]),
        Mini_cookie_file=cookie_at,Mini_cookie_hex=actual[cookie_at:cookie_at+16].hex(),Mini_cookie_headers_changes=0,
        native79_current_parent_SHA256=H(actual[16+79*8192:16+80*8192]),native79_combined_SHA256=H(bank79),
        consumer_bindings=consumers,
        new_facade_contract=['Strict combined hash only; portable inverse replaces only20B to exacta2, never reads live Nightly',
            'Use frozen Sonic inverse only for versioned1327/e32f metadata; actual CPU bundle raw must be combined',
            'Preserve both Lua bodies byte-for-byte after config; refresh C.sha and every native hook full-bank pin, notably bank126 Sonic cookie',
            'Preserve all5120/7168 Mini bytes and both full16B loaded cookies; derive actual movement vector AF4D, keep A000/A3E5 return observers',
            'Native79 exact20B owning preimages and unchanged liveRollB54C; no cookie/header/art/helper/physics changes'],
        source_gate_transfer=dict(already_versioned_e32f=['Flat owner/command semantics and Roll exit invariant','144 full public wrappers/realKarnov+Roll/cycle delta','96 full-header faults/Fresh/Ready/CoRetire','All12 new helper PCs paired IRQ+busyNMI','Genuine earnedM/F/capacity/motion/bounce','Strong full1-1 and25 grounded1-2'],
            do_not_repeat_flat_or_full_matrices_without_new_cause=True),
        required_after_new_lease=['Strict owning combined composer/inverse and metadata/cold16/readback',
            'Execute actual combined earnedF/two-shot and strongfull Lua bodies as narrow source replays',
            'Sonic actual combined neutral/ceiling source replay using frozen currenta2 controls and refreshed auth only',
            'Paired combined IRQ/busyNMI smoke at reached sharedForeign/owner reload for Mini41 and Sonic43; same resident ISR and preservedSonic94 expected; do not relabel old40 cases as combined'],
        no_combined_ROM_constructed=True,no_combined_CPU_executed=True,no_physical_files_or_Mesen=True,
        versioned_reference_composition_receipt=versioned_proof['receipt_SHA256'],
        reader=Reader.metadata(actual),outputs=0)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':print('RESULT '+json.dumps(plan(ROM.read_bytes()),separators=(',',':')),flush=True)
