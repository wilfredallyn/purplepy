{
  description = "purple-py";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: (utils.lib.eachSystem ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ] (system: rec {

    packages = {
      pythonEnv = nixpkgs.legacyPackages.${system}.python310.withPackages (ps: with ps; [
        black
        jupyter
        # nostr-sdk
        numpy
        pandas
        pip
        psycopg2
        sqlalchemy
      ]);

      postgres = nixpkgs.legacyPackages.${system}.postgresql;
    };

    defaultPackage = packages.pythonEnv;

    devShell = with nixpkgs.legacyPackages.${system}; mkShell {
      buildInputs = [
        packages.pythonEnv
        packages.postgres
      ];

      shellHook = ''
        if [ ! -d "/run/postgresql" ]; then
          sudo mkdir -p /run/postgresql/
          sudo chown $(whoami) /run/postgresql/
        fi
        if [ ! -d "pgsql" ]; then
          mkdir pgsql
          initdb -D pgsql --no-locale --encoding=UTF8
          createdb $(whoami)
          psql -c "CREATE ROLE postgres WITH SUPERUSER LOGIN;"
        fi
        if ! pg_ctl status -D pgsql &>/dev/null; then
          pg_ctl start -D pgsql
      fi
      '';
    };
  }));
}


# let
#   nostr-sdk = python3.pkgs.buildPythonPackage rec {
#     pname = "nostr-sdk";
#     version = "0.0.4";

#     src = python3.pkgs.fetchPypi {
#       inherit pname version;
#       sha256 = "<SHA256_HASH>"; # You'll need to provide the actual SHA256 hash of the package.
#     };

#     meta = with lib; {
#       description = "Description of nostr-sdk";
#       license = licenses.mit; # Replace with the actual license
#     };
#   };
# in
