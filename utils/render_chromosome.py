import pickle
import os
import sys
sys.path.append("..")

def _load(path):
    with open(path, 'rb') as f:
        chrome = pickle.load(f)
        

if __name__ == '__main__':
    test_chrome = _load(os.path.join('results', '0', '{"ride_count": 3}.p'))
    print(test_chrome.elite)
