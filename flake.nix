{
  description = "purple-py";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: utils.lib.eachSystem ["x86_64-linux" "x86_64-darwin" "aarch64-darwin"] (system: let
    pkgs = nixpkgs.legacyPackages.${system};

    # remove wheeldata after updating nixpkgs: dash-bootstrap-components, nostr-sdk
    dashBootstrapComponents = let
      dashBootstrapComponentsWheelData = {
        url = "https://files.pythonhosted.org/packages/cd/2a/cf963336e8b6745406d357e2f2b33ff1f236531fcadbe250096931855ec0/dash_bootstrap_components-1.5.0-py3-none-any.whl";
        sha256 = "b487fec1a85e3d6a8564fe04c0a9cd9e846f75ea9e563456ed3879592889c591";
      };
    in pkgs.python310Packages.buildPythonPackage rec {
      pname = "dash-bootstrap-components";
      version = "1.5.0";
      format = "wheel";
      src = pkgs.fetchurl {
        url = dashBootstrapComponentsWheelData.url;
        sha256 = dashBootstrapComponentsWheelData.sha256;
      };
      # propagatedBuildInputs = [];
    };

    nostrSdk = let
      wheelData = {
        "x86_64-linux" = {
          url = "https://files.pythonhosted.org/packages/2f/50/7c1f5188daee363c12fb7c14a3cadd229876b4cbad6bc2b55f73ce601e4c/nostr_sdk-0.0.4-cp310-cp310-manylinux_2_17_x86_64.whl";
          sha256 = "1rck27yi1kwpm32bpx64lh363kayvhkqa36lvmfazg6wa8cvw7qf";
        };
        "x86_64-darwin" = {
          url = "https://files.pythonhosted.org/packages/9d/d8/9cc5b4d6d4d404da7ccf6de6f00fa3dd5e1127f447aa746e18eb5b5907e3/nostr_sdk-0.0.4-cp310-cp310-macosx_11_0_x86_64.whl";
          sha256 = "0rjqdnwsa5ahdy2xxz8vcp2vzisw3x94safy1n7sbyj7cbchlp9j";
        };
        "aarch64-darwin" = {
          url = "https://files.pythonhosted.org/packages/e7/fe/cfaa29d10a9a325c081296dea3791db8dd61da130cf3ef692e40171121f7/nostr_sdk-0.0.4-cp310-cp310-macosx_11_0_arm64.whl";
          sha256 = "061l1829fycmj2c0d9f4i608qxxxw7v1nc8najf4vbjh1mwqjl8k";
        };
      };
      currentWheel = wheelData.${system} or (throw "Unsupported system: ${system}");
    in pkgs.python310Packages.buildPythonPackage rec {
      pname = "nostr-sdk";
      version = "0.0.4";
      format = "wheel";
      src = pkgs.fetchurl {
        url = currentWheel.url;
        sha256 = currentWheel.sha256;
      };
      # propagatedBuildInputs = [];
    };

  in rec {
    packages = {
      pythonEnv = pkgs.python310.withPackages (ps: with ps; [
        black
        dash
        dashBootstrapComponents
        jupyter
        neo4j
        nostrSdk
        numpy
        pandas
        pip
        psycopg2
        pytest
        python-dotenv
        sqlalchemy
      ]);
      postgres = pkgs.postgresql;
      neo4j = pkgs.neo4j;
    };
    
    defaultPackage = packages.pythonEnv;

    devShell = pkgs.mkShell {
      buildInputs = [
        packages.pythonEnv
        packages.postgres
        packages.neo4j
      ];
      
      shellHook = ''
        PG_RUN_DIR="$PWD/pgsql-run"
        export PGDATA="$PWD/pgsql"

        if [ ! -d "$PG_RUN_DIR" ]; then
          mkdir -p $PG_RUN_DIR
        fi

        if [ ! -d "$PGDATA" ]; then
          initdb --no-locale --encoding=UTF8
          createdb "$(whoami)"
          psql -c "CREATE ROLE postgres WITH SUPERUSER LOGIN;"
        fi

        echo "unix_socket_directories = '$PG_RUN_DIR'" > "$PGDATA/postgresql.conf"
        echo "listen_addresses = 'localhost'" >> "$PGDATA/postgresql.conf"
        echo "port = 5432" >> "$PGDATA/postgresql.conf"


        # start pgsql
        # if ! pg_ctl status -D pgsql &>/dev/null; then
        #   pg_ctl start -D pgsql
        # fi

        # Set up Neo4j
        NEO4J_CONF_DIR="$PWD/neo4j-conf"
        NEO4J_DATA_DIR="$PWD/neo4j-data"
        NEO4J_LOGS_DIR="$PWD/neo4j-logs"
        NEO4J_RUN_DIR="$PWD/neo4j-run"
        NEO4J_PLUGINS_DIR="$PWD/neo4j-plugins"
        NEO4J_LIB_DIR="$PWD/neo4j-lib"
        NEO4J_LICENSES_DIR="$PWD/neo4j-licenses"
        NEO4J_IMPORT_DIR="$PWD/neo4j-import"

        mkdir -p $NEO4J_CONF_DIR $NEO4J_DATA_DIR $NEO4J_LOGS_DIR $NEO4J_RUN_DIR $NEO4J_PLUGINS_DIR $NEO4J_LIB_DIR $NEO4J_LICENSES_DIR $NEO4J_IMPORT_DIR

        NEO4J_PATH=$(dirname $(which neo4j))

        cp $NEO4J_PATH/../share/neo4j/conf/neo4j.conf $NEO4J_CONF_DIR/
        chmod u+rw $NEO4J_CONF_DIR/neo4j.conf
        sed -i "s|#dbms.directories.data=.*|dbms.directories.data=$NEO4J_DATA_DIR|" $NEO4J_CONF_DIR/neo4j.conf
        sed -i "s|#dbms.directories.logs=.*|dbms.directories.logs=$NEO4J_LOGS_DIR|" $NEO4J_CONF_DIR/neo4j.conf
        sed -i "s|#dbms.directories.run=.*|dbms.directories.run=$NEO4J_RUN_DIR|" $NEO4J_CONF_DIR/neo4j.conf
        sed -i "s|#dbms.directories.plugins=.*|dbms.directories.plugins=$NEO4J_PLUGINS_DIR|" $NEO4J_CONF_DIR/neo4j.conf
        sed -i "s|#dbms.directories.lib=.*|dbms.directories.lib=$NEO4J_LIB_DIR|" $NEO4J_CONF_DIR/neo4j.conf
        sed -i "s|#dbms.directories.licenses=.*|dbms.directories.licenses=$NEO4J_LICENSES_DIR|" $NEO4J_CONF_DIR/neo4j.conf
        sed -i "s|^\(#\?\)dbms.directories.import=.*|dbms.directories.import=$NEO4J_IMPORT_DIR|" $NEO4J_CONF_DIR/neo4j.conf

        export NEO4J_CONF=$NEO4J_CONF_DIR
        neo4j-admin set-initial-password neo4j

        echo "To start PostgreSQL: pg_ctl start -o \"-c listen_addresses=\'\'"
        echo "To start Neo4j: neo4j start"
      '';
    };
  });
}
