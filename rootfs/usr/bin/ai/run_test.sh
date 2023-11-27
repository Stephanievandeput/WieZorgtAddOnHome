#!/bin/bash

# 30 --> 30/3 = 10 (days)
# 90 --> 90/3 = 30 (days)
# 180 --> 180/3 = 60 (days)

for ((i=0; i<180; i++)); do
    python Core/AiTraining.py
done
