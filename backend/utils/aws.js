import AWS from 'aws-sdk';
import fs from 'fs';
import path from 'path';

// Configure AWS SDK
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION || 'us-east-1',
});

const s3 = new AWS.S3();

/**
 * Upload a file to AWS S3
 * @param {string} filePath - Local file path
 * @param {string} filename - Name to save in S3
 * @returns {Promise<string>} S3 URL
 */
export async function uploadToS3(filePath, filename) {
  const fileContent = fs.readFileSync(filePath);
  
  const params = {
    Bucket: process.env.AWS_S3_BUCKET,
    Key: `uploads/${filename}`,
    Body: fileContent,
    ContentType: 'application/pdf',
    ACL: 'public-read', // Adjust based on your security needs
  };

  try {
    const data = await s3.upload(params).promise();
    
    // Delete local file after successful upload
    fs.unlinkSync(filePath);
    
    return data.Location;
  } catch (error) {
    console.error('Error uploading to S3:', error);
    throw error;
  }
}

/**
 * Delete a file from AWS S3
 * @param {string} fileKey - S3 file key
 */
export async function deleteFromS3(fileKey) {
  const params = {
    Bucket: process.env.AWS_S3_BUCKET,
    Key: fileKey,
  };

  try {
    await s3.deleteObject(params).promise();
  } catch (error) {
    console.error('Error deleting from S3:', error);
    throw error;
  }
}

/**
 * Generate a presigned URL for temporary access
 * @param {string} fileKey - S3 file key
 * @param {number} expiresIn - Expiration time in seconds (default: 3600)
 * @returns {string} Presigned URL
 */
export function getPresignedUrl(fileKey, expiresIn = 3600) {
  const params = {
    Bucket: process.env.AWS_S3_BUCKET,
    Key: fileKey,
    Expires: expiresIn,
  };

  return s3.getSignedUrl('getObject', params);
}

export default {
  uploadToS3,
  deleteFromS3,
  getPresignedUrl,
};
