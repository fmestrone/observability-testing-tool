### RUN-ADVOBS-TOOL

# This script is automatically installed into the GCE instances of the QL environment during lab provisioning
# It runs the AdvObs Tools on the VM to generate metrics and logs for the labs

cd /root || exit 1

# Assign the first argument to a variable
lab_number=$1

# Use case to set the variable based on the parameter value
case "$lab_number" in
    lab1)
        lab_file=""
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
    value4)
        lab_file=""
        ;;
    *)
        lab_file=""  # Default case if none match
        ;;
esac

if [[ -z "$lab_file" ]]; then
    echo "Error: Invalid lab name."
    exit 1
fi

. /root/advanced-observability-querying-tool-v0.9.0/.venv/bin/activate
ADVOBS_DEBUG=1 python /root/advanced-observability-querying-tool-v0.9.0/main.py $lab_file > advobs-$lab_number.log 2>&1 &

lab_pid=$!

echo $lab_pid > advobs-$lab_number.pid
