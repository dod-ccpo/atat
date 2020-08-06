#!/bin/bash


for i in $(cat gs.txt)
do

az group delete --name $i -y

done
