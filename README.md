# movie-embeddings-demo 1.0.6

## Prerequisites
- Python 3.8+
- Google Cloud CLI/SDK
  - [Google Cloud CLI](https://cloud.google.com/sdk/docs/quickstart)
- GCP Project with Vertex API Enabled
  - [gcloud init](https://cloud.google.com/sdk/gcloud/reference/init)
  - [Configure application default credentials](https://cloud.google.com/docs/authentication/external/set-up-adc)

## Quickstart

### 1. Download the dataset
![](https://raw.githubusercontent.com/mminichino/movie-embeddings-demo/main/doc/tmdb.png)
<br>
The dataset was generated from data obtained from TMDB as well as other public sources.
```
curl -OLs https://github.com/mminichino/movie-embeddings-demo/releases/download/1.0.6/movie-data-2023.json
```
### 2. Install the demo package
```
pip3 install git+https://github.com/mminichino/movie-embeddings-demo
```
### 3. Update PATH
```
export PATH=$(python3 -m site --user-base)/bin:$PATH
```
### 4. Create the collection and the Search index
```
data_load -u Administrator -p 'password' -h cb.host.example.com -f movie-data-2023.json
```
If you are using Capella, you will need to create the bucket in the Capella UI before you load the data. If you have a Capella API key, you can use the data load utility to create the bucket by supplying the appropriate additional arguments. See below for instructions on how to configure the Capella API credentials.
```
data_load -u Administrator -p 'password' -h cb.abcdef.cloud.couchbase.com -f movie-data-2023.json -R default -P project -D database
```

### Capella Credentials
The automation for Capella uses the v4 public API. To use the automation, create an API key in the Capella UI and save it to a file named ```default-api-key-token.txt``` in a directory named ```.capella``` in your home directory.
```
.capella
├── credentials
├── default-api-key-token.txt
├── project-api-key-token.txt
└── test-api-key-token.txt
```
Credentials file format:
```
[default]
api_host = cloudapi.cloud.couchbase.com
token_file = default-api-key-token.txt
account_email = john.doe@example.com

[project]
token_file = project-api-key-token.txt
```
