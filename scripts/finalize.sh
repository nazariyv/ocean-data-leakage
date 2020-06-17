source scripts/catch-errors.sh

sleep 15

echo '👾 INITIALIZE DB WITH THE FOLLOWING COMAMND'
echo 'curl -X POST "http://aquarius:8050/api/v1/operator/pgsqlinit" -H  "accept: application/json"'
# for the above curl to work, you need to add thi line
#127.0.0.1 aquarius
# to the end of your /etc/hosts. You need to edit it with sudo permissions.
# For example:
# sudo vim /etc/hosts

echo '🦑 SUCCESS SETTING UP OCEAN COMPUTE-TO-DATA ENVIRONMENT'
