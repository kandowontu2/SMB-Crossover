"""Mini native special-window override successor, no installation."""
import inspect
import compose_mini_graphics_root_1103_v35 as P

def main():
    source=inspect.getsource(P.main)
    assert source.count('mini-mario-candidate-root-1103-v35')==1
    source=source.replace('mini-mario-candidate-root-1103-v35','mini-mario-candidate-root-1103-v40')
    env=dict(P.__dict__,__file__=__file__)
    exec(compile(source,__file__,'exec'),env);env['main']()

if __name__=='__main__':main()
