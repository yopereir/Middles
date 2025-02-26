# This project is the Solution to the 
## How to deploy and test:
- Deploy stack to a connected kubernetes cluster by running `./deploy.sh`.
- Run `kubectl port-forward -n $NAMESPACE svc/meme-generator-server-service 8080:8089`.
- To get meme data as AI Subscription user: `curl -X GET -H "Authorization: Bearer 2" "http://localhost:8080/memes?lat=40.73&lon=-73.93&query=food"` where Bearer token is userID.
- To check user data within Redis container you can use `redis-cli get token:2`, use `KEYS *` to get all keys.
- To check user data within Postgres container you can use `psql -h postgres -d memes -U postgres -W -c "SELECT * from users;"` with default password `password`.