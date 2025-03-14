# /bin/bash
#
# # ==============================================================
# # script to create initial .env and required host-directories  #
# # ==============================================================

# check if .env exists if yes exit
if [ -f .env ]; then
    echo ".env file already exists. Exiting."
    return
fi

# read host_directory as parameter
if [ -z "$1" ]; then
    echo "Please provide host data directory as parameter"
    return
fi

# check if host directory already exists
if [ -d "$1" ]; then
    echo "Host directory already exists. Exiting."
    return
fi

# create required directories
echo "Creating required directories"
mkdir -p $1/{db,redis,media,static,npm}

# create .env file
echo "Creating .env file"
# get UID from id command
echo "UID=$(id -u)" > .env
# get GID from id command
echo "GID=$(id -g)" >> .env
echo "" >> .env
# generate SECRET_KEY
echo "SECRET_KEY=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 50)" >> .env
echo "DB_PASSWORD=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 20)" >> .env
echo "REDIS_PASSWORD=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 20)" >> .env
echo "" >> .env
# set host directories
echo "BACKUP_VOLUME_PATH=$1/backup" >> .env
echo "DB_VOLUME_PATH=$1/db" >> .env
echo "REDIS_VOLUME_PATH=$1/redis" >> .env
echo "MEDIA_VOLUME_PATH=$1/media" >> .env
echo "STATIC_VOLUME_PATH=$1/static" >> .env
echo "NPM_VOLUME_PATH=$1/npm" >> .env
echo "" >> .env
# set ALLOWED_HOSTS
echo "ALLOWED_HOSTS=localhost" >> .env
echo "CSRF_TRUSTED_ORIGINS=http://localhost" >> .env