#!/bin/bash

# Script to set up IAM permissions for OpenSearch access
# Run this script after updating the policy file with your actual domain ARN

echo "Setting up IAM permissions for OpenSearch access..."
echo "=================================================="

# Load environment variables from .env file
if [ -f "../.env" ]; then
    echo "📄 Loading AWS credentials from .env file..."
    export $(cat ../.env | grep -E '^AWS_' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "⚠️  .env file not found at ../.env"
fi

# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ Error: Cannot get AWS account ID. Please check your AWS credentials."
    echo ""
    echo "Make sure you have AWS CLI configured with valid credentials:"
    echo "  aws configure"
    echo "Or set environment variables:"
    echo "  export AWS_ACCESS_KEY_ID=your_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret"
    exit 1
fi

echo "✅ AWS Account ID: $ACCOUNT_ID"

# Get the current IAM user
IAM_USER=$(aws sts get-caller-identity --query Arn --output text | cut -d'/' -f2)
echo "✅ IAM User: $IAM_USER"

# Create a fresh policy file with the correct account ID
cat > opensearch-iam-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "es:ESHttpGet",
        "es:ESHttpPost",
        "es:ESHttpPut",
        "es:ESHttpDelete",
        "es:ESHttpHead"
      ],
      "Resource": "arn:aws:es:us-east-1:$ACCOUNT_ID:domain/air-openai-project/*"
    }
  ]
}
EOF

echo ""
echo "📝 Updated IAM policy:"
cat opensearch-iam-policy.json

echo ""
echo "🔧 Creating and attaching IAM policy..."

# Create the policy
POLICY_NAME="AIR-OpenSearch-Access"
POLICY_ARN="arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME"

# Check if policy already exists
if aws iam get-policy --policy-arn "$POLICY_ARN" >/dev/null 2>&1; then
    echo "⚠️  Policy already exists. Updating it..."
    aws iam create-policy-version \
        --policy-arn "$POLICY_ARN" \
        --policy-document file://opensearch-iam-policy.json \
        --set-as-default
else
    echo "📋 Creating new policy..."
    aws iam create-policy \
        --policy-name "$POLICY_NAME" \
        --policy-document file://opensearch-iam-policy.json \
        --description "Access policy for AIR OpenSearch domain"
fi

# Attach policy to user
echo "🔗 Attaching policy to user: $IAM_USER"
aws iam attach-user-policy \
    --user-name "$IAM_USER" \
    --policy-arn "$POLICY_ARN"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! IAM permissions have been set up."
    echo ""
    echo "Next steps:"
    echo "1. Wait 1-2 minutes for permissions to propagate"
    echo "2. Run the test again: python3 test_pipeline.py"
    echo ""
    echo "If you still get 403 errors, check your OpenSearch domain access policy:"
    echo "https://console.aws.amazon.com/es/home?region=us-east-1#domain:resource=air-openai-project;action=dashboard"
else
    echo ""
    echo "❌ Failed to attach policy. Please check the error above."
    echo ""
    echo "Manual steps:"
    echo "1. Go to AWS Console → IAM → Users → $IAM_USER"
    echo "2. Click 'Add permissions' → 'Attach policies directly'"
    echo "3. Create new policy with the JSON from opensearch-iam-policy.json"
fi