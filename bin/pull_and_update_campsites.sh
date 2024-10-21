EXPNAME="pull-all-recgov"

instance_type="t3.small"
# C5.micro
yourpemfilepath=/Users/deaxman/Downloads/main.pem
aws cloudformation create-stack --stack-name ${EXPNAME} --template-body file:///Users/${USER}/Projects/WorkerRunningScripts/cloudformation_template.yaml --capabilities CAPABILITY_IAM --parameters ParameterKey=KeyName,ParameterValue=$(echo ${yourpemfilepath} | xargs basename | sed 's/\.pem//g') ParameterKey=UserName,ParameterValue=${USER} ParameterKey=InstanceType,ParameterValue=${instance_type} ParameterKey=ExpName,ParameterValue=${EXPNAME} ParameterKey=ECSAMI,ParameterValue="ami-0ebfd941bbafe70c6"

cluster_id=$(aws ec2 describe-instances --filters Name=tag:"aws:cloudformation:stack-name",Values=${EXPNAME} | jq -r '.["Reservations"][-1]["Instances"][0]["PublicDnsName"]')

scp -i ${yourpemfilepath} scrape_all_camp_info.py requirements_to_pull.txt ec2-user@${cluster_id}:/home/ec2-user/

ssh -i ${yourpemfilepath} -o "StrictHostKeyChecking=no" ec2-user@${cluster_id} 



screen -S pull_data

python3.9 -m venv recgov_datapull
source recgov_datapull/bin/activate
pip install -r requirements_to_pull.txt

python3.9 scrape_all_camp_info.py all_data_raw_${DATE}.jsonl


cp all_data_backup.json all_data_raw_${DATE}.jsonl


DATE=$(date +%m%d%y)
python3.9 convert_and_process_raw_data.py all_data_raw_${DATE}.jsonl /Users/deaxman/Downloads/recgov_all_converted_${DATE}.jsonl /Users/deaxman/Downloads/recgov_camp_id_maps_${DATE}.json

/Users/deaxman/Downloads/recgov_all_converted_${DATE}.jsonl 

BUCKET_NAME="campsite_finder"
REGION="us-east-1"  # Change to your AWS region



# Check if the S3 bucket exists
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Bucket does not exist. Creating bucket: $BUCKET_NAME"
    aws s3 mb "s3://$BUCKET_NAME" --region $REGION
else
    echo "Bucket $BUCKET_NAME already exists."
fi

S3_PATH="s3://$BUCKET_NAME/all_campground_info/all_data_raw_${DATE}.jsonl"
LOCAL_FILE="/Users/deaxman/Downloads/all_data_raw_${DATE}.jsonl"
aws s3 cp "$LOCAL_FILE" "$S3_PATH" --acl private --region $REGION



S3_PATH="s3://$BUCKET_NAME/all_campground_info/recgov_all_converted_${DATE}.jsonl"
LOCAL_FILE="/Users/deaxman/Downloads/recgov_all_converted_${DATE}.jsonl"
aws s3 cp "$LOCAL_FILE" "$S3_PATH" --acl private --region $REGION


S3_PATH="s3://$BUCKET_NAME/all_campground_info/recgov_camp_id_maps_${DATE}.json"
LOCAL_FILE="/Users/deaxman/Downloads/recgov_camp_id_maps_${DATE}.json"
aws s3 cp "$LOCAL_FILE" "$S3_PATH" --acl private --region $REGION





scp -i ${yourpemfilepath} ec2-user@${cluster_id}:/home/ec2-user/all_data_backup.json ~/Downloads/all_data_backup.json
wc -l ~/Downloads/all_data_backup.json



aws cloudformation delete-stack --stack-name ${EXPNAME}


