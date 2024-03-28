#!/usr/bin/env python3

import argparse
from moviedemo.google_embedding import GoogleEmbedding
from cbcmgr.cb_operation_s import CBOperation


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', '--user', action='store', help="User Name", default="Administrator")
    parser.add_argument('-p', '--password', action='store', help="User Password", default="password")
    parser.add_argument('-h', '--host', action='store', help="Cluster Node Name", default="localhost")
    parser.add_argument('-b', '--bucket', action='store', help="Bucket", default="movies")
    parser.add_argument('-s', '--scope', action='store', help="Scope", default="data")
    parser.add_argument('-c', '--collection', action='store', help="Collection", default="data")
    options = parser.parse_args()

    question = input("What movie would you like to watch? ")

    vector = GoogleEmbedding().get_text_embeddings(question)

    keyspace = f"{options.bucket}.{options.scope}.{options.collection}"
    op = CBOperation(options.host, options.user, options.password, ssl=True, quota=1024, create=True, replicas=0)
    op.connect(keyspace)

    results = op.vector_search('movie_vector', 'image_embedding', vector)
    for result in results:
        print(result.get('title'))


if __name__ == '__main__':
    main()
