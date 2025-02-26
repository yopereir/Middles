# This project is the Solution to the Meme API assignment

## Project Strcuture
1. Solution for questions 1 and 2 are present at `./images/meme-generator-server/`
2. Solution for questions 3 and 4 are present at `./stack-files/`
3. The `deploy.sh` script is created to automate deploying the complete solution.

## Answering the questions:
### Question 1
- The `server.go` file contains the server that processes the `/memes` API call.
- This API has 2 endpoints:
* `/memes/` that simly returns a 200 stating that this is the meme server.
* `/memes/?lat&lon&query` which receives 2 things- the `lat`,`lon` and `query` data from the user and the Authorization token (`bearerToken`).
- To separate Meme data from the server code, a `memes.go` file is used that defines the structure of Meme data that is generated for the user. It also contains mock data that is sent to the user based on `lat`, `lon` and `query`.
- The request fails if the Auth Token is not present with the request.
- The data received from `lat`,`lon` and `query` is sanitized before used to fetch the meme.
- A testing file `server_test.go` is used to validate the 2 endpoints.


### Question 2 and Question 4
- A PostgresDB is used to store user data. It has `userID`, `tokenBalance` and `subscriptionType` fields.
- A Redis in-memory database is used to provide quick access to user data. It stores 2 general types of keys- `token:userID` and `subscription:userID`.
- A user can have a subscriptionType of either `AI` or `default`. When `AI`, 3 tokens are deducted, otherwise 1.
- If the user does not have enough balance, an error is returned, otherwise a meme is generated.

### Question 3
- I have chosen deploying via Kubernetes as it can work with any Cloud vendor.
- A kubernetes Deployment is created for the go-server, the postgres DB, and the redis server.
- These deployments can be scaled up based on resource needs, thereby increasing server replicas. To automate this scaling up, an Horizontal Pod autoscaler (HPA) is used that increases the number of replicas as average CPU utilization goes more than 80%.
- The redis in-memory database can be used to track tokens without adding too much load to the main postgres database. Thes redis servers can be created in Availability Zones in the same region as the user, like based on Country. This will decrease latancy as well.

## How to deploy and test:
### Go server deployment:
- To only run go server locally, go to `./images/meme-generator-server` and run `go run .`. It will use `localhost:8089`.
- Run go tests at `./images/meme-generator-server` by running `go test -v`.
### Complete stack deployment:
- To deploy the complete solution, run `./deploy.sh`. This assumes that you are on a debian-based OS, have `docker` and `kubectl` installed, and are connected to a kubernetes cluster.
- Connect to the stack from localhost by running `kubectl port-forward -n $NAMESPACE svc/meme-generator-server-service 8080:8089` on a separate terminal. This will use `localhost:8080`.

### Manual tests
- To get meme data as AI Subscription user: `curl -X GET -H "Authorization: Bearer 2" "http://localhost:8080/memes?lat=40.73&lon=-73.93&query=food"` where Bearer token is userID.
- To check user data within Redis container you can use `redis-cli get token:2`, use `KEYS *` to get all keys.
- To check user data within Postgres container you can use `psql -h postgres -d memes -U postgres -W -c "SELECT * from users;"` with default password `password`.