"""Actual mounted current CF code gates; no file/native/emulator outputs."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import contra_force_p1_work_marker_model_1116 as M

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def cold_all(raw):
    results=[]
    for key in M.IDENTITIES:
        m=M.cold(raw,key);b=m.bundle
        carrier=raw[C.Plan.Audit.P.CHR+935*1024:C.Plan.Audit.P.CHR+959*1024]
        assert bytes(m.ram[1])==carrier[:8192],(key,'RAM1 code readback')
        assert bytes(m.ram[3])==carrier[16384:24576],(key,'RAM3 code/data readback')
        for _ in range(2):m.controller_pad=0;Frames.frame(m,whole_pass=True)
        M.empty(m,key)
        assert bytes(m.ram[1])==carrier[:8192]and bytes(m.ram[3])==carrier[16384:24576]
        rows=[m[512+i*4+2]&24 for i in range(64)]
        assert not any(rows),(key,'Complete late leaves hidden/visible tags')
        assert not m.ram[2][0x2df]&128,(key,'Late phase consumed at completeMain')
        assert m.ram[2][0x2fb]==0,(key,'Native palette Choice0')
        row=dict(identity=key,compiled_name=M.IDENTITIES[key][0],variant=M.IDENTITIES[key][1],actual_raw_SHA256=C.H(raw),
            code_RAM1_RAM3_full_readback_exact=True,current_cookie=bytes(m.ram[2][-32:-16]).hex(),
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
            lives=N.get(m,'NumberofLives'),pending=m[W.address(b,'SmFreezePalettePending')],LastBlue=m[W.address(b,'SmFreezeLastBlue')],
            marker=m.ram[2][0x2df],Choice=m.ram[2][0x2fb],all64_visible_hidden_OAM_tag_bits_zero=True)
        results.append(row);print('PROGRESS '+json.dumps(row,separators=(',',':')),flush=True)
    return dict(all4_real_compiled_Select_Start_constructors_and_two_completeMain=True,rows=results,
        actual_unredirected_candidate_CPU=True,no_gameplay_seeds=True,outputs=0)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cold',action='store_true');args=ap.parse_args();assert args.cold
    parent=C.load_current_image();raw,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Mounted source gate attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=dict(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,cold=cold_all(raw),native=False,outputs=0)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
