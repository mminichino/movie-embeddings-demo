#!/usr/bin/env python3

import argparse
from google_embedding import GoogleEmbedding
import couchbase.search as search
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, SearchOptions, TLSVerifyMode
from couchbase.vector_search import VectorQuery, VectorSearch


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="movies")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="data")
    options = parser.parse_args()

    auth = PasswordAuthenticator(options.user, options.password)
    opts = ClusterOptions(auth, tls_verify=TLSVerifyMode.NO_VERIFY, network="external")
    cluster = Cluster.connect(f"couchbase://{options.host}", opts)
    bucket = cluster.bucket(options.bucket)
    scope = bucket.scope(options.scope)
    collection = scope.collection(options.collection)

    question = input("What movie would you like to watch? ")

    vector = GoogleEmbedding().get_text_embeddings(question)

    search_req = search.SearchRequest.create(search.MatchAllQuery()).with_vector_search(
        VectorSearch.from_vector_query(VectorQuery('image_embedding', vector)))
    search_iter = scope.search('movie_vector', search_req, SearchOptions(limit=2))
    for row in search_iter.rows():
        print(f'row: {row}')

    print(f'Metatdata: {search_iter.metadata()}')


if __name__ == '__main__':
    main()
