loadmodule "$1"
power 0 sleep 2 power 1
fork "xsdb" as myx
com0 echo = 1
myx echo = 1
print myx "conn; jtag ta 1; jtag freq 30000000; ta 1;ta; after 2000;set x 0"
sleep 10
print myx "device program /group/xap_charserv2/engineering/Characterization/charmnt/Bench/Project/Versal/VC1902/VST/AIE//sv60_es2/vdu_linux_files/SSAV_SV60_VDU_INST4_ES1_PVT_MultiS_1LP.pdi;after 1000; puts \"PDI LOADED SUCCESSFULLY\";set x 1"
print myx "after 100; puts \"Value is \$x\""
sleep 1
test
wait
   when myx matches "Value is (\\S+)"
      $PASS := "expr \"$PASS\" + \"$1\" || true"
      continue
   end
   after 45 seconds
     print "Test Hung"
     continue
   end
endtest
com0 echo = 0
sleep 2
kill myx
sleep 1


