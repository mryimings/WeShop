import time
import string
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3


if __name__ == "__main__":

    AWS_ACCESS_KEY = ''
    AWS_SECRET_KEY = ''
    region = 'us-east-1'
    service = 'es'

    awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)

    host = 'search-test-qaqcu3tpmtqedbutv744acsjm4.us-east-1.es.amazonaws.com'  # For example, my-test-domain.us-east-1.es.amazonaws.com

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    document = {"text": 'hhh', "keyword": 'hhhh'}

    # print type(es)

    # es.index(index='test', doc_type="symtest", id=1, body=document)
    #
    print(es.exists(index="test", doc_type="symtest", id=1))

    # print(es.get(index='test', doc_type='symtest', id='huy'))
