#!/usr/bin/env python3
"""
Test script for Media API functionality
"""
import asyncio
import httpx
import json
from typing import Dict, Any


class MediaAPITester:
    """Test client for Media API"""
    
    def __init__(self, base_url: str = "http://localhost:48080", token: str = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    async def test_presign_upload(self, filename: str, mime_type: str, owner_type: str, owner_id: str) -> Dict[str, Any]:
        """Test presigned upload URL generation"""
        print(f"Testing presign upload for {filename}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/media/uploads/presign",
                headers=self.headers,
                json={
                    "filename": filename,
                    "mime_type": mime_type,
                    "owner_type": owner_type,
                    "owner_id": owner_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Presign successful: {data['asset_id']}")
                return data
            else:
                print(f"✗ Presign failed: {response.status_code} - {response.text}")
                return {}
    
    async def test_complete_upload(self, asset_id: str, storage_key: str) -> Dict[str, Any]:
        """Test upload completion"""
        print(f"Testing upload completion for {asset_id}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/media/complete",
                headers=self.headers,
                json={
                    "asset_id": asset_id,
                    "storage_key": storage_key
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Upload completion successful: {data['processing_status']}")
                return data
            else:
                print(f"✗ Upload completion failed: {response.status_code} - {response.text}")
                return {}
    
    async def test_list_assets(self, owner_type: str = None, owner_id: str = None) -> list:
        """Test asset listing"""
        print("Testing asset listing...")
        
        params = {}
        if owner_type:
            params["owner_type"] = owner_type
        if owner_id:
            params["owner_id"] = owner_id
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/media",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ List assets successful: {len(data)} assets found")
                return data
            else:
                print(f"✗ List assets failed: {response.status_code} - {response.text}")
                return []
    
    async def test_get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Test getting specific asset"""
        print(f"Testing get asset {asset_id}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/media/{asset_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Get asset successful: {data['filename_original']}")
                return data
            else:
                print(f"✗ Get asset failed: {response.status_code} - {response.text}")
                return {}
    
    async def test_product_images(self, product_id: str) -> list:
        """Test product images endpoint"""
        print(f"Testing product images for {product_id}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/media/products/{product_id}/images",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Product images successful: {len(data)} images found")
                return data
            else:
                print(f"✗ Product images failed: {response.status_code} - {response.text}")
                return []
    
    async def test_reorder_images(self, product_id: str, asset_ids: list) -> bool:
        """Test reordering product images"""
        print(f"Testing reorder images for {product_id}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/media/products/{product_id}/images/order",
                headers=self.headers,
                json={"asset_ids": asset_ids}
            )
            
            if response.status_code == 200:
                print("✓ Reorder images successful")
                return True
            else:
                print(f"✗ Reorder images failed: {response.status_code} - {response.text}")
                return False
    
    async def test_set_primary_image(self, product_id: str, asset_id: str) -> bool:
        """Test setting primary image"""
        print(f"Testing set primary image for {product_id}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/media/products/{product_id}/images/primary",
                headers=self.headers,
                json={"asset_id": asset_id}
            )
            
            if response.status_code == 200:
                print("✓ Set primary image successful")
                return True
            else:
                print(f"✗ Set primary image failed: {response.status_code} - {response.text}")
                return False
    
    async def test_delete_asset(self, asset_id: str) -> bool:
        """Test deleting an asset"""
        print(f"Testing delete asset {asset_id}...")
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/v1/media/{asset_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print("✓ Delete asset successful")
                return True
            else:
                print(f"✗ Delete asset failed: {response.status_code} - {response.text}")
                return False
    
    async def run_full_test(self):
        """Run a complete test suite"""
        print("🚀 Starting Media API Test Suite")
        print("=" * 50)
        
        # Test 1: Presign upload
        presign_data = await self.test_presign_upload(
            filename="test-product.jpg",
            mime_type="image/jpeg",
            owner_type="product",
            owner_id="test_product_123"
        )
        
        if not presign_data:
            print("❌ Presign test failed, stopping tests")
            return
        
        asset_id = presign_data.get("asset_id")
        storage_key = presign_data.get("storage_key")
        
        # Test 2: Complete upload (this would fail without actual file upload)
        print("\n⚠️  Note: Complete upload test requires actual file upload to S3")
        complete_data = await self.test_complete_upload(asset_id, storage_key)
        
        # Test 3: List assets
        await self.test_list_assets()
        
        # Test 4: List assets with filters
        await self.test_list_assets(owner_type="product", owner_id="test_product_123")
        
        # Test 5: Get specific asset (will fail if upload wasn't completed)
        await self.test_get_asset(asset_id)
        
        # Test 6: Product images
        await self.test_product_images("test_product_123")
        
        # Test 7: Reorder images (will fail without actual images)
        await self.test_reorder_images("test_product_123", [asset_id])
        
        # Test 8: Set primary image
        await self.test_set_primary_image("test_product_123", asset_id)
        
        # Test 9: Delete asset
        await self.test_delete_asset(asset_id)
        
        print("\n" + "=" * 50)
        print("✅ Media API Test Suite Complete")


async def main():
    """Main test function"""
    # You can provide a token for authenticated requests
    # token = "your_jwt_token_here"
    token = None
    
    tester = MediaAPITester(token=token)
    await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())
