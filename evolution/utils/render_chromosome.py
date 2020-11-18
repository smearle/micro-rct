import pickle
def _load(path):
    with open(path, 'rb') as f:
        chrome = pickle.load(f)