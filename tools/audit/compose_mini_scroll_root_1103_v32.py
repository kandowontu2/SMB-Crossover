"""Distinct Mini camera successor; preserve the non-scrolling candidate."""
import inspect
import compose_mini_anchor_root_1103_v28 as A

def main():
    source=inspect.getsource(A.main)
    assert source.count('mini-mario-candidate-root-1103-v28')==1
    source=source.replace('mini-mario-candidate-root-1103-v28','mini-mario-candidate-root-1103-v32')
    env=dict(A.__dict__,__file__=__file__)
    exec(compile(source,__file__,'exec'),env);env['main']()

if __name__=='__main__':main()
