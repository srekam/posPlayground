import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardMedia,
  IconButton,
  Typography,
  Alert,
  LinearProgress,
  Chip,
  Grid,
} from '@mui/material';
import {
  CloudUpload,
  Delete,
  Image as ImageIcon,
  Close,
} from '@mui/icons-material';

import imageUploadService from '../services/imageUploadService';

const ImageUpload = ({ 
  images = [], 
  onImagesChange, 
  ownerType = 'product', 
  ownerId,
  maxImages = 5,
  disabled = false 
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    // Validate file count
    if (images.length + files.length > maxImages) {
      setError(`Maximum ${maxImages} images allowed`);
      return;
    }

    // Validate file types and sizes
    const validFiles = [];
    for (const file of files) {
      if (!file.type.startsWith('image/')) {
        setError(`${file.name} is not a valid image file`);
        continue;
      }
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError(`${file.name} is too large (max 10MB)`);
        continue;
      }
      validFiles.push(file);
    }

    if (validFiles.length === 0) return;

    setError('');
    setUploading(true);
    setUploadProgress(0);

    try {
      const uploadPromises = validFiles.map(async (file, index) => {
        const progress = (index / validFiles.length) * 100;
        setUploadProgress(progress);
        
        const result = await imageUploadService.uploadImage(file, ownerType, ownerId);
        return result;
      });

      const results = await Promise.all(uploadPromises);
      
      // Add new images to the list
      const newImages = results.map(result => ({
        asset_id: result.asset_id,
        url: result.url,
        filename: validFiles[results.indexOf(result)].name,
        uploaded_at: new Date().toISOString(),
        primary: false
      }));

      onImagesChange([...images, ...newImages]);
      setUploadProgress(100);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const handleDeleteImage = async (imageIndex) => {
    const imageToDelete = images[imageIndex];
    
    try {
      await imageUploadService.deleteImage(imageToDelete.asset_id);
      
      // Remove from local state
      const newImages = images.filter((_, index) => index !== imageIndex);
      
      // If we deleted the primary image, make the first remaining image primary
      if (imageToDelete.primary && newImages.length > 0) {
        newImages[0].primary = true;
      }
      
      onImagesChange(newImages);
    } catch (err) {
      setError(`Failed to delete image: ${err.message}`);
    }
  };

  const handleSetPrimary = (imageIndex) => {
    const newImages = images.map((img, index) => ({
      ...img,
      primary: index === imageIndex
    }));
    onImagesChange(newImages);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (disabled || uploading) return;
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const fakeEvent = { target: { files } };
      handleFileSelect(fakeEvent);
    }
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Upload Area */}
      {images.length < maxImages && (
        <Card
          variant="outlined"
          sx={{
            mb: 2,
            border: '2px dashed',
            borderColor: 'primary.main',
            backgroundColor: 'grey.50',
            cursor: disabled || uploading ? 'not-allowed' : 'pointer',
            opacity: disabled || uploading ? 0.6 : 1,
          }}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => !disabled && !uploading && fileInputRef.current?.click()}
        >
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {uploading ? 'Uploading...' : 'Click or drag images here'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Maximum {maxImages} images, up to 10MB each
            </Typography>
            
            {uploading && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={uploadProgress} 
                  sx={{ mb: 1 }}
                />
                <Typography variant="caption">
                  {Math.round(uploadProgress)}% complete
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        disabled={disabled || uploading}
      />

      {/* Image Gallery */}
      {images.length > 0 && (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Images ({images.length}/{maxImages})
          </Typography>
          <Grid container spacing={2}>
            {images.map((image, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card>
                  <Box sx={{ position: 'relative' }}>
                    <CardMedia
                      component="img"
                      height="200"
                      image={image.url}
                      alt={image.filename}
                      sx={{ objectFit: 'cover' }}
                    />
                    
                    {/* Primary badge */}
                    {image.primary && (
                      <Chip
                        label="Primary"
                        color="primary"
                        size="small"
                        sx={{
                          position: 'absolute',
                          top: 8,
                          left: 8,
                        }}
                      />
                    )}
                    
                    {/* Action buttons */}
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        display: 'flex',
                        gap: 1,
                      }}
                    >
                      {!image.primary && (
                        <IconButton
                          size="small"
                          onClick={() => handleSetPrimary(index)}
                          disabled={disabled}
                          sx={{ 
                            backgroundColor: 'rgba(255,255,255,0.8)',
                            '&:hover': { backgroundColor: 'rgba(255,255,255,0.9)' }
                          }}
                        >
                          <ImageIcon fontSize="small" />
                        </IconButton>
                      )}
                      
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteImage(index)}
                        disabled={disabled}
                        sx={{ 
                          backgroundColor: 'rgba(255,255,255,0.8)',
                          '&:hover': { backgroundColor: 'rgba(255,255,255,0.9)' }
                        }}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="body2" noWrap>
                      {image.filename}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default ImageUpload;
