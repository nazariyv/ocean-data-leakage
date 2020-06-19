source scripts/catch-errors.sh

sleep 10

echo '👾 INITIALIZE DB WITH THE FOLLOWING COMAMND'

# ! IF YOU CHANGE THE PWD IN POSTGRESQL CONFIG-MAP THIS WON'T WORK
echo 'jhfg76jkdfdf76' | curl -X POST "http://localhost:8050/api/v1/operator/pgsqlinit" -H  "accept: application/json"

echo '🦑 SUCCESS SETTING UP OCEAN COMPUTE-TO-DATA ENVIRONMENT'
