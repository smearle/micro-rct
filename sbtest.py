from itertools import zip_longest
from typing import Dict, List, Tuple, Type, Union

import gym
import torch as th
from torch import nn

#from stable_baselines3.common.preprocessing import get_flattened_obs_dim, is_image_space
#from stable_baselines3.common.utils import get_device

import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np


from gym_micro_rct.envs.rct_env import RCT



class BaseFeaturesExtractor(nn.Module):
    """
    Base class that represents a features extractor.

    :param observation_space:
    :param features_dim: Number of features extracted.
    """

    def __init__(self, observation_space: gym.Space, features_dim: int = 0):
        super(BaseFeaturesExtractor, self).__init__()
        assert features_dim > 0
        self._observation_space = observation_space
        self._features_dim = features_dim

    @property
    def features_dim(self) -> int:
        return self._features_dim

    def forward(self, observations: th.Tensor) -> th.Tensor:
        raise NotImplementedError()



class Self_Attn(nn.Module):
    """ Self attention Layer"""
    #def __init__(self,in_dim,activation):
    def __init__(self,in_dim):
        super(Self_Attn,self).__init__()
        self.chanel_in = in_dim
        #self.activation = activation
        
        self.query_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim//8 , kernel_size= 1)
        self.key_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim//8 , kernel_size= 1)
        self.value_conv = nn.Conv2d(in_channels = in_dim , out_channels = in_dim , kernel_size= 1)
        self.gamma = nn.Parameter(th.zeros(1))

        self.softmax  = nn.Softmax(dim=-1) #
    def forward(self,x):
        """
            inputs :
                x : input feature maps( B X C X W X H)
            returns :
                out : self attention value + input feature 
                attention: B X N X N (N is Width*Height)
        """
        m_batchsize,C,width ,height = x.size()
        proj_query  = self.query_conv(x).view(m_batchsize,-1,width*height).permute(0,2,1) # B X CX(N)
        proj_key =  self.key_conv(x).view(m_batchsize,-1,width*height) # B X C x (*W*H)
        energy =  th.bmm(proj_query,proj_key) # transpose check
        attention = self.softmax(energy) # BX (N) X (N) 
        proj_value = self.value_conv(x).view(m_batchsize,-1,width*height) # B X C X N

        out = th.bmm(proj_value,attention.permute(0,2,1) )
        out = out.view(m_batchsize,C,width,height)
        
        out = self.gamma*out + x
        return attention[:, None, :,:,]

class AttnCnn(nn.Module):
    """
    :param observation_space:
    :param features_dim: Number of features extracted.
        This corresponds to the number of unit for the last layer.
    """

    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 512):
        super(AttnCnn, self).__init__()
        # We assume CxHxW images (channels first)
        # Re-ordering will be done by pre-preprocessing or wrapper

        self.attn = Self_Attn(observation_space.shape[0])
        self.features_dim = features_dim
        n_input_channels = 1
        self.cnn = nn.Sequential(
            #nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4, padding=0),
            nn.Conv2d(n_input_channels, 8, kernel_size=32, stride=2, padding=0),
            nn.ReLU(),
            #nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=0),
            nn.Conv2d(8, 16, kernel_size=16, stride=2, padding=0),
            nn.ReLU(),
            nn.Conv2d(16, 16, kernel_size=4, stride=1, padding=0),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute shape by doing one forward pass
        with th.no_grad():
            n_flatten = self.cnn(self.attn(th.as_tensor(observation_space.sample()[None])).float()).shape[1]

        self.linear = nn.Sequential(nn.Linear(n_flatten, features_dim), nn.ReLU())

        
    def forward(self, observations: th.Tensor) -> th.Tensor:
        return self.linear(self.cnn(self.attn(observations)))

class CnnAttn(nn.Module):
    """
    :param observation_space:
    :param features_dim: Number of features extracted.
        This corresponds to the number of unit for the last layer.
    """
    
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 512):
        super(CnnAttn, self).__init__()
        # We assume CxHxW images (channels first)
        # Re-ordering will be done by pre-preprocessing or wrapper
        
        self.features_dim = features_dim
        n_input_channels=observation_space.shape[0]
        self.cnn = nn.Sequential(
            #nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4, padding=0),
            nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=1, padding=0),
            nn.ReLU(),
            #nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=0),
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=2, stride=1, padding=0),
            nn.ReLU(),
        )

        # Compute shape by doing one forward pass
        with th.no_grad():
            in_attn = (self.cnn(th.as_tensor(observation_space.sample()[None])).float()).shape[1]
            
        self.attn = Self_Attn(in_attn)
        self.flatten = (nn.Flatten())

       # Compute shape by doing one forward pass
        with th.no_grad():
            n_flatten = (self.flatten(self.attn(self.cnn(th.as_tensor(observation_space.sample()[None])).float()))).shape[1]
        self.linear = nn.Sequential(nn.Flatten(), nn.Linear(n_flatten, features_dim), nn.ReLU())

        
    def forward(self, observations: th.Tensor) -> th.Tensor:
        return self.linear(self.attn(self.cnn(observations)))


class NatureCNN(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 512):
        super(NatureCNN, self).__init__(observation_space, features_dim)
        # We assume CxHxW images (channels first)
        # Re-ordering will be done by pre-preprocessing or wrapper
        '''
        assert is_image_space(observation_space), (
            "You should use NatureCNN "
            f"only with images not with {observation_space}\n"
            "(you are probably using `CnnPolicy` instead of `MlpPolicy`)\n"
            "If you are using a custom environment,\n"
            "please check it using our env checker:\n"
            "https://stable-baselines3.readthedocs.io/en/master/common/env_checker.html"
        )
        '''
        n_input_channels = observation_space.shape[0]
        self.cnn = nn.Sequential(
            #nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4, padding=0),
            nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=1, padding=0),
            nn.ReLU(),
            #nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=0),
            nn.Conv2d(32, 64, kernel_size=4, stride=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=0),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute shape by doing one forward pass
        with th.no_grad():
            n_flatten = self.cnn(th.as_tensor(observation_space.sample()[None]).float()).shape[1]
            
        self.linear = nn.Sequential(nn.Linear(n_flatten, features_dim), nn.ReLU())
             
    def forward(self, observations: th.Tensor) -> th.Tensor:
        return self.linear(self.cnn(observations))

class AttnCnnMin(nn.Module):
    """ Self attention Layer"""
    #def __init__(self,in_dim,activation):
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 512):
        super(AttnCnnMin,self).__init__()
        self.chanel_in = observation_space.shape[0]
        #self.activation = activation
        self.features_dim = features_dim

        self.query_conv = nn.Conv2d(in_channels = self.chanel_in , out_channels = self.chanel_in//8 , kernel_size= 1)
        self.key_conv = nn.Conv2d(in_channels = self.chanel_in , out_channels = self.chanel_in//8 , kernel_size= 1)
        self.value_conv = nn.Conv2d(in_channels = self.chanel_in , out_channels = self.chanel_in , kernel_size= 1)
        self.gamma = nn.Parameter(th.zeros(1))
        self.softmax  = nn.Softmax(dim=-1) #

        self.flatten = nn.Flatten()
        n_flatten = 65536
        self.linear = nn.Sequential(nn.Linear(n_flatten, features_dim), nn.ReLU())

        
    def forward(self,x):
        """
            inputs :
                x : input feature maps( B X C X W X H)
            returns :
                out : self attention value + input feature 
                attention: B X features_dim)
        """
        m_batchsize,C,width ,height = x.size()
        proj_query  = self.query_conv(x).view(m_batchsize,-1,width*height).permute(0,2,1) # B X CX(N)
        proj_key =  self.key_conv(x).view(m_batchsize,-1,width*height) # B X C x (*W*H)
        energy =  th.bmm(proj_query,proj_key) # transpose check
        attention = self.softmax(energy) # BX (N) X (N) 
        proj_value = self.value_conv(x).view(m_batchsize,-1,width*height) # B X C X N

        out = th.bmm(proj_value,attention.permute(0,2,1) )
        out = out.view(m_batchsize,C,width,height)
        out = self.gamma*out + x

        return self.linear(self.flatten(attention))

class NewCNN1(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Box, features_dim: int = 512):
        super(NewCNN1, self).__init__(observation_space, features_dim)
        # We assume CxHxW images (channels first)
        # Re-ordering will be done by pre-preprocessing or wrapper

        n_input_channels = observation_space.shape[0]
        self.cnn = nn.Sequential(
            #nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4, padding=0),
            nn.Conv2d(n_input_channels, 32, kernel_size=6, stride=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(n_input_channels, 64, kernel_size=5, stride=1, padding=0),
            nn.ReLU(),
            #nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=0),
            nn.Conv2d(64, 128, kernel_size=4, stride=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=0),
            nn.ReLU(),
            nn.Flatten(),
        )

        # Compute shape by doing one forward pass
        with th.no_grad():
            n_flatten = self.cnn(th.as_tensor(observation_space.sample()[None]).float()).shape[1]
        
        self.linear = nn.Sequential(nn.Linear(n_flatten, features_dim), nn.ReLU())
        
    def forward(self, observations: th.Tensor) -> th.Tensor:
        return self.linear(self.cnn(observations))

env = RCT(settings_path='configs/settings.yml')
#new = NatureCNN(env.observation_space)
#new = Self_Attn(29)
#new = CnnAttn(env.observation_space)
new = AttnCnnMin(env.observation_space)
#print(env.observation_space.shape[0])
ins = th.randn(50, 29,16,16)
outs = new(ins)
#print(len(outs))
#print(len(outs))
print(outs.shape)

l1 = nn.Conv2d(29, 32, kernel_size=6, stride=1, padding=0)
l2 = nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=0)
l3 = nn.Conv2d(64, 128, kernel_size=4, stride=1, padding=0)
l4 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=0)
l5 = nn.Flatten()
#out = l5(l4(l3(l2(l1(ins)))))



cnn = nn.Sequential(
    #nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4, padding=0),
    nn.Conv2d(29, 32, kernel_size=8, stride=1, padding=0),
    nn.ReLU(),
    #nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=0),
    nn.Conv2d(32, 64, kernel_size=4, stride=1, padding=0),
    nn.ReLU(),
    nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=0),
    nn.ReLU(),
    nn.Flatten(),
    )
#v = cnn(ins)
#print(out.shape)