{
  description = "purple-py";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: utils.lib.eachSystem ["x86_64-linux" "x86_64-darwin" "aarch64-darwin"] (system: let
    pkgs = nixpkgs.legacyPackages.${system};

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
      # propagatedBuildInputs = [];  # Add Python dependencies if any
    };

  in rec {
    packages = {
      pythonEnv = pkgs.python310.withPackages (ps: with ps; [
        black
        jupyter
        nostrSdk
        numpy
        pandas
        pip
        psycopg2
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
  });
}
