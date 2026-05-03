# Streamlit Cloud Deployment Guide

## Quick Deploy Steps

### 1. **Push to GitHub**
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. **Deploy on Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "New app"
- Select your GitHub repository and main branch
- Set main file path: `app.py`
- Click "Deploy"

### 3. **Add Secrets (if using Google Maps API)**
- Go to your app on Streamlit Cloud
- Click **Settings** → **Secrets**
- Add your API key:
```toml
GOOGLE_MAPS_API_KEY = "your_actual_api_key_here"
```

## Why Maps Wasn't Working

✗ **Problem**: Local `secrets.toml` is NOT uploaded to Streamlit Cloud
✗ **Problem**: Placeholder value `"your_google_maps_api_key_here"` was being used
✓ **Solution**: Configure secrets through Streamlit Cloud dashboard

## What Changed

### Files Updated:
1. **`app.py`** - Added secrets fallback handling
   - Tries `st.secrets` first (Streamlit Cloud)
   - Falls back to environment variable (if set)
   - Gracefully handles missing API key

2. **`requirements.txt`** - Added version pinning
   - `folium>=0.14.0`
   - `streamlit-folium>=0.15.0`
   - `pyarrow` + `protobuf` (Streamlit Cloud compatibility)

3. **`metro_data.py`** - Fixed file paths
   - Uses `pathlib.Path` for cross-platform compatibility
   - Works with Streamlit Cloud file system

4. **`.streamlit/config.toml`** - Cloud-optimized settings
   - `headless = true` (required for Cloud)
   - `enableXsrfProtection = true` (security)
   - `enableCORS = false` (Cloud requirement)

5. **`.streamlit/secrets.toml`** - Clear local-only instructions
   - This file stays local (in `.gitignore`)
   - Secrets configured via Cloud dashboard instead

## Features That Work Without Google Maps API

✓ **Metro Network Maps** - Uses Folium with free tile layers:
  - OpenStreetMap (default)
  - CartoDB Light
  - Esri Street Map
  
✓ **Route Finding** - NetworkX graph operations

✓ **Analytics & Charts** - Plotly visualizations

✓ **Passenger Data** - Historical statistics

✗ **Advanced Maps Features** (optional):
  - Street View (requires API key)
  - Distance Matrix API (requires API key)
  - Places Autocomplete (requires API key)

## Environment Variables (Alternative to Secrets)

If deploying outside Streamlit Cloud, set environment variable:
```bash
export GOOGLE_MAPS_API_KEY="your_api_key"
streamlit run app.py
```

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set local secrets
# Edit .streamlit/secrets.toml with your API key

# Run app
streamlit run app.py
```

## Troubleshooting

### Issue: "ModuleNotFoundError"
→ Check `requirements.txt` has all imports

### Issue: "Data files not found"
→ Ensure `data/` folder is in GitHub repository
→ Check file permissions are readable

### Issue: Maps still not showing
→ Check browser console for errors (F12)
→ Verify `.streamlit/config.toml` has `enableCORS = false`
→ Clear browser cache and reload

### Issue: App runs locally but crashes on Cloud
→ Check logs: Streamlit Cloud → Settings → App logs
→ Verify all data CSV files are committed to Git
→ Check Python version matches (3.11+)

## .gitignore Configuration

Ensure these are ignored (don't commit):
```
.streamlit/secrets.toml     # Local secrets only!
.venv/
venv/
__pycache__/
*.pyc
.env
```

## Performance Tips

1. Use `@st.cache_data` for expensive operations
2. Lazy-load large DataFrames
3. Limit re-runs with session state
4. Use Streamlit Cloud's auto-reload feature

## Next Steps

1. ✓ Update code to use `st.secrets` fallback
2. ✓ Pin package versions in `requirements.txt`
3. ✓ Push to GitHub
4. → Deploy on Streamlit Cloud
5. → Add secrets via Cloud dashboard
6. → Test the live app

---

**Status**: Ready for Streamlit Cloud deployment! 🚀
