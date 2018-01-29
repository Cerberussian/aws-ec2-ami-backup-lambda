# aws-ec2-ami-backup-lambda

# Original code: https://gist.github.com/bkozora/724e01903a9ad481d21e
# @author Robert Kozora <bobby@kozora.me> (as mentioned in code)

Hello!

This python code is to be used with scheduling (cloudwatch events) to take images of all instanced with backup tag.

You decide if its hourly / daily / weekly / monthly.

Here is author's original code comment:

# This script will search for all instances having a tag with "Backup" or "backup"
# on it. As soon as we have the instances list, we loop through each instance
# and create an AMI of it. Also, it will look for a "Retention" tag key which
# will be used as a retention policy number in days. If there is no tag with
# that name, it will use a 7 days default value for each AMI.
#
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function 

I've modified the original code and cleaned it up a bit.

Compared to original:

* Removed to_tag and replaced it with retention_days list
* Moved tag iteration logic to main
* Retention is now per instance retention tag (instead of maximum retention found)
* Default retention is now a global variable
* Removed chunks of commented code to make it cleaner
* Images now got name tag of instances they are images of (in addition to deletion date)


The work on lambda to actually remove the images according to DeleteOn tag 
is work in progress and based on Robert Kozora's code too.
