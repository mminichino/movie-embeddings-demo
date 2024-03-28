# movie-embeddings-demo 1.0.3

## Quickstart

### 1. Download the dataset
![](https://raw.githubusercontent.com/mminichino/movie-embeddings-demo/main/doc/tmdb.png)
<br>
The dataset was generated from data obtained from TMDB as well as other public sources.
```
curl -OLs https://github.com/mminichino/movie-embeddings-demo/releases/download/1.0.3/movie-data-2023.json
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
