/**
 * Items API Service
 * Centralized service for all items-related API calls
 */

import apiClient, { API_ENDPOINTS } from '../config/api';

class ItemsService {
  /**
   * Get items list with filters
   * @param {object} filters - Filter parameters
   * @returns {Promise} API response
   */
  async getItems(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    const response = await apiClient.get(`${API_ENDPOINTS.ITEMS.LIST}?${params}`);
    return response.data;
  }

  /**
   * Get item by ID
   * @param {string} itemId - Item ID
   * @returns {Promise} API response
   */
  async getItem(itemId) {
    const response = await apiClient.get(API_ENDPOINTS.ITEMS.GET_BY_ID(itemId));
    return response.data;
  }

  /**
   * Create new item
   * @param {object} itemData - Item data
   * @returns {Promise} API response
   */
  async createItem(itemData) {
    const response = await apiClient.post(API_ENDPOINTS.ITEMS.CREATE, itemData);
    return response.data;
  }

  /**
   * Update item
   * @param {string} itemId - Item ID
   * @param {object} itemData - Updated item data
   * @returns {Promise} API response
   */
  async updateItem(itemId, itemData) {
    const response = await apiClient.put(API_ENDPOINTS.ITEMS.UPDATE(itemId), itemData);
    return response.data;
  }

  /**
   * Delete item
   * @param {string} itemId - Item ID
   * @returns {Promise} API response
   */
  async deleteItem(itemId) {
    const response = await apiClient.delete(API_ENDPOINTS.ITEMS.DELETE(itemId));
    return response.data;
  }

  /**
   * Update item status
   * @param {string} itemId - Item ID
   * @param {boolean} active - Active status
   * @returns {Promise} API response
   */
  async updateItemStatus(itemId, active) {
    const response = await apiClient.patch(
      API_ENDPOINTS.ITEMS.UPDATE_STATUS(itemId),
      { active }
    );
    return response.data;
  }

  /**
   * Bulk update item status
   * @param {Array} itemIds - Array of item IDs
   * @param {boolean} active - Active status
   * @returns {Promise} Array of API responses
   */
  async bulkUpdateItemStatus(itemIds, active) {
    const promises = itemIds.map(itemId => 
      this.updateItemStatus(itemId, active)
    );
    return Promise.all(promises);
  }
}

class InventoryService {
  /**
   * Get inventory items
   * @param {object} filters - Filter parameters
   * @returns {Promise} API response
   */
  async getInventoryItems(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.ITEMS}?${params}`);
    return response.data;
  }

  /**
   * Get inventory movements
   * @param {object} filters - Filter parameters
   * @returns {Promise} API response
   */
  async getInventoryMovements(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    const response = await apiClient.get(`${API_ENDPOINTS.INVENTORY.MOVEMENTS}?${params}`);
    return response.data;
  }

  /**
   * Create inventory movement
   * @param {object} movementData - Movement data
   * @returns {Promise} API response
   */
  async createMovement(movementData) {
    const response = await apiClient.post(API_ENDPOINTS.INVENTORY.CREATE_MOVEMENT, movementData);
    return response.data;
  }
}

class CategoriesService {
  /**
   * Get categories list
   * @returns {Promise} API response
   */
  async getCategories() {
    const response = await apiClient.get(API_ENDPOINTS.CATEGORIES.LIST);
    return response.data;
  }

  /**
   * Get category by ID
   * @param {string} categoryId - Category ID
   * @returns {Promise} API response
   */
  async getCategory(categoryId) {
    const response = await apiClient.get(API_ENDPOINTS.CATEGORIES.GET_BY_ID(categoryId));
    return response.data;
  }

  /**
   * Create category
   * @param {object} categoryData - Category data
   * @returns {Promise} API response
   */
  async createCategory(categoryData) {
    const response = await apiClient.post(API_ENDPOINTS.CATEGORIES.CREATE, categoryData);
    return response.data;
  }

  /**
   * Update category
   * @param {string} categoryId - Category ID
   * @param {object} categoryData - Updated category data
   * @returns {Promise} API response
   */
  async updateCategory(categoryId, categoryData) {
    const response = await apiClient.put(API_ENDPOINTS.CATEGORIES.UPDATE(categoryId), categoryData);
    return response.data;
  }

  /**
   * Delete category
   * @param {string} categoryId - Category ID
   * @returns {Promise} API response
   */
  async deleteCategory(categoryId) {
    const response = await apiClient.delete(API_ENDPOINTS.CATEGORIES.DELETE(categoryId));
    return response.data;
  }
}

class AccessZonesService {
  /**
   * Get access zones list
   * @returns {Promise} API response
   */
  async getAccessZones() {
    const response = await apiClient.get(API_ENDPOINTS.ACCESS_ZONES.LIST);
    return response.data;
  }

  /**
   * Get access zone by ID
   * @param {string} zoneId - Zone ID
   * @returns {Promise} API response
   */
  async getAccessZone(zoneId) {
    const response = await apiClient.get(API_ENDPOINTS.ACCESS_ZONES.GET_BY_ID(zoneId));
    return response.data;
  }

  /**
   * Create access zone
   * @param {object} zoneData - Zone data
   * @returns {Promise} API response
   */
  async createAccessZone(zoneData) {
    const response = await apiClient.post(API_ENDPOINTS.ACCESS_ZONES.CREATE, zoneData);
    return response.data;
  }

  /**
   * Update access zone
   * @param {string} zoneId - Zone ID
   * @param {object} zoneData - Updated zone data
   * @returns {Promise} API response
   */
  async updateAccessZone(zoneId, zoneData) {
    const response = await apiClient.put(API_ENDPOINTS.ACCESS_ZONES.UPDATE(zoneId), zoneData);
    return response.data;
  }

  /**
   * Delete access zone
   * @param {string} zoneId - Zone ID
   * @returns {Promise} API response
   */
  async deleteAccessZone(zoneId) {
    const response = await apiClient.delete(API_ENDPOINTS.ACCESS_ZONES.DELETE(zoneId));
    return response.data;
  }
}

class CardsService {
  /**
   * Get card by ID
   * @param {string} cardId - Card ID
   * @returns {Promise} API response
   */
  async getCard(cardId) {
    const response = await apiClient.get(API_ENDPOINTS.CARDS.GET_BY_ID(cardId));
    return response.data;
  }

  /**
   * Add entitlement to card
   * @param {string} cardId - Card ID
   * @param {object} entitlementData - Entitlement data
   * @returns {Promise} API response
   */
  async addEntitlement(cardId, entitlementData) {
    const response = await apiClient.post(
      API_ENDPOINTS.CARDS.ADD_ENTITLEMENT(cardId),
      entitlementData
    );
    return response.data;
  }

  /**
   * Add credits to card
   * @param {string} cardId - Card ID
   * @param {object} creditsData - Credits data
   * @returns {Promise} API response
   */
  async addCredits(cardId, creditsData) {
    const response = await apiClient.post(
      API_ENDPOINTS.CARDS.ADD_CREDITS(cardId),
      creditsData
    );
    return response.data;
  }
}

class MediaService {
  /**
   * Get presigned URL for upload
   * @param {object} uploadData - Upload data
   * @returns {Promise} API response
   */
  async getPresignedUrl(uploadData) {
    const response = await apiClient.post(API_ENDPOINTS.MEDIA.PRESIGN, uploadData);
    return response.data;
  }

  /**
   * Complete upload
   * @param {object} completionData - Completion data
   * @returns {Promise} API response
   */
  async completeUpload(completionData) {
    const response = await apiClient.post(API_ENDPOINTS.MEDIA.COMPLETE, completionData);
    return response.data;
  }

  /**
   * Upload file to presigned URL
   * @param {File} file - File to upload
   * @param {string} presignedUrl - Presigned URL
   * @returns {Promise} Upload response
   */
  async uploadToPresignedUrl(file, presignedUrl) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(presignedUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response;
  }
}

// Export service instances
export const itemsService = new ItemsService();
export const inventoryService = new InventoryService();
export const categoriesService = new CategoriesService();
export const accessZonesService = new AccessZonesService();
export const cardsService = new CardsService();
export const mediaService = new MediaService();

// Export service classes for testing
export {
  ItemsService,
  InventoryService,
  CategoriesService,
  AccessZonesService,
  CardsService,
  MediaService,
};
