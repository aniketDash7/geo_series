import pystac_client
import planetary_computer
import pandas as pd
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import stackstac
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

class GeospatialProcessor:
    def __init__(self):
        self.catalog = pystac_client.Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            ignore_conformance=True,
        )

    def _array_to_base64(self, arr, cmap=None):
        """Converts a numpy array to a base64 encoded PNG."""
        plt.figure(figsize=(4, 4))
        if cmap:
            plt.imshow(arr, cmap=cmap)
            plt.colorbar()
        else:
            # Assume RGB (3, H, W) -> (H, W, 3)
            # Normalize to 0-1 for plotting if needed
            arr = np.clip(arr, 0, 3000) / 3000
            plt.imshow(np.transpose(arr, (1, 2, 0)))
        
        plt.axis('off')
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def get_ndvi_data(self, lat, lon, start_date=None, end_date=None):
        """
        Fetches Sentinel-2 data for a point and returns time series + imagery.
        """
        buffer = 0.015 # Larger buffer for visual context
        bbox = [lon - buffer, lat - buffer, lon + buffer, lat + buffer]
        
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_obj = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)
            start_date = start_obj.strftime('%Y-%m-%d')
            
        time_range = f"{start_date}/{end_date}"

        search = self.catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=time_range,
            query={"eo:cloud_cover": {"lt": 10}} 
        )
        
        items = search.item_collection()
        if not items:
            return None

        signed_items = [planetary_computer.sign(item) for item in items]

        # Fetch bands for NDVI (B08, B04) and RGB (B04, B03, B02)
        ds = stackstac.stack(
            signed_items,
            assets=["B08", "B04", "B03", "B02"],
            bounds_latlon=bbox,
            epsg=4326,
            resolution=0.0001
        ).compute()

        # 1. Time Series Calculation
        red = ds.sel(band="B04").astype("float32")
        nir = ds.sel(band="B08").astype("float32")
        ndvi = (nir - red) / (nir + red)
        
        # Spatial mean for time series
        ndvi_mean = ndvi.mean(dim=["x", "y"])
        timeseries = []
        for time, value in zip(ndvi_mean.time.values, ndvi_mean.values):
            if np.isnan(value): continue
            timeseries.append({
                "date": pd.to_datetime(time).strftime("%Y-%m-%d"),
                "ndvi": float(round(value, 4))
            })
        timeseries.sort(key=lambda x: x["date"])

        # 2. Timelapse Generation (RGB & Mask for each time slice)
        frames = []
        
        if len(ds.time) > 0:
            # For efficiency in a mini-app, we might want to sample or limit frames
            # but let's try the full sequence if it's cloud filtered anyway.
            for i in range(len(ds.time)):
                slice_ds = ds.isel(time=i)
                slice_ndvi = ndvi.isel(time=i).values
                
                # RGB Array
                rgb_arr = np.stack([
                    slice_ds.sel(band="B04").values,
                    slice_ds.sel(band="B03").values,
                    slice_ds.sel(band="B02").values
                ])
                
                frames.append({
                    "date": pd.to_datetime(slice_ds.time.values).strftime("%Y-%m-%d"),
                    "rgb": self._array_to_base64(rgb_arr),
                    "mask": self._array_to_base64(slice_ndvi, cmap='RdYlGn')
                })

        return {
            "timeseries": timeseries,
            "frames": frames
        }

if __name__ == "__main__":
    processor = GeospatialProcessor()
    print("Testing data fetch...")
    res = processor.get_ndvi_data(40.7812, -73.9665)
    if res:
        print(f"Time series length: {len(res['timeseries'])}")
        print(f"Frames generated: {len(res['frames'])}")
        if len(res['frames']) > 0:
            print(f"Latest Date: {res['frames'][-1]['date']}")
