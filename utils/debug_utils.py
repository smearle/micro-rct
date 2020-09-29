
def print_msg(msg, priority=0, verbose=False):
    if verbose:
        print('{} {}'.format(''.join('*' for p in range(0, priority)), msg))