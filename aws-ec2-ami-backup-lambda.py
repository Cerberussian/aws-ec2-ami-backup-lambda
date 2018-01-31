# Automated AMI Backups
#
# This script will search for all instances having a tag with "Backup" or "backup"
# on it. As soon as we have the instances list, we loop through each instance
# and create an AMI of it. Also, it will look for a "Retention" tag key which
# will be used as a retention policy number in days. If there is no tag with
# that name, it will be set to default value for each AMI.
#
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function 

import boto3
import collections
import datetime
import sys
import pprint
import os

default_retention = int(os.environ['DEFAULT_RETENTION'])

ec = boto3.client('ec2')

def lambda_handler(event, context):

    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup']},
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])
    
    print "Found %d instances that need backing up" % len(instances)
    
    retention_days = dict()
    instance_name = dict()
    
    for instance in instances:
        create_time = datetime.datetime.now()
        create_fmt = create_time.strftime('%H%M%S-%Y-%m-%d')
    
        AMIid = ec.create_image(
            InstanceId=instance['InstanceId'], 
            Name="Lambda - " + instance['InstanceId'] + " from " + create_fmt, 
            Description="Lambda created AMI of instance " + instance['InstanceId'] + " from " + create_fmt, 
            NoReboot=True, 
            DryRun=False
            )
        
        for t in instance['Tags']:
            if t['Key'] == 'Retention':
                retention_days[AMIid['ImageId']]=int(t.get('Value'))
            if t['Key'] == 'Name':
                instance_name[AMIid['ImageId']] = t.get('Value')

        try:
            retention_days[AMIid['ImageId']]
        except:
            retention_days[AMIid['ImageId']] = default_retention
            print "setting default retention priod for %s" % AMIid['ImageId']

        #pprint.pprint(instance)
                
        print "Retaining image %s of instance %s for %d days" % (
            AMIid['ImageId'],
            instance['InstanceId'],
            retention_days[AMIid['ImageId']]
        )
    
    for id in retention_days:
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days[id])
        delete_fmt = delete_date.strftime('%m-%d-%Y')
        
        print "Will delete image of %s on %s" % (instance_name[id], delete_fmt)
        
        # Resources does not accept strings
        listed_id = [id]
        
        ec.create_tags(
            Resources=listed_id,
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
                {'Key': 'Name', 'Value': instance_name[id]}
            ]
        )