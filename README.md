**Plan:**
1. Create a requirements.txt file.
2. Create a Dockerfile for containerizing your FastAPI app.
3. Build and test the Docker image locally.
4. Create an Azure Container Registry (ACR) or use Docker Hub.
5. Push the Docker image.
6. Set up an Azure Web App for Containers using an App Service plan.
7. Deploy and test your app.

**Steps:**

1. **Create requirements.txt**

   In your project directory (next to app.py and test.py), create a file named requirements.txt with:

   ```txt
   fastapi
   uvicorn
   groq
   gunicorn
   ```

2. **Create Dockerfile**

   Create a Dockerfile in your project directory:

   ```dockerfile
   # filepath: /C:/Users/dasha/Desktop/New folder (4)/Dockerfile
   FROM python:3.9-slim

   # Set work directory
   WORKDIR /app

   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Expose port and run the application using gunicorn with uvicorn worker
   EXPOSE 8000
   CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app:app"]
   ```

3. **Build and test locally**

   Open your terminal in your project folder and run:

   ```bash
   docker build -t detect .
   docker run -p 3100:3100 detect
   ```

   Test by visiting http://localhost:8000/detect.

4. **Push your image to a registry**

   You can either use Docker Hub or create an ACR. For Docker Hub:

   ```bash
   docker tag detect nevrohelios/detect:latest
   docker push nevrohelios/detect:latest
   ```

5. **Create and configure Azure Web App**

   Using Azure CLI:

   ```bash
   az login
   az appservice plan create --name relay --resource-group hackathon --sku B1 --is-linux
   az webapp create --resource-group hackathon --plan relay --name detect-fastapi --deployment-container-image-name nevrohelios/detect:latest
   ```

6. **Configure settings (if needed)**

   If your app requires environment variables (e.g., GROQ_API_KEY), set them:

   ```bash
   az webapp config appsettings set --resource-group hackathon --name detect-fastapi --settings PORT=3100 GROQ_API_KEY=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
   ```

7. **Deploy and verify**

   Once deployed, browse to your app’s URL (e.g., https://my-fastapi-app.azurewebsites.net/detect) and test your endpoint.

These steps will containerize your FastAPI app and deploy it to Azure App Service for Containers.