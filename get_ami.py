"""
author:  simon.macklin@abide-financial.com
date:  9th August 2017
version: 0.1
Description:  "cloud formation custom resource script which returns the latest ami id.
"""

from dateutil import parser
from os import environ
from json import dumps
from requests import put
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_latest_ami(owner_id, platform):
    """ returns the latest ami id as a string """
    client = boto3.client('ec2')
    response = client.describe_images(
        Filters=[{
            'Name': 'owner-id', 'Values': [owner_id],
            'Name': 'tag-key', 'Values': ['platform'],
            'Name': 'tag-value', 'Values': [platform]
        }]
    )
    if len(response['Images']) < 1:
        logger.critical('no ami found.  Check the owner id and platform type matches the tags on the image')
        raise Exception('no ami found.  Check the owner id and platform type matches the tags on the image')
    else:
        for image in sorted(response['Images'], key=lambda x: parser.parse(x['CreationDate']), reverse=True):
            return image['ImageId']


def send_response(event, response_status, response_data, reason):
    """ sends a http response to the return url inside the event dict """
    resp = dict()
    resp['Status'] = response_status
    resp['StackId'] = event['StackId']
    resp['PhysicalResourceId'] = 'FindAmiCustomResource'
    resp['RequestId'] = event['RequestId']
    resp['LogicalResourceId'] = event['LogicalResourceId']
    resp['Data'] = response_data
    resp['Reason'] = reason
    logger.info(resp)
    return put(event['ResponseURL'], dumps(resp))


def lambda_handler(event, context):
    if event['RequestType'] == 'Delete':
        send_response(event, 'SUCCESS', None)
    else:
        try:
            ami = get_latest_ami(environ['owner_id'], environ['platform'])
            data = dict()
            data['ami_id'] = ami
            send_response(event, 'SUCCESS', data, None)
        except Exception as e:
            send_response(event, 'FAILED', None, e)
