# helper_functions.inc.sh: General helper functions

# Check pip to see if the given package is installed
# (returns 0 if installed, 2 if not installed)
check_system_pip_for () {
  local package_name="${1}"

  # Use 'pip list' to see if the requested package is already installed
  pip list --format=columns --disable-pip-version-check | \
    grep -Fe "${package_name}" >/dev/null 2>&1
  return $?
}

pip_install () {
  local packages="${1}"
  local flags="${2}"

  run_command "pip install ${flags} ${packages}"
  return $?
}

# Used whenever an environment sensitive command is being run
run_command () {
  local cmd="${1}"

  poetry run ${cmd}
  return $?
}

migrate_db() {
  # Run migrations
  run_command "alembic upgrade head"
}

seed_db() {
  run_command "python ./script/seed_roles.py"
}

create_db_extension() {
  local database_name="${1}"
  local extension_name="${2}"

  if [ -z "${database_name}"  ]; then
    local database_name="atat"
  fi

  if [ -z "${extension_name}"  ]; then
    local extension_name="uuid-ossp"
  fi

	echo "Creating ${extension_name} in ${database_name}"
  psql "${database_name}" -c "CREATE EXTENSION IF NOT EXISTS \"${extension_name}\""
}

reset_db() {
  local database_name="${1}"

  # If the DB exists, drop it
  dropdb --if-exists "${database_name}"

  # Create a fresh DB
  createdb "${database_name}"

  # create uuid extension
  create_db_extension "${database_name}"

  # Run migrations
  migrate_db

  # Seed database data
  seed_db
}

output_divider() {
  if tty -s; then
    echo "$( tput bold )$( tput smul )$( tput setaf 6 )${1}$( tput sgr 0)"
  else
    echo $1
  fi
}

warning() {
  if tty -s; then
    echo "$( tput bold )$( tput setaf 1 )${1}$( tput sgr 0)"
  else
    echo $1
  fi
}
