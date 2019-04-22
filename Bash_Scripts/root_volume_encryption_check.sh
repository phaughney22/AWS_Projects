#!/bin/bash
#
#
#This scripts itterates through each of the AMIs within the detected AWS account.
#For each image in the account, it checks the root volume to see if it is encrypted.
#If it is not encrypted, it checks for the region of the AMI and creates a new, encrypted copy of the AMI in the same region and with the default account key.

owner=$(aws sts get-caller-identity --query '[Account]' --output text);
echo "Running scan for images belonging to Account $owner."
for image in $(aws ec2 describe-images --owners $owner --query 'Images[*].[ImageId]' --output text);
do
  echo "Checking AMI with ID of $image.";
  echo;
  root_device=$(aws ec2 describe-images --image-ids $image --query 'Images[*].[RootDeviceName]' --output text);
  echo "Root device of image is $root_device.";
  echo;
  response=$(aws ec2 describe-images --image-ids $image --query 'Images[*].BlockDeviceMappings[?DeviceName==`'$root_device'`].[Ebs.Encrypted]' --output text);
  echo "Image is encrypted? $response.";
  echo;
  if [ -z "$response" ];
  then
    echo "Cannot obtain encryption state of root volume of AMI with ID of $image. Returned NULL value on check.";
    echo;
  elif [ "$response" == "True" ];
  then
    echo "AMI with ID of $image is already encrypted. No action will be taken.";
    echo;
  elif [ "$response" == "False" ];
  then
    echo "AMI with ID of $image is not encrypted. Will create encrypted copy, delete old volume and update any references to previous AMI ID.";
    echo;
    read -p "Are you sure? (Y to continue, any key to exit.)" -r
    echo;
    if [[ $REPLY =~ ^[Yy]$ ]];
    then
      echo "Continuing...";
      echo;
      echo "Will now located the specified AMI's region..."
      echo;
      for region in $(aws ec2 describe-regions --output text --query 'Regions[*].RegionName');
      do
        regioncheck=$(aws ec2 describe-images --region $region --image-ids $image 2>/dev/null);
        if [ -z "$regioncheck" ];
        then
          echo "No image with specified ID found in the $region region."
          echo;
        else
          regionforimage=$region;
          echo "Image found in $regionforimage region.";
          echo;
        fi
      done 2>/dev/null; wait 2>/dev/null;
      echo "Now creating an encrypted copy of AMI $image in the $regionforimage region."
      echo;
      newencryptedimage=$(aws ec2 copy-image --source-region $regionforimage --source-image-id $image --region $regionforimage --name $image"_encrypted" --encrypted --output text);
      echo "Completed creating encrypted image with AMI ID $newencryptedimage."
      echo;
      for launchconfigimagecheck in $(aws autoscaling describe-launch-configurations --query 'LaunchConfigurations[*].[ImageId]' --output text);
      do
        if [ "$launchconfigimagecheck" == "$image" ];
        then
          launchconfigname=$(aws autoscaling describe-launch-configurations --query 'LaunchConfigurations[*].[LaunchConfigurationName]' --output text);
          echo "Image of $image is found in launch configuration $launchconfigname. This image will not be deleted. Please update the launch configuration to be include the new, encrypted image with image ID of $newencryptedimage."
        else
          echo "Image ID not returned in any autoscaling launch configurations. Deregistering original AMI with ID $image and marking associated snapshot for deletion"
          echo;
          aws ec2 deregister-image --dry-run --image-id $image;
          for snapstodelete in $(aws ec2 describe-images --image-id $image --query 'Images[*].BlockDeviceMappings[*].[Ebs.SnapshotId]' --output text);
          do
            aws ec2 delete-snapshot --dry-run --snapshot-id $snapstodelete;
            echo "Completed deregistration of AMI $image and deletion of snapshot $snapstodelete."
            echo;
          done
        fi
      done
    else
      echo "Exiting program."
    fi
  fi
done
