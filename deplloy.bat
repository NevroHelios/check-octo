docker build -t nevrohelios/detect:latest .
docker push nevrohelios/detect:latest
az webapp restart --name detect-fastapi --resource-group hackathon