"""Current source69 tail read extents; metadata only, no proposed-code CPU."""
from pathlib import Path
from unittest.mock import patch
import json,re
import audit_cf_guard_tail_capacity_root_1116 as Capacity
import profile_contra_force_service_layers_1116 as S

C,M,W=S.C,S.M,S.W


def run(actual):
    capacity=Capacity.inspect(actual);parent=S.BT.inverse(actual);b=M.symbols(parent)
    rogue=[]
    for mode,count,banks,highs in(('lower',192,'RdaLowerBankTable','RdaLowerHighTable'),
                                  ('upper',32,'RdaUpperRawBankTable','RdaUpperRawHighTable')):
        ba,ha=W.location(b,banks),W.location(b,highs)
        for i in range(count):
            bank=parent[ba+i]&127;start=(parent[ha+i]-0xa0)*256
            assert 0<=start<=8192-256
            if bank==69:rogue.append(dict(mode=mode,row=i,offset_half_open=[start,start+256]))
            assert not(bank==69 and start+256>0x1ff2 and start<0x2000),('Live Rogue immutable page overlaps proposed tail',mode,i,start)
    ba,sa,la=(W.location(b,n)for n in('S2AudioSampleBank','S2AudioSampleStart','S2AR8349'))
    dmc=[]
    for i in range(8):
        bank=parent[ba+i];lo=0xc000+64*parent[sa+i];size=16*parent[la+i+1]+1
        assert bank in(119,120)and lo+size<=0x10000
        dmc.append(dict(bank=bank,CPU=lo,bytes=size))
    # Conservative byte census of every possible absolute-indexed read base
    # in the unchanged bank. A hit is not presumed to be an instruction.
    page=parent[16+69*8192:16+70*8192]
    indexed_ops={0x1d,0x19,0x3d,0x39,0x5d,0x59,0x7d,0x79,0xb9,0xbc,0xbd,0xbe,0xd9,0xdd,0xf9,0xfd}
    leads=[]
    for i in range(8190):
        operand=page[i+1]+256*page[i+2]
        if page[i]in indexed_ops and 0xbef3<=operand<0xc000:
            leads.append(dict(PC=0xa000+i,opcode=page[i],base=operand,maximum_one_byte_index_read=operand+255))
    # The only own-bank range capable of reaching this tail is the declared
    # cookie reader; actual source LDX15/DEX bounds it to BFAD..BFBD.
    assert leads==[dict(PC=0xbf7b,opcode=0xdd,base=0xbfad,maximum_one_byte_index_read=0xc0ac)],leads
    guard=C.R/'tools/reference/contra_force_rom_guard_v1.s';retire=C.R/'tools/reference/contra_force_retire_proposal_v2.s'
    scene=C.R/'tools/reference/cf_cold_warm_resource_proposal_v3.s'
    assert C.H(guard.read_bytes())=='1daec12142d29efddec86648784df235c71216d910577341002862e317a81334'
    assert C.H(retire.read_bytes())=='b783b5063eee160ce983fd1b7723d707eb60e64e902fdc68c5417825310d9b09'
    assert C.H(scene.read_bytes())=='5e64a1a41cf23157922d7f52173c60864e50776cbefa9c3ecc351dd0c32f5a28'
    assert'ldx #15\nCfExternalByte:'in guard.read_text()and'dex\n bpl CfExternalByte'in guard.read_text()
    assert parent[16+69*8192+0x1f72:16+69*8192+0x1f83]==bytes.fromhex('a20fe002f008bde0dfddadbfd018ca10f1')
    # The final original Z2 procedures are source code, not open-ended data.
    end_sources={n:(C.R/'src'/n).read_text()for n in('zelda2_link_menu.s','zelda2_link_drops.s')}
    assert'.proc Z2MenuPrepare'in end_sources['zelda2_link_menu.s']
    assert'.proc Z2ReadCell'in end_sources['zelda2_link_drops.s']and'lda (R6),y'in end_sources['zelda2_link_drops.s']
    assert'cmp #4\n bcs Kill\n tay\n lda BagExpHi,y'in end_sources['zelda2_link_drops.s']
    return dict(actual_input_SHA256=C.H(actual),reference6a3_SHA256=C.H(parent),capacity=capacity,
        all224_Rogue_page_descriptors_exclude_tail=True,Rogue69_rows=rogue,
        all8_S2_DMC_samples=dmc,DMC_excludes_bank69=True,
        conservative_absolute_indexed_read_candidates=leads,
        actual_current_cookie_base=0xbfad,cookie_X_maximum=15,cookie_end_exclusive=0xbfbd,
        terminal_Z2_code=dict(ReadCell=[0xbef2,0xbf23],MenuPrepare=[0xbf23,0xbf47],
            BagExpHi=[0xbeee,0xbef2],BagExpLo=[0xbeea,0xbeee],maximum_legal_bag_index=3,
            ReadCell_indirect_is_native_block_buffer_not_ROMSegment69=True),
        source_header_rest_reads='DFE0/DFE1/DFE2 in explicitly mapped RAM2; no ROM69 tail read',
        source_names_and_hashes={n:C.H((C.R/'src'/n).read_bytes())for n in end_sources},
        limits=['Known current immutable PRG page readers, source-bounded tables, and conservative whole-bank read-base census',
            'Does not assert arbitrary malformed pointers cannot reach an unrelated physical page'],
        no_CPU_executed=True,no_proposed_bytes_executed=True,no_allocation_or_game_change=True,outputs=0)


if __name__=='__main__':
    actual=Capacity.BT.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Tail extent census attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(actual)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
