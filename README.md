1. Ensure you have docker installed
2. Clone the repository
3. Run sudo docker build -t somenameyouwanttouse .
4. Run sudo docker run -p 8087:8087 --name somenamecanbethesmae -d --restart unless-stopped somenameyouwanttouse
   If you want to change the port changed it to .py script, dockerfile and to this run command.