#!/usr/bin/env python3
"""
 Copyright (c) 2018 Intel Corporation.
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to
 the following conditions:
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import sys
import logging as log
from openvino.inference_engine import IENetwork, IEPlugin


class Network:
    """
    Load and configure inference plugins for the specified target devices 
    and performs synchronous and asynchronous modes for the specified infer requests.
    """

    def __init__(self):
        ### Done: Initialize any class variables desired ###
        self.network = None
        self.plugin = None
        self.input_blob = None
        self.out_blob = None
        self.exec_network = None
        self.infer_request = None

    def load_model(self, model, device, num_requests, cpu_extension=None, plugin=None):
        ### Done: Load the model ###
        model_xml = model
        model_bin = os.path.splitext(model_xml)[0] + ".bin"
        
        if not plugin:
            self.plugin = IEPlugin(device=device)
        else:
            self.plugin = plugin

        if cpu_extension and 'CPU' in device:
            self.plugin.add_cpu_extension(cpu_extension) 
            
        self.network = IENetwork(model=model_xml, weights=model_bin)

        ### DONE: Check for supported layers ###
        if self.plugin.device == "CPU":
            supported_layers = self.plugin.get_supported_layers(self.network)
            not_supported_layer = [layers for layers in self.network.layers.keys() if layers not in supported_layers]
            
            if len(not_supported_layer) > 0:
                sys.exit(1)
                
        ### DONE: Add any necessary extensions ###

        ### DONE: Return the loaded inference plugin ###         
        if num_requests == 0:
            self.exec_network = self.plugin.load(network=self.network)
        else:
            self.exec_network = self.plugin.load(network=self.network, num_requests=num_requests)
        # get input and output layer
        self.input_blob = next(iter(self.network.inputs))
        self.out_blob = next(iter(self.network.outputs))
        
        ### Note: You may need to update the function parameters. ###
        return self.plugin, self.get_input_shape()

    def get_input_shape(self):
        ### DONE: Return the shape of the input layer ###
        return self.network.inputs[self.input_blob].shape

    def exec_net(self, request_id, image):
        ### DONE: Start an asynchronous request ###
        self.infer_request = self.exec_network.start_async(
            request_id=request_id, inputs={self.input_blob: image})
        ### DONE: Return any necessary information ###
        ### Note: You may need to update the function parameters. ###
        return self.exec_network

    def wait(self, request_id):
        ### DONE: Wait for the request to be complete. ###
        status = self.exec_network.requests[request_id].wait(-1)
        ### DONE: Return any necessary information ###
        ### Note: You may need to update the function parameters. ###
        return status

    def get_output(self, request_id, output=None):
        ### Done: Extract and return the output results
        ### Note: You may need to update the function parameters. ###
        if output:
            result = self.infer_request_handle.outputs[output]
        else:
            result = self.exec_network.requests[request_id].outputs[self.out_blob]
        return result
