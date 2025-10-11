# Deployment Guide

## Deploying to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `scriptorian` repository
4. Railway will automatically detect the `railway.json` configuration
5. Set environment variables (optional):
   - `SCRIPTORIAN_DATA_PATH`: Path to scripture data (default: ./data)
   - `SCRIPTORIAN_VECTOR_DB_PATH`: Path to vector database (default: ./vector_db)
6. Deploy! Your server will be available at: `https://your-app.railway.app/sse`

## Deploying to Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your `scriptorian` repository
4. Render will automatically detect the `render.yaml` configuration
5. Click "Create Web Service"
6. Your server will be available at: `https://scriptorian.onrender.com/sse`

## Using the Hosted Server

Once deployed, update your Claude Desktop config to use the hosted version:

```json
{
  "mcpServers": {
    "scriptorian": {
      "url": "https://your-deployment-url.com/sse"
    }
  }
}
```

Replace `your-deployment-url.com` with your actual deployment URL.

## Custom Domain (scriptorian.ai)

### Railway
1. In your Railway project settings, go to "Settings" → "Domains"
2. Click "Custom Domain" and add `scriptorian.ai`
3. Update your DNS records with Railway's provided values

### Render
1. In your Render service settings, go to "Settings" → "Custom Domain"
2. Add `scriptorian.ai`
3. Update your DNS A record to point to Render's IP

## Environment Variables

- `PORT`: Port to run the server on (default: 8000)
- `SCRIPTORIAN_DATA_PATH`: Custom path to scripture data
- `SCRIPTORIAN_VECTOR_DB_PATH`: Custom path to vector database

## Pre-indexing for Production

For better first-request performance, you can pre-index the scriptures:

```bash
python scripts/index_scriptures.py
```

Then commit the `vector_db/` directory (update `.gitignore` to allow it).
