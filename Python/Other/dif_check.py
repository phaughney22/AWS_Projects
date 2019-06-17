#Quick script for checking if contents of one file exits in contents of another. Used to find list of instances that are not managed within a specific VPC.

import os

prod_inst=open("prod_inst.txt","r")
ssm_list=open("ssm_man_inst.txt","r")
managed=open("managed.txt","w+")
unmanaged=open("unmanaged.txt","w+")
if prod_inst.mode == "r" and ssm_list.mode == "r":
    prod_contents=prod_inst.readlines()
    ssm_contents=ssm_list.readlines()
    for line in prod_contents:
        if line in ssm_contents:
            managed.write(line)
        else:
            unmanaged.write(line)
managed.close()
unmanaged.close()
ssm_list.close()
prod_inst.close()
