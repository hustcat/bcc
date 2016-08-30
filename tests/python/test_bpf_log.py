#!/usr/bin/env python
# Copyright (c) PLUMgrid, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")

from bcc import BPF
from builtins import input
from simulation import Simulation
import sys
import os
from unittest import main, TestCase


#arg1 = sys.argv.pop(1)
output = os.path.join(os.getcwd(), 'output.txt')
sys.stderr = open(output, 'wb')
error_msg = "R0 invalid mem access 'map_value_or_null'\n"
text = ""

class TestBPFProgLoad(TestCase):
    def setUp(self):
        global text
        text += """
               #include <uapi/linux/ptrace.h>
               #include <bcc/proto.h>
               BPF_TABLE("hash", int, int, t1, 10);
               int sim_port(struct __sk_buff *skb) {
               int x = 0, *y;

               """
        repeat = """
               y = t1.lookup(&x);
               if (!y) return 0;
               x = *y;
               """
        end = """
               y = t1.lookup(&x);
               x = *y;
               return 0; 
               }
              """
        for i in range(0,300):
            text += repeat
        text += end
        #print(text)
        #self.b = BPF(text=text, debug=2)

    def test_jumps(self):
        #print(text)
        b = BPF(text=text, debug=2)

        try:
            ingress = b.load_func("sim_port",BPF.SCHED_CLS)
        except Exception:
            sys.stderr.flush()
            with open(output, 'rb') as f:
                lines = f.readlines()
                os.remove(output)
                self.assertEqual(error_msg in lines, True)

if __name__ == "__main__":
    main()


