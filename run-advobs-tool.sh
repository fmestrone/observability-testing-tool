### RUN-ADVOBS-TOOL

# This script is automatically installed into the GCE instances of the QL environment during lab provisioning
# It runs the AdvObs Tools on the VM to generate metrics and logs for the labs

cd /root || exit 1

# Assign the first argument to a variable
lab_number=$1

# Copy the case statement and paste into run-lab-prep.sh
case "$lab_number" in
    lab1)
        lab_file="/root/advanced-observability-querying-tool-v0.9.0/lab01.yaml"
        ;;
    lab2)
        lab_file="/root/advanced-observability-querying-tool-v0.9.0/lab02.yaml"
        ;;
    lab3part1)
        lab_file="/root/advanced-observability-querying-tool-v0.9.0/lab03a.yaml"
        ;;
    lab3part2)
        lab_file="/root/advanced-observability-querying-tool-v0.9.0/lab03b.yaml"
        ;;
    lab3part3)
        lab_file="/root/advanced-observability-querying-tool-v0.9.0/lab03c.yaml"
        ;;
    verify)
        lab_file="verify"
        ;;
    startup)
        lab_file="startup"
        ;;
    *)
        lab_file=""  # Default case if none match
        ;;
esac
# End copy

if [[ -z "$lab_file" ]]; then
    echo "Error: Invalid lab name."
    exit 1
fi

if [ "$lab_file" = "verify" ]; then

  HOSTNAME=$(hostname)
  VERSION=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/attributes/version" -H "Metadata-Flavor: Google")
  META_REGION_STRING=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google")
  REGION=`echo "$META_REGION_STRING" | awk -F/ '{print $4}'`

  echo "ok! ($VERSION) $HOSTNAME in $REGION"

elif [ "$lab_file" = "startup" ]; then

  sudo google_metadata_script_runner startup

else

  . /root/advanced-observability-querying-tool-v0.9.0/.venv/bin/activate
  ADVOBS_DEBUG=1 python /root/advanced-observability-querying-tool-v0.9.0/main.py $lab_file > advobs-$lab_number.log 2>&1 &

  lab_pid=$!

  echo $lab_pid > advobs-$lab_number.pid

fi
