#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 11:04:21 2020
@author: hk3
"""

import torch
from torch import nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch.utils.data import TensorDataset
import numpy as np
           

class AE(nn.Module):
    def __init__(self, d_inp, d_hid):
        """
        Parameters
        ----------
        d_inp : dimension of input layer
        d_hid : dimension of hidden layer

        Returns
        -------
        None.
        """
        super(AE, self).__init__()
        self.d_inp = d_inp
        self.d_hid = d_hid
        self.encoder = nn.Linear(d_inp, d_hid)
        self.decoder = nn.Linear(d_hid, d_inp)
        
    def forward(self, x):
        x = F.relu(self.encoder(x))
        x = F.relu(self.decoder(x))
        return x
    def encode(self, x):
        x = F.relu(self.encoder(x))
        return x
    
    def train(self, train_data, epochs, learning_rate, batch_size):   
        x_train = Variable(torch.from_numpy(train_data)).type(torch.FloatTensor)
        y_train = Variable(torch.from_numpy(train_data)).type(torch.FloatTensor)
        
        trn = TensorDataset(x_train, y_train)
        trn_dataloader = torch.utils.data.DataLoader(trn, batch_size=batch_size, shuffle=True, num_workers=4)
        
        optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        loss_func = nn.MSELoss()
        print(self)
                
        losses = []
        for epoch in range(epochs):
            for batch_idx, (data, target) in enumerate(trn_dataloader):
                data = torch.autograd.Variable(data)
                optimizer.zero_grad()
                pred = self.forward(data)
                loss = loss_func(pred, data)
                losses.append(loss.cpu().data.item())
                loss.backward()
                optimizer.step()
                
                if(batch_idx%35==0):
                    print('Train epoch: {}, loss: {}'.format(epoch, loss.cpu().data.item()))
        return
        
    
    def encoding(self, train_data):
        x_train = Variable(torch.from_numpy(train_data)).type(torch.FloatTensor)
        y_train = Variable(torch.from_numpy(train_data)).type(torch.FloatTensor)
        
        trn = TensorDataset(x_train, y_train)
        trn_dataloader = torch.utils.data.DataLoader(trn, batch_size=1, shuffle=False, num_workers=4)
        
        #print(self)
        encoded_data = []
        
        for batch_idx, (data, target) in enumerate(trn_dataloader):
            data = torch.autograd.Variable(data)
            enc = self.encode(data).detach().numpy()
            enc = enc.flatten()
            encoded_data.append(enc)
            
        return np.array(encoded_data)
        
            
    
class Stacked_AE:
    def __init__(self, N_layers, dims):
        """
        Parameters
        ----------
        N_layers: Number of AE to stack
        dims : dimension of input followed by 
                hidden layer (array, length = N_layers + 1)

        Returns
        -------
        None.
        """
        if(len(dims)!=N_layers+1):
            print("Entered wrong dimensions, dimension of input followed by hidden layers")
            exit(0);
        self.AANNs = []
        self.N_layers = N_layers
        self.dims = dims
        for i in range(N_layers):
            model = AE(dims[i], dims[i+1])
            self.AANNs.append(model)
    
    
    def encoding(self, i, data_set):
        return self.AANNs[i].encoding(data_set)
                                    
    
    def stack_training(self, train_data, epochs, learning_rate, batch_size):
        data_set = train_data;
        for i in range(self.N_layers):
            self.AANNs[i].train(data_set, epochs, learning_rate, batch_size)
            data_set = self.encoding(i, data_set);