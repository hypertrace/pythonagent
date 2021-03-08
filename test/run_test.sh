#!/bin/bash
#File: run_test.sh
#Author: Nitin Sahai
#Date: 03/04/2021
#Notes:
#
# This runs the flask test on the demo HyperTrace Python Agent
#
curl -X GET http://localhost:5000/ -H "tester1:tester1" -H "tester2:tester2" -v
echo ""
exit 0
