# Docker

## Build

change to root folder, and exec:

```
docker build -t umem -f docker/Dockerfile .
```

run docker:
```
docker run -d -v ~/umem/db:/app/db -p 8000:8000 --name umem umem:latest
```