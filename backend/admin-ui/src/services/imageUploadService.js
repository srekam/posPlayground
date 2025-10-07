// Image Upload Service using Media API
import apiClient, { API_ENDPOINTS } from '../config/api';

class ImageUploadService {
  /**
   * Upload image using presigned URL flow
   * @param {File} file - The image file to upload
   * @param {string} ownerType - Type of owner (e.g., 'product', 'item')
   * @param {string} ownerId - ID of the owner
   * @returns {Promise<Object>} Upload result with asset info
   */
  async uploadImage(file, ownerType = 'product', ownerId) {
    try {
      // Step 1: Get presigned URL
      const presignResponse = await apiClient.post(API_ENDPOINTS.MEDIA.PRESIGN, {
        filename: file.name,
        mime_type: file.type,
        owner_type: ownerType,
        owner_id: ownerId,
        acl: 'public'
      });

      const { upload_url, headers, asset_id, storage_key } = presignResponse.data;

      // Step 2: Upload file directly to S3/MinIO
      const formData = new FormData();
      
      // Add headers as form fields
      Object.entries(headers).forEach(([key, value]) => {
        formData.append(key, value);
      });
      
      // Add the file
      formData.append('file', file);

      const uploadResponse = await fetch(upload_url, {
        method: 'POST',
        body: formData
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      // Step 3: Complete upload
      const completeResponse = await apiClient.post(API_ENDPOINTS.MEDIA.COMPLETE, {
        asset_id,
        storage_key
      });

      return {
        success: true,
        asset_id,
        storage_key,
        url: upload_url.split('?')[0], // Remove query params for display URL
        data: completeResponse.data
      };

    } catch (error) {
      console.error('Image upload failed:', error);
      throw new Error(`Failed to upload image: ${error.message}`);
    }
  }

  /**
   * Get image URL for display
   * @param {string} assetId - The asset ID
   * @param {string} variant - Image variant (thumb, sm, md, lg, orig)
   * @returns {string} Image URL
   */
  getImageUrl(assetId, variant = 'md') {
    // For now, return a placeholder. In production, this would construct the CDN URL
    return `https://via.placeholder.com/400x400?text=Image+${assetId}`;
  }

  /**
   * Delete an image
   * @param {string} assetId - The asset ID to delete
   */
  async deleteImage(assetId) {
    try {
      await apiClient.delete(`${API_ENDPOINTS.MEDIA.DELETE}/${assetId}`);
      return { success: true };
    } catch (error) {
      console.error('Image deletion failed:', error);
      throw new Error(`Failed to delete image: ${error.message}`);
    }
  }

  /**
   * Get images for an item
   * @param {string} itemId - The item ID
   * @returns {Promise<Array>} List of images
   */
  async getItemImages(itemId) {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.MEDIA.PRODUCT_IMAGES(itemId)}`);
      return response.data || [];
    } catch (error) {
      console.error('Failed to get item images:', error);
      return [];
    }
  }
}

export default new ImageUploadService();
