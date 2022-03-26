# weather_tweet

## [WIP] Following procedure does not work!

### deploy
#### power shell
```
> docker-compose up --build
```

#### bash
```
$ cd deploy/dist/
$ mv PIL ../../
$ mv Pillow.libs/ ../../
$ mv Pillow-9.0.1.dist-info/ ../../
$ cd ../../
$ zip -r ../weather_tweet.zip ./*
```