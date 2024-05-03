project := `basename $PWD`

# Lists available recipes
default:
  @just --list

# Update constraints
update-constraints:
    docker buildx bake \
        --load \
        --file docker-bake.hcl \
        --no-cache \
        --set *.tags={{project}}-constraints \
        app
    docker run --rm --entrypoint='' {{project}}-constraints pip freeze > requirements/constraints.txt
    docker image rm {{project}}-constraints

# Run manage.py migrate
migrate:
  docker-compose exec -T application sh -c 'python manage.py migrate'

# Run manage.py makemigrations
makemigrations:
  docker-compose exec -T application sh -c 'python manage.py makemigrations'

# Shell (backend)
shell:
  docker-compose exec application sh

# Run unit tests
# TODO: Update for however tests are run here
# test:
#   docker-compose exec -T application sh test.sh
