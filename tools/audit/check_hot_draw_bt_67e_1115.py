"""Leased actual HotNew118 source gates, no files or native emulator."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_hot_draw_bt_67e_1115 as C
import replay_hot_draw_bt_67e_1115 as F
import hot_draw_bt_67e_model_1115 as Model

W,N,Frames=Model.W,Model.N,Model.Frames


def strict(parent,image):
    rejects=[]
    def rejected(label,raw,method):
        try:method(raw)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Unknown/dirty input accepted',label))
    for label,raw,method in(('parent_inverse',parent,C.inverse),('candidate_forward',image,C.proposal),
        ('old7fb',C.reference(parent),C.proposal),('truncated',image[:-1],C.inverse),
        ('unknown',bytes(len(image)),C.inverse)):
        rejected(label,raw,method)
    for label,at in(('owned',C.FILE),('tail108',C.FILE+118),('ThShared',C.FILE+118+47),
        ('HotPlayerGraphics',C.FILE+186),('Mini',C.FILE+214),('cache',1989648),('BTcookie',765868),
        ('PrinceCookie',535471),('PrinceCarrier',1800000),('BubPalette',1501131),('BubCookie',536570),
        ('carry',792489),('score',1034694),('DK',105706),('Gimmick',201137),('unowned',90000)):
        for kind,raw,method in(('forward',parent,C.proposal),('inverse',image,C.inverse)):
            bad=bytearray(raw);bad[at]^=1;rejected(kind+'_'+label,bytes(bad),method)
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Portable operation read mutable Nightly'
        return reader(path)
    C.inverse.cache_clear();C.proposal.cache_clear()
    with patch.object(Path,'read_bytes',read):
        assert C.inverse(image)==parent and C.proposal(parent)[0]==image
        old7fb=C.reference(parent);ace=C.Plan.Reference.reference(old7fb);old174=C.Carry.inverse(ace)
        protected=[]
        for label,a,b,count in(('Bub',old7fb,parent,57),('Prince',ace,old7fb,9907),('carry',old174,ace,714)):
            sites={i for i,(x,y)in enumerate(zip(a,b,strict=True))if x!=y};assert len(sites)==count
            assert not sites.intersection(range(C.FILE,C.FILE+118))
            assert all(image[i]==parent[i]for i in sites)
            protected.append(dict(owner=label,changed_bytes=count,all_current_values_preserved=True))
        bindings={key:F.bindings(image,key)['sha']for key in F.IDENTITIES}
        assert set(bindings.values())=={C.CANDIDATE}
        loaders=[]
        for label,fixture in(('installed_parent',parent),('postdelivery_candidate',image)):
            seen=[]
            def load(path):
                if path.resolve()==C.ROM.resolve():seen.append(1);assert len(seen)==1;return fixture
                return read(path)
            with patch.object(Path,'read_bytes',load):assert C.load_current_image()==fixture
            loaders.append(label)
    return dict(composition=C.proposal(parent)[1],strict_rejections=rejects,
        portable_inverse_exact67=True,all_unowned_bytes_exact=True,protected_changes=protected,
        actual_candidate_bindings=bindings,single_read_loader_cases=loaders,
        mutable_Nightly_reads_after_load=0,inline_preimage_bytes=len(C.OLD))


def cold(parent,image):
    out=[]
    for key in('rash','zitz'):
        pair=[Model.cold(raw,key)for raw in(parent,image)];Model.compare(pair)
        row=dict(identity=key,SelectedCharacter=N.get(pair[1],'SelectedCharacter'),
            FmGroups=N.get(pair[1],'FmGroups'),lives=N.get(pair[1],'NumberofLives'),
            PlayerStatus=N.get(pair[1],'PlayerStatus'),actual_owning_ROM=C.H(pair[1].bundle['raw']))
        assert row['SelectedCharacter']==33 and row['lives']==2
        assert row['PlayerStatus']==0 and N.get(pair[1],'CheatInvincible')==N.get(pair[1],'CheatStartLevel')==0
        pair[1].raw_page(1,194)
        assert bytes(pair[1][C.BASE:C.BASE+118])==C.NEW
        assert bytes(pair[1][C.BASE+118:C.BASE+226])==image[C.FILE+118:C.FILE+226]
        row.update(actual_first_Hot118_readback=True,live_following108_exact=True)
        out.append(row);print('PROGRESS '+json.dumps(row),flush=True)
    return dict(real_compiled_Select_Start_constructor=True,rows=out,
        full_native_private_RAM_OAM_VRAM_maps_and_live_stack_equal=True,gameplay_seeds=0)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','cold'));args=ap.parse_args()
    raw=C.load_current_image();parent=F.parent(raw);image,info=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Source gate attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q={'strict':strict,'cold':cold}[args.mode](parent,image)
    q.update(mode=args.mode,parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,
        actual_candidate_opcodes=True,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
