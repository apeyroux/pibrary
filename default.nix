with import <nixpkgs> {};

{}:
let
  python = import ./requirements.nix { inherit pkgs; };
in python.mkDerivation {
  name = "pibrary-1.0.0";
  src = ./.;
  buildInputs = [
    python.packages."python-amazon-simple-product-api"
    python.packages."SQLAlchemy"
    python.packages."click"
  ];
  propagatedBuildInputs = [
    python.packages."python-amazon-simple-product-api"
    python.packages."SQLAlchemy"
    python.packages."click"
  ];
}
