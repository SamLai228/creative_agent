/** API 服務層 */
import axios from 'axios';

const API_BASE_URL = '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 上傳圖片素材
 * @param {File} file - 圖片檔案
 * @returns {Promise} 上傳結果
 */
export const uploadMaterial = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/materials/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * 為素材貼標
 * @param {string} filePath - 檔案路徑
 * @param {boolean} forceUpdate - 是否強制更新
 * @returns {Promise} 標籤資訊
 */
export const tagMaterial = async (filePath, forceUpdate = false) => {
  const response = await api.post('/api/materials/tag', null, {
    params: {
      file_path: filePath,
      force_update: forceUpdate,
    },
  });
  
  return response.data;
};

/**
 * 取得所有已貼標素材
 * @returns {Promise} 素材列表
 */
export const getAllMaterials = async () => {
  try {
    const response = await api.get('/api/materials');
    // 確保返回的是陣列
    if (Array.isArray(response.data)) {
      return response.data;
    }
    // 如果返回的是物件，轉換為陣列
    if (response.data && typeof response.data === 'object') {
      return Object.values(response.data);
    }
    return [];
  } catch (error) {
    console.error('取得素材列表失敗:', error);
    // 如果是網路錯誤，提供更詳細的錯誤訊息
    if (error.response) {
      throw new Error(error.response.data?.detail || error.response.statusText || '取得素材列表失敗');
    } else if (error.request) {
      throw new Error('無法連接到伺服器，請確認後端服務是否正在運行');
    } else {
      throw error;
    }
  }
};

/**
 * 取得單一素材標籤
 * @param {string} filePath - 檔案路徑
 * @returns {Promise} 標籤資訊
 */
export const getMaterialTags = async (filePath) => {
  const response = await api.get(`/api/materials/${encodeURIComponent(filePath)}`);
  return response.data;
};

/**
 * 取得素材圖片 URL
 * @param {string} filePath - 檔案路徑
 * @returns {string} 圖片 URL
 */
export const getMaterialImageUrl = (filePath) => {
  return `${API_BASE_URL}/api/materials/image/${encodeURIComponent(filePath)}`;
};

/**
 * 搜尋素材
 * @param {Object} searchParams - 搜尋條件
 * @returns {Promise} 搜尋結果
 */
export const searchMaterials = async (searchParams) => {
  const response = await api.post('/api/materials/search', searchParams);
  return response.data;
};

/**
 * 取得統計資訊
 * @returns {Promise} 統計資訊
 */
export const getStats = async () => {
  const response = await api.get('/api/materials/stats');
  return response.data;
};

/**
 * 刪除素材（檔案和標籤）
 * @param {string} filePath - 檔案路徑
 * @returns {Promise} 刪除結果
 */
export const deleteMaterial = async (filePath) => {
  const response = await api.delete(`/api/materials/${encodeURIComponent(filePath)}`);
  return response.data;
};

/**
 * 取得所有可用的 EDM template 列表
 * @returns {Promise<Array<{name, stem, url}>>}
 */
export const getTemplates = async () => {
  const response = await api.get('/api/generation/templates');
  return response.data;
};

/**
 * 取得 template 的 region 配置
 * @param {string} templateName - Template 檔名
 * @returns {Promise} region 配置
 */
export const getTemplateRegions = async (templateName) => {
  const response = await api.get('/api/generation/template-regions', {
    params: { template_name: templateName },
  });
  return response.data;
};

/**
 * 根據 template region 配置生成文案
 * @param {Object} payload - { template_name, product_name, ... }
 * @returns {Promise<{copy: {[region_id]: string}}>}
 */
export const generateCopyForTemplate = async (payload) => {
  const response = await api.post('/api/generation/generate-copy-for-template', payload);
  return response.data;
};

/**
 * 根據需求生成 HTML EDM
 * @param {Object} requirements - { product_name, promotion_type, key_message, target_audience, tone }
 * @returns {Promise<{html: string}>}
 */
export const generateHtml = async (requirements) => {
  const response = await api.post('/api/generation/generate-html', requirements);
  return response.data;
};

/**
 * 將文字疊加到 template 並匯出（PNG 或 HTML）
 * @param {Object} payload - { template_name, regions: [...], export_format?: 'png'|'html' }
 * @returns {Promise<{url: string, filename: string}>}
 */
export const renderWithCopy = async (payload) => {
  const response = await api.post('/api/generation/render-with-copy', payload);
  return response.data;
};
