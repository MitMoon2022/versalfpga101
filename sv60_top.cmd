become "ph1760"
if run "[ -z $2 ]" then
   $loop = 1
else
   $loop = "$2"
endif
$PASS = 0
repeat $loop
  execute "/home/xapchar/sv60_chk.cmd" "$1"
end
print "Total runs: $loop"
print "Passed runs: $PASS"

