sudo docker container rm packabot -f
# sudo docker rmi -f packabot
sudo docker build -t packabot .
sudo docker run -p 80:80 -itd --name packabot packabot
sudo docker logs -f packabot