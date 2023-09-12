{
  description = "purple-py";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs?ref=nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }: (utils.lib.eachSystem ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ] (system: rec {

    packages = {
      pythonEnv = nixpkgs.legacyPackages.${system}.python310.withPackages (ps: with ps; [
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
    };

  }));
}
